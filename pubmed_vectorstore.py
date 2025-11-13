from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_groq import ChatGroq
from langchain_community.docstore.document import Document
from prompt import PROMPT, EXAMPLE_PROMPT

# Load environment variables (for Groq API key, etc.)
load_dotenv()

# ---------- CONSTANTS ----------
CHUNK_SIZE = 1000
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path(__file__).parent / "resources" / "vectorstore"
COLLECTION_NAME = "mediassist_articles"

llm = None
vector_store = None

# ---------- INITIALIZATION ----------
def initialize_components():
    """
    Initializes the LLM and the Chroma vector store.
    """
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000
        )

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True},
        )
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTORSTORE_DIR)
        )

# ---------- VECTOR CREATION ----------
def process_pubmed_articles(articles):
    """
    Takes a list of article dictionaries (from PubMedRetriever)
    and stores them as vector embeddings in the Chroma DB.
    """

    yield "Initializing components..."
    initialize_components()

    vector_store.reset_collection()
    yield "Processing articles..."

    docs = []
    for article in articles:
        # Combine title and abstract into a single text block
        abstract_text = " ".join(article["abstract"].values())
        content = f"Title: {article['title']}\n\nAbstract: {abstract_text}"

        metadata = {
            "pmid": article["pmid"],
            "journal": article["journal"],
            "authors": article["authors"],
            "publication_date": article["publication_date"],
            "source": f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/"
        }

        docs.append(Document(page_content=content, metadata=metadata))

    # Split long abstracts if needed
    yield "Splitting text into chunks..."
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=CHUNK_SIZE
    )

    split_docs = text_splitter.split_documents(docs)
    uuids = [str(uuid4()) for _ in range(len(split_docs))]

    yield f"Adding {len(split_docs)} chunks to the vector store..."
    vector_store.add_documents(split_docs, ids=uuids)

    yield "✅ Done adding PubMed articles to vector DB."

# ---------- QUERY FUNCTION ----------
def generate_answer(query):
    """
    Uses the vector DB to retrieve relevant articles
    and generate an LLM-based answer with sources.
    """
    if not vector_store:
        raise RuntimeError("Vector database is not initialized")

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PROMPT,
            "document_prompt": EXAMPLE_PROMPT,
            "document_variable_name": "summaries"
        }
    )

    result = chain.invoke({"question": query}, return_only_outputs=True)

    # Extract unique sources by using a set to track PMIDs we've seen
    unique_sources = []
    seen_sources = set()

    for doc in result["source_documents"]:
        source_url = doc.metadata["source"]
        if source_url not in seen_sources:
            seen_sources.add(source_url)
            unique_sources.append(source_url)

    first_doc_content = (
        result["source_documents"][0].page_content
        if result["source_documents"]
        else None
    )

    return result["answer"], unique_sources, first_doc_content