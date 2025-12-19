from datetime import datetime
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)

class MockCursor:
    def __init__(self, data):
        self.data = data
    
    def sort(self, key, direction=1):
        # Handle simple sorting
        # direction: 1 for ascending, -1 for descending
        reverse = direction == -1
        
        # Helper to get value for sorting, handling missing keys
        def get_sort_key(item):
            # Special handling for tuple keys if passed from pymongo style sort
            if isinstance(key, list):
                # Just sort by the first key for simplicity in mock
                k = key[0][0]
                return item.get(k, "")
            return item.get(key, "")

        # If key is a list of tuples (pymongo style), extract the first one
        if isinstance(key, list):
            primary_key, primary_direction = key[0]
            reverse = primary_direction == -1
            sort_key = primary_key
        else:
            sort_key = key

        self.data.sort(key=lambda x: str(x.get(sort_key, "")), reverse=reverse)
        return self
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.data = []

    def insert_one(self, document):
        if "_id" not in document:
            document["_id"] = ObjectId()
        self.data.append(document)
        return type('obj', (object,), {'inserted_id': document["_id"]})

    def _matches(self, doc, query):
        for k, v in query.items():
            doc_val = doc.get(k)
            
            if isinstance(v, dict):
                for op, op_val in v.items():
                    if op == "$ne":
                        if doc_val == op_val: return False
                    elif op == "$gte":
                        if doc_val is None or doc_val < op_val: return False
                    elif op == "$lte":
                        if doc_val is None or doc_val > op_val: return False
                    elif op == "$gt":
                        if doc_val is None or doc_val <= op_val: return False
                    elif op == "$lt":
                        if doc_val is None or doc_val >= op_val: return False
            else:
                if doc_val != v: return False
        return True

    def find(self, query=None):
        if query is None: query = {}
        results = [doc for doc in self.data if self._matches(doc, query)]
        return MockCursor(results)

    def find_one(self, query=None):
        results = self.find(query).data
        return results[0] if results else None

    def update_one(self, query, update, upsert=False):
        doc = self.find_one(query)
        if doc:
            if "$set" in update:
                doc.update(update["$set"])
            return type('obj', (object,), {'modified_count': 1})
        elif upsert:
            new_doc = query.copy()
            if "$set" in update:
                new_doc.update(update["$set"])
            if "_id" not in new_doc:
                new_doc["_id"] = ObjectId()
            self.data.append(new_doc)
            return type('obj', (object,), {'modified_count': 1})
        return type('obj', (object,), {'modified_count': 0})

    def count_documents(self, query):
        return len(self.find(query).data)

    def create_index(self, keys, **kwargs):
        pass

class MockDatabase:
    def __init__(self):
        self.collections = {}
        logger.warning("Initialized Mock Database (In-Memory)")

    def __getattr__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

    def dump(self):
        return {name: col.data for name, col in self.collections.items()}

