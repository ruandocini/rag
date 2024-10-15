import psycopg2
from github import Github, Auth
import os
from pydantic import BaseModel
import base64
import hashlib
from markdown import markdown
from typing import List
from concurrent.futures import ThreadPoolExecutor

class Repository(BaseModel):
    name: str
    documentation_path: str

class Database():
    def __init__(self, user, password, host, port, database):
        self.conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        self.cursor = self.conn.cursor()

    def insert_item(self, item_id, name):
        # verify if item exists
        self.cursor.execute(
            "SELECT * FROM items WHERE name = %s",
            (name, )
        )
        if self.cursor.fetchone() is not None:
            # verify if item_id is the same
            self.cursor.execute(
                "SELECT id FROM items WHERE id = %s",
                (item_id, )
            )
            if self.cursor.fetchone() is None:
                # update item_id
                self.cursor.execute(
                    """
                    UPDATE items SET id = %s WHERE name = %s;
                    """,
                    (item_id, name)
                )
                self.cursor.connection.commit()
                # delete contents
                self.cursor.execute(
                    """
                    DELETE FROM contents WHERE item_id = %s;
                    """,
                    (item_id, )
                )
                self.cursor.connection.commit()
                return "updated"
            else:
                return "unchanged"
        
        else:
            # insert item
            self.cursor.execute(
                """
                INSERT INTO items (id, name) VALUES (%s, %s); 
                """,
                (item_id, name)
            )
            return "inserted"

    def insert_contents(self, content_id, item_id, content, embedding):
        self.cursor.execute(
            """
            INSERT INTO contents (id, item_id, content, embedding) VALUES (%s, %s, %s, %s)
            """,
            (content_id, item_id, content, embedding)
        )
        print("Added content {}".format(content_id))
        self.cursor.connection.commit()
    
    def delete_item(self, item_id: str):
        self.cursor.execute(
            """
            DELETE FROM items WHERE id = %s;
            DELETE FROM contents WHERE item_id = %s;
            """,
            (item_id, item_id)
        )
        self.cursor.connection.commit()

    def similarity_search(self, query_embedding):
        self.cursor.execute(
            """
            SELECT items.id, items.name, contents.content, 1 - (contents.embedding <=> %s) AS cosine_similarity
            FROM contents
            JOIN items ON items.id = contents.item_id
            ORDER BY cosine_similarity 
            DESC LIMIT 30
            """,
            (query_embedding,)
        )
        return self.cursor.fetchall()
    
    def decode_content(self, content):
        return {
            "filename": str(content.path.replace("/","__")), 
            "base_64":hashlib.sha256(content.content.encode()).hexdigest(), 
            "content": base64.b64decode(content.content).decode("utf-8")
        } 
    
    def extract_github_documents(self, repository: Repository):

        auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
        g = Github(auth=auth)
        repo = g.get_repo(repository.name)
        contents = repo.get_contents(repository.documentation_path, ref="main")
        with ThreadPoolExecutor(max_workers=30) as executor:
            decoded_contents = list(executor.map(self.decode_content, contents))
        return decoded_contents