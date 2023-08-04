import os.path
import json

from pydantic import BaseModel
from fastapi import FastAPI

from vlite import VLite

data_loc = "/code/data"

app = FastAPI()
store = {}

class Document(BaseModel):
    code: str
    text: str

class Query(BaseModel):
    code: str
    query: str

def locate_paper(paper_id):
    if paper_id in store: # In memory
        print(f"{paper_id}: In memory")
        return {'exists': True}
    elif os.path.isfile(f"{data_loc}/{paper_id}.npz"): # On disk, bring into memory
        print(f"{paper_id}: In disk")
        embeddings = VLite(f"{data_loc}/{paper_id}.npz")
        store[paper_id] = embeddings
        return {'exists': True}
    else:
        print(f"{paper_id}: No record")
        return {'exists': False}

@app.get("/papers/{paper_id}")
def paper_status(paper_id: str):
    return locate_paper(paper_id)

def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file: {e}")
    else:
        print(f"File '{file_path}' does not exist.")

@app.post("/embed")
def embed_doc(payload: Document):
    code = payload.code
    text = payload.text
    file_path = f"{data_loc}/{code}.npz"
    delete_file_if_exists(file_path)
    embeddings = VLite(file_path)
    embeddings.memorize(text)
    store[code] = embeddings
    return {"status": "success"}

@app.post("/papers")
def query(payload: Query):
    code = payload.code
    query = payload.query

    response = locate_paper(code)
    if not response['exists']:
        return {'status': 'error', 'message': 'paper not stored'}
    
    embeddings = store[code]
    docs, scores = embeddings.remember(query)
    return {"status": 'success', 'data': json.dumps(docs)}

@app.post("/shutdown")
def save_all():
    for code, embeddings in store:
        filepath = f"{data_loc}/{code}.npz"
        if not os.path.exists(filepath):
            embeddings.save()