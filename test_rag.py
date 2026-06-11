from backend.rag.rag_pipeline import create_vector_store

vector_store = create_vector_store("data/scheme_detail.txt")

docs = vector_store.similarity_search("वृद्धावस्था पेंशन", k=1)

print("\n=== RETRIEVED TEXT ===\n")
print(docs[0].page_content)