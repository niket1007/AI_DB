import json
import requests
import os
import time
import sqlglot
from sqlglot import exp
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8001/text-to-sql" 
SPIDER_PATH = "./spider_data"
DB_DIR = os.path.abspath(f"{SPIDER_PATH}/database")

class SpiderEvaluator:
    def __init__(self):
        self.stats = {
            "total": 0,
            "column_match_count": 0,
            "join_match_count": 0,
            "where_match_count": 0,
            "exec_match_count": 0,
            "full_logic_match_count": 0
        }
        self.results_log = []

    def _local_executor(self, db_url, query):
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text(query))
                return [tuple(row) for row in result]
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _get_schema_dict(self, db_meta):
        tables = []
        for i, name in enumerate(db_meta['table_names_original']):
            cols = []
            for j, (t_idx, c_name) in enumerate(db_meta['column_names_original']):
                if t_idx == i:
                    raw_type = db_meta['column_types'][j].upper()
                    cols.append({
                        "name": c_name,
                        "type": "VARCHAR" if "TEXT" in raw_type else "INTEGER",
                        "description": f"Field {c_name}",
                        "primary_key": (j in db_meta['primary_keys'])
                    })
            tables.append({"name": name, "columns": cols, "description": f"Table {name}"})
        
        rels = []
        for fk in db_meta['foreign_keys']:
            c_info = db_meta['column_names_original'][fk[0]]
            p_info = db_meta['column_names_original'][fk[1]]
            rels.append({
                "from_table": db_meta['table_names_original'][c_info[0]],
                "from_column": c_info[1],
                "to_table": db_meta['table_names_original'][p_info[0]],
                "to_column": p_info[1]
            })
        return {"tables": tables, "relationships": rels}

    def _normalize_operators(self, expression):
        """Standardizes LIKE/ILIKE to EQ (=) for consistent component matching."""
        if not expression:
            return expression
        if isinstance(expression, (exp.Like, exp.ILike)):
            return exp.EQ(this=expression.this, expression=expression.expression)
        for arg_key, arg_val in expression.args.items():
            if isinstance(arg_val, list):
                expression.set(arg_key, [self._normalize_operators(v) for v in arg_val])
            elif isinstance(arg_val, exp.Expression):
                expression.set(arg_key, self._normalize_operators(arg_val))
        return expression

    def _analyze_components(self, gen_sql, gold_sql):
        def parse(s):
            try:
                p = sqlglot.parse_one(s.lower().replace('"', ''))
                # Extract Columns (normalized to remove table aliases)
                cols = {c.sql().split('.')[-1] for c in p.find_all(exp.Column)}
                # Extract Joins
                joins = {j.sql() for j in p.find_all(exp.Join)}
                # Extract and Normalize Where clause (LIKE -> =)
                where_node = p.find(exp.Where)
                where_sql = self._normalize_operators(where_node).sql() if where_node else ""
                return {"cols": cols, "joins": joins, "where": where_sql}
            except: return None

        g, s = parse(gen_sql), parse(gold_sql)
        if not g or not s:
            return {"col": False, "join": False, "where": False}
        
        return {
            "col": g["cols"] == s["cols"],
            "join": g["joins"] == s["joins"],
            "where": g["where"] == s["where"]
        }

    def run(self, limit=10):
        with open(f"{SPIDER_PATH}/dev.json", 'r') as f: dev_set = json.load(f)
        with open(f"{SPIDER_PATH}/tables.json", 'r') as f: 
            table_map = {t['db_id']: t for t in json.load(f)}

        start_time = time.time()
        for i, entry in enumerate(dev_set[:limit]):
            db_id = entry['db_id']
            db_url = f"sqlite:///{DB_DIR}/{db_id}/{db_id}.sqlite"
            schema = self._get_schema_dict(table_map[db_id])
            print(f"Item {i+1} | DB: {db_id}")

            try:
                response = requests.post(API_URL, json={
                    "connection_url": db_url,
                    "text": entry['question'],
                    "er_diagram_json": schema
                }).json()
                
                gen_sql = response.get("sql", "")
                logic_res = self._analyze_components(gen_sql, entry['query'])
                
                gold_res = self._local_executor(db_url, entry['query'])
                gen_res = response.get("data", [])
                if isinstance(gen_res, list) and len(gen_res) > 0 and isinstance(gen_res[0], dict):
                    gen_res = [tuple(d.values()) for d in gen_res]

                is_exec_match = (set(gen_res) == set(gold_res)) if isinstance(gold_res, list) else False

                # Update Stats
                self.stats["total"] += 1
                if logic_res["col"]: self.stats["column_match_count"] += 1
                if logic_res["join"]: self.stats["join_match_count"] += 1
                if logic_res["where"]: self.stats["where_match_count"] += 1
                if is_exec_match: self.stats["exec_match_count"] += 1
                
                full_logic = all(logic_res.values())
                if full_logic: self.stats["full_logic_match_count"] += 1

                self.results_log.append({
                    "id": i + 1,
                    "question": entry['question'],
                    "column_match": logic_res["col"],
                    "join_match": logic_res["join"],
                    "where_match": logic_res["where"],
                    "exec_match": is_exec_match,
                    "component_analysis": {
                        "matched": [k for k, v in logic_res.items() if v],
                        "not_matched": [k for k, v in logic_res.items() if not v]
                    },
                    "gen_sql": gen_sql,
                    "gold_sql": entry['query']
                })
                print(f"Result: Exec Match: {is_exec_match} | Logic Match: {full_logic}")
            except Exception as e:
                print(f"Failed query {i+1}: {e}")

        final_report = {
            "total": self.stats["total"],
            "column_match": self.stats["column_match_count"],
            "join_match": self.stats["join_match_count"],
            "where_match": self.stats["where_match_count"],
            "exec_match": self.stats["exec_match_count"],
            "full_logic_match": self.stats["full_logic_match_count"],
            "total_time": time.time() - start_time,
            "exec_accuracy_percentage": (self.stats["exec_match_count"] / self.stats["total"]) * 100,
            "logic_match_accuracy_percentage": (self.stats["full_logic_match_count"] / self.stats["total"]) * 100,
            "results": self.results_log
        }

        with open("full_spider_report.json", 'w') as f:
            json.dump(final_report, f, indent=2)
        print("Comprehensive report saved: full_spider_report.json")

if __name__ == "__main__":
    evaluator = SpiderEvaluator()
    # Dev Size: 1034
    evaluator.run(limit=1034)