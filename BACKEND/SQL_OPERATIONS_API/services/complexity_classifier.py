import networkx as nx
from Exceptions.custom_exception import CustomException
from models.db_schema_model import JSONModel

class Complexity_Classifier:
    def __init__(self, db_schema: JSONModel, user_ques: str):
        self.db_schema = db_schema
        self.user_ques = user_ques.lower()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        try:
            graph = nx.Graph()
            for table in self.db_schema.tables:
                graph.add_node(table.name)
            
            for relationship in self.db_schema.relationships:
                graph.add_edge(relationship.from_table, relationship.to_table)
            return graph
        except Exception as e:
            raise CustomException(
                message={"error": str(e)})
    
    def _get_complexity_level(self):
        table_hits = []
        for table in self.db_schema.tables:
            if table.name.lower() in self.user_ques:
                table_hits.append(table.name)
            elif (table.description and 
                  any(word in self.user_ques for word in table.description.lower().split())):
                table_hits.append(table.name)
        
        join_distance = 0
        if len(table_hits) > 1:
            try:
                distances = []
                for i in range(len(table_hits)):
                    for j in range(i+1, len(table_hits)):
                        dist = nx.shortest_path_length(
                            self.graph, table_hits[i], table_hits[j])
                        distances.append(dist)
                join_distance = max(distances) if distances else 0
            except Exception as e:
                join_distance = 5

        if join_distance == 0:
            return "EASY"
        elif 1 <= join_distance <= 2:
            return "MEDIUM"
        elif 3 <= join_distance <= 4:
            return "HARD"
        else:
            return "VERY HARD"
            
    def __call__(self) -> str:
        label = self._get_complexity_level()
        return label
        
                        


