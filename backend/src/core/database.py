import os
from pymongo import MongoClient
from typing import Any, Dict, List
from bson.objectid import ObjectId

class Database:
    def __init__(self, db_name: str = "mydatabase"):
        # ATENÇÃO: Alterado de "mongodb://localhost:27017/" para "mongodb://mongodb:27017/"
        # 'mongodb' é o nome do serviço MongoDB no docker-compose.yml
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")

        self.client = MongoClient(MONGO_URI) 
        self.db = self.client[db_name]

    def insert_one(self, collection_name: str, data: Dict[str, Any]):
        return self.db[collection_name].insert_one(data)

    def insert_many(self, collection_name: str, data_list: List[Dict[str, Any]]):
        return self.db[collection_name].insert_many(data_list)

    def find_one(self, collection_name: str, query: Dict[str, Any]):
        return self.db[collection_name].find_one(query)

    def find(self, collection_name: str, query: Dict[str, Any] = {}, projection: Dict[str, Any] = None):
        """
        Busca documentos com base em uma consulta e projeção.
        """
        return list(self.db[collection_name].find(query, projection))

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]):
        return self.db[collection_name].update_one(query, {"$set": update})

    def delete_one(self, collection_name: str, query: Dict[str, Any]):
        return self.db[collection_name].delete_one(query)

    def delete_many(self, collection_name: str, query: Dict[str, Any]):
        return self.db[collection_name].delete_many(query)

    def count_documents(self, collection_name: str, query: Dict[str, Any] = {}):
        return self.db[collection_name].count_documents(query)

    def close(self):
        self.client.close()

    def get_object_id(self, id_string: str) -> ObjectId:
        """Converte uma string de ID em um ObjectId do MongoDB."""
        return ObjectId(id_string)
    
    def find_with_pagination(self, collection_name: str, query: Dict[str, Any] = {}, skip: int = 0, limit: int = 20, sort_by: List = None):
        """
        Busca documentos com opções de paginação e ordenação.
        """
        cursor = self.db[collection_name].find(query)
        if sort_by:
            cursor = cursor.sort(sort_by)
        
        return cursor.skip(skip).limit(limit)