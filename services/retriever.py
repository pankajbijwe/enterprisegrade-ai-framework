# retriever.py - Retrieval logic / vectorstore adapter 
# services/retriever.py
from typing import List, Dict
from storage.vectorstore import VectorStore

class Retriever:
    def __init__(self, vectorstore: VectorStore):
        self.vs = vectorstore

    def retrieve_by_embedding(self, embedding, top_k=5) -> List[Dict]:
        return self.vs.query(embedding, top_k=top_k)