from fastapi import FastAPI
from db.database import Database, Repository
from db.utils.embeddings import generate_embeddings
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from typing import List
from llm.llm import LLM
from llm.prompts import simple
import hashlib


class Query(BaseModel):
    query: str

app = FastAPI()
connection = Database(
    user=os.environ.get("POSTGRES_USER", "postgres"),
    password=os.environ.get("POSTGRES_PASSWORD", "password"),
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=os.environ.get("POSTGRES_PORT", 5432),
    database=os.environ.get("POSTGRES_DB", "postgres")
)

llm = LLM("gpt4")

@app.post("/insert_content/", status_code=201)
async def insert_content(repository: Repository):

    documentation = connection.extract_github_documents(repository)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=30,
    )

    item_state = [
        connection.insert_item(
            item_id=item["base_64"],
            name=item["filename"],
        )
        for item in documentation
    ]

    documentation = [
        {
            "filename": item["filename"],
            "base_64": item["base_64"],
            "content": text_splitter.split_text(item["content"])
        }
        for item in documentation
    ]

    [
        connection.insert_contents(
            content_id=hashlib.sha256(chunk.encode()).hexdigest(),
            item_id=item["base_64"],
            content=chunk,
            embedding=generate_embeddings(chunk)
        )
        for item, state in zip(documentation,item_state)
        for chunk in item["content"]
        if state == "updated" or state == "inserted"
    ]

    return {"message": "Contents of " + repository.name + " inserted/updated successfully"}

@app.get("/search_content/")
async def search_content(query: Query):
    query_embedding = generate_embeddings(query.query)
    context = connection.similarity_search(query_embedding)
    context_content = [
        row[2]
        for row in context
    ]
    unified_ctx = "\n".join(context_content)

    return llm.generate_text(simple(context=unified_ctx,query=query.query))

@app.get("/simple_search/")
async def simple_search(query: Query):
    query_embedding = generate_embeddings(query.query)
    context = connection.similarity_search(query_embedding)
    return context