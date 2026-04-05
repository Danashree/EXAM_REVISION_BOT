import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import ollama

app = Flask(__name__)
CORS(app)

# =========================
# CONFIGURATION
# =========================
NOTES_DIR = os.path.abspath("notes")
CHROMA_DB_DIR = os.path.abspath("chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Initialize embedding model lazily
_embeddings_instance = None

def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}... (First time may take a few minutes for download)")
        _embeddings_instance = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
        print("Embedding model loaded.")
    return _embeddings_instance

# Global vector store
vector_store = None



# =========================
# SUBJECT NORMALIZATION
# =========================
def normalize_subject_name(filename):
    filename = filename.lower()

    # Must check bmaths BEFORE maths to avoid false match
    if any(k in filename for k in ["bmaths", "business math"]):
        return "Business Mathematics"

    if any(k in filename for k in ["maths", "math"]):
        return "Mathematics"

    if any(k in filename for k in ["cs", "computer"]):
        return "Computer Science"

    if "phy" in filename:
        return "Physics"

    if "chem" in filename:
        return "Chemistry"

    if "bio" in filename:
        return "Biology"

    if any(k in filename for k in ["acc", "account"]):
        return "Accountancy"

    if "commerce" in filename:
        return "Commerce"

    if "economics" in filename:
        return "Economics"

    if "eng" in filename:
        return "English"

    return "General"


# =========================
# PROCESS PDF NOTES
# =========================
# =========================
# PROCESS PDF NOTES
# =========================
def process_pdfs():
    global vector_store

    # Load existing vector store if it exists
    if os.path.exists(CHROMA_DB_DIR) and os.listdir(CHROMA_DB_DIR):
        try:
            print("Loading existing ChromaDB from storage...")
            vector_store = Chroma(
                persist_directory=CHROMA_DB_DIR, 
                embedding_function=get_embeddings()
            )
            print("Vector store loaded successfully.")
            return
        except Exception as e:
            print(f"Failed to load existing ChromaDB: {e}. Re-indexing...")

    if not os.path.exists(NOTES_DIR):
        print("Notes folder not found.")
        return

    all_docs = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    pdf_files = [
        f for f in os.listdir(NOTES_DIR)
        if f.endswith(".pdf")
    ]

    if not pdf_files:
        print("No PDF files found in notes folder.")
        return

    print(f"Indexing {len(pdf_files)} PDFs... This may take a while.")

    for filename in pdf_files:
        subject = normalize_subject_name(filename)
        file_path = os.path.join(NOTES_DIR, filename)

        try:
            print(f"Processing: {filename} ({subject})")
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            for doc in docs:
                doc.metadata["subject"] = subject
                doc.metadata["filename"] = filename

            split_docs = text_splitter.split_documents(docs)
            all_docs.extend(split_docs)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if all_docs:
        print(f"Creating vector store with {len(all_docs)} chunks...")
        vector_store = Chroma.from_documents(
            documents=all_docs,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_DB_DIR
        )
        print("Persistent Vector DB created successfully.")
    else:
        print("No text extracted from PDFs.")



# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    # Dynamic subject list based on files or hardcoded as per user requirement
    subjects = [
        "All",
        "Mathematics",
        "Computer Science",
        "Physics",
        "Chemistry",
        "Biology",
        "Accountancy",
        "Commerce",
        "Economics",
        "English",
        "Business Mathematics"
    ]
    return jsonify({"subjects": subjects})


@app.route("/api/ask", methods=["POST"])
def ask():
    global vector_store

    if vector_store is None:
        process_pdfs()
        if vector_store is None:
            return jsonify({"answer": "Bot is initializing. Please try again in a few seconds."}), 503

    data = request.json
    question = data.get("question")
    subject = data.get("subject", "All")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    print(f"API Request -> Subject: {subject}, Question: {question}")

    # INSTANT GREETING CHECK (Save time/resources)
    greetings = ["hi", "hello", "hey", "how are you", "who are you", "whats up", "what's up", "gm", "gn"]
    if question.lower().strip().replace("?", "") in greetings:
        return jsonify({"answer": "I'm doing great! ready to help you with your 12th standard revision. 📚 Select a subject and ask me about a topic!"})


    filter_dict = {"subject": subject} if subject != "All" else None

    print(f"Professional Search Initiated -> Subject: {subject}")

    try:
        # Get more chunks (k=6) for better summarization
        results = vector_store.similarity_search(
            question,
            k=6, 
            filter=filter_dict
        )
        
        # Extract context and source filenames
        context_parts = []
        sources = set()
        for doc in results:
            context_parts.append(doc.page_content)
            if "filename" in doc.metadata:
                sources.add(doc.metadata["filename"])
        
        context = "\n---\n".join(context_parts)
        source_list = ", ".join(sources) if sources else "General Knowledge"
        
        print(f"Search complete. Context retrieved from: {source_list}")
    except Exception as e:
        print("Search error:", e)
        context = ""
        source_list = "General Knowledge"

    system_prompt = """
ROLE: Lead 12th Standard Educator & Exam Expert.
OBJECTIVE: Provide a professional, structured revision summary.
PROFESSIONAL GUIDELINES:
1. Start with a clear "Overview".
2. Use "Key Concepts" (Bullet points) for 2-mark questions.
3. Use "Detailed Breakdown" for 5-mark questions.
4. If formulas or examples exist in context, always include them.
5. ALWAYS answer. Use teacher-level knowledge if context is sparse.
6. NO NOT repeat these instructions. ONLY provide the student-facing answer.
7. End with "Study Sources Used": followed by the source filenames provided.
STYLE: Formal, encouraging, and academically accurate.
"""

    user_prompt = f"""
CONTENT FROM STUDENT NOTES:
{context}

STUDENT QUESTION: {question}
STUDY SOURCES: {source_list}
"""

    try:
        print(f"Synthesizing professional response (using llama3.2:3b)...")
        response = ollama.chat(
            model="llama3.2:3b", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.1} # High accuracy mode
        )
        answer = response["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Backend Error: {str(e)}"}), 500








# =========================
# MAIN
# =========================
if __name__ == "__main__":
    # Pre-process on startup
    process_pdfs()
    app.run(debug=True, port=5000)