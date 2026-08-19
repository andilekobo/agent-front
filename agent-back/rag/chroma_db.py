import chromadb
from pathlib import Path


# Location where Chroma will store the database
DB_PATH = Path(__file__).parent / "data" / "chroma"


# Create persistent Chroma client
client = chromadb.PersistentClient(
    path=str(DB_PATH)
)


# Create or load CareerOps collection
collection = client.get_or_create_collection(
    name="careerops_knowledge"
)


def get_collection():
    return collection