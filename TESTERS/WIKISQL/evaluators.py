import json
import requests
import sqlite3
import os
import time
import datetime
import re
from typing import Dict

# Logs
curr = str(datetime.datetime.now()).replace(".", "_").replace(":", "-")
f = open(f"{str(curr)}_log.log", "x", encoding="utf-8", errors="replace")
def log(*args) -> None:
    global f
    print(*args, file=f, flush=True)

# --- Configuration ---
API_URL = "http://127.0.0.1:8001/text-to-sql?testing=true"
WIKISQL_DIR = "./wikisql"
DATA_PATH = os.path.join(WIKISQL_DIR, "dev.jsonl")
TABLES_PATH = os.path.join(WIKISQL_DIR, "dev.tables.jsonl")
TEST_DB_FILENAME = "wikisql_test.db"
TEST_DB_PATH = os.path.abspath(TEST_DB_FILENAME)

def load_wikisql_tables(path: str) -> Dict[str, Dict]:
    tables = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            t = json.loads(line)
            tables[t['id']] = t
    return tables

def map_table_to_schema(table_meta: Dict) -> Dict:
    table_id_clean = table_meta['id'].replace("-", "_")
    table_name = f"table_{table_id_clean}"
    columns = [{
        "name": col.strip(),
        "type": ("VARCHAR" if table_meta['types'][i] == 'text' else "FLOAT"),
        "size": 255 if table_meta['types'][i] == 'text' else None,
        "description": f"Column for {col.strip()}"}
               for i, col in enumerate(table_meta['header'])]
    return {"tables": [
        {"name": table_name, "columns": columns, "description": f"WikiSQL table ID: {table_meta['id']}"}]}

def decompose_generated_sql(gen_sql: str, schema: Dict) -> Dict:
    res = {"sel": -1, "agg": 0, "conds": []}
    if not gen_sql:
        return res

    sql_clean = gen_sql.replace('"', '').replace('`', '')
    sql_lower = sql_clean.lower()

    cols = [c['name'].lower() for c in schema['tables'][0]['columns']]

    def has_column_reference(text: str, col_name: str) -> bool:
        """
        Match a raw column name in SQL-ish text without relying on \\b boundaries.
        This handles punctuation in headers (e.g., "No.", "School/Club Team").
        """
        col = re.escape(col_name)

        return re.search(rf'(?<![a-z0-9_]){col}(?![a-z0-9_])', text, re.IGNORECASE) is not None

    agg_ops = ['', 'max', 'min', 'count', 'sum', 'avg']

    cond_ops = [('!=', 3), ('>=', 1), ('<=', 2), ('>', 1), ('<', 2), ('like', 0), ('=', 0)]

    try:
        from_parts = re.split(r'\bfrom\b', sql_lower, flags=re.IGNORECASE)
        if len(from_parts) < 2:
            return res
        select_part = re.sub(r'^\s*select\s+', '', from_parts[0], flags=re.IGNORECASE).strip()

        # --- Aggregation ---
        for i, agg in enumerate(agg_ops):
            if agg and re.search(rf'\b{agg}\b', select_part, re.IGNORECASE):
                print("Matched", agg)
                res["agg"] = i
                break

        # --- Selected column ---
        sorted_col_indices = sorted(range(len(cols)), key=lambda i: len(cols[i]), reverse=True)
        for i in sorted_col_indices:
            if has_column_reference(select_part, cols[i]):
                res["sel"] = i
                break

        if res["sel"] == -1:
            return res

        # --- WHERE conditions ---
        where_parts = re.split(r'\bwhere\b', sql_lower, flags=re.IGNORECASE)
        if len(where_parts) < 2:
            return res

        where_part = where_parts[1].strip()

        conditions = re.split(r'\s+and\s+', where_part, flags=re.IGNORECASE)

        for cond in conditions:
            cond = cond.strip()
            found_col_idx = -1

            for i in sorted_col_indices:
                if has_column_reference(cond, cols[i]):
                    found_col_idx = i
                    break

            if found_col_idx == -1:
                continue

            # --- Operator ---
            found_op = 0
            for op_str, op_idx in cond_ops:
                if op_str in cond:
                    found_op = op_idx
                    break

            # --- Value extraction ---
            val_match = re.search(r"'(.*?)'", cond)
            if val_match:
                val = val_match.group(1)
            else:
                op_str_used = next((op for op, _ in cond_ops if op in cond), '=')
                after_op = cond.split(op_str_used, 1)[-1].strip().rstrip(';').strip()
                val = after_op if after_op else cond.split()[-1].strip(';')

            res["conds"].append([found_col_idx, found_op, val])

    except Exception as e:
        log(f"Decomposition Error: {e}")

    return res

def setup_test_database(questions, tables_meta):
    log(f"--- Phase 1: Setup DB ---")
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    conn = sqlite3.connect(TEST_DB_PATH)
    u_ids = list(set([q['table_id'] for q in questions]))
    for tid in u_ids:
        meta = tables_meta[tid]
        schema = map_table_to_schema(meta)
        t_name = schema['tables'][0]['name']
        col_defs = ", ".join([f'"{c["name"]}" {c["type"]}' for c in schema['tables'][0]['columns']])
        conn.execute(f'CREATE TABLE "{t_name}" ({col_defs})')
        conn.executemany(
            f'INSERT INTO "{t_name}" VALUES ({", ".join(["?" for _ in meta["header"]])})',
            meta['rows']
        )
        log(f"{schema['tables'][0]['name']} created successfully.")
    conn.commit()
    conn.close()

def execute_local(query: str):
    try:
        conn = sqlite3.connect(TEST_DB_PATH)
        res = conn.execute(query).fetchall()
        conn.close()
        return res, None
    except Exception as e:
        log(f"execute_local: {str(e)}")
        return None, str(e)

def evaluate_wikisql(limit: int = 20):
    tables_meta = load_wikisql_tables(TABLES_PATH)
    questions = []
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            questions.append(json.loads(line))
            if len(questions) >= limit:
                break

    setup_test_database(questions, tables_meta)

    log(f"--- Phase 2: Evaluation ---")
    stats = {
        "total": 0,
        "comp_match": 0,
        "exec_match": 0,
        "total_time": 0.0,
        "accuracy_percentage": 0.0,
        "results": []
    }

    for entry in questions:
        print(entry)
        table_id = entry['table_id']
        question = entry['question']
        gt_json = entry['sql']

        schema = map_table_to_schema(tables_meta[table_id])

        start = time.time()
        gen_sql, duration = None, 0
        try:
            r = requests.post(
                API_URL,
                json={
                    "connection_url": f"sqlite:///{TEST_DB_PATH}",
                    "er_diagram_json": schema,
                    "text": question
                },
                timeout=60
            )
            duration = time.time() - start
            if r.status_code == 200:
                gen_sql = r.json().get("sql")
            else:
                log(r.status_code, r.json())
        except Exception as e:
            log(f"evaluate_wikisql - call api: {str(e)}")
            duration = time.time() - start

        # --- Component Match ---
        comp_match = False
        if gen_sql:
            decomposed = decompose_generated_sql(gen_sql, schema)
            log("Comp match:", gt_json, decomposed, gen_sql)
            if decomposed['sel'] == gt_json['sel'] and decomposed['agg'] == gt_json['agg']:
                gen_cond_set = set((c[0], c[1], str(c[2]).lower().strip()) for c in decomposed['conds'])
                gt_cond_set  = set((c[0], c[1], str(c[2]).lower().strip()) for c in gt_json['conds'])
                if gen_cond_set == gt_cond_set:
                    comp_match = True
                    stats["comp_match"] += 1

        stats["total_time"] += duration
        stats["total"] += 1
        log(f"[{stats['total']}] Logic: {comp_match} | {round(duration, 1)}s")

        stats["results"].append({
            "id": stats["total"],
            "question": question,
            "logic_match": comp_match,
            "gen_sql": gen_sql
        })
        time.sleep(10)

    stats["accuracy_percentage"] = round(stats['comp_match'] / stats['total'] * 100, 2)

    with open("wikisql_thesis_report.json", "w", encoding="utf-8") as out:
        json.dump(stats, out, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Total dev questions count = 8421
    evaluate_wikisql(limit=8421)
