# Exam Revision Bot 🎓📚🤖

An AI-powered, professional exam preparation assistant designed specifically for **students**. This bot helps students revise complex subjects using their own PDF notes and provides **exam-ready answers** (short & detailed styles) in simple, professional English.

Built using **Flask, ChromaDB, Sentence Transformers, and Ollama (Llama 3.2:3b)**.

---

## 🚀 Professional Features

- **📖 Smart RAG Pipeline:** Automatically reads, chunks, and indexes multiple PDF notes from your `notes/` folder.
- **🧠 Advanced Llama 3.2 Brain:** Uses the state-of-the-art **Llama 3.2 (3B)** model for smarter, faster, and more accurate reasoning.
- **🎯 Professional Source Attribution:** Every answer cites the specific PDF sources it retrieved (e.g., *Source: physics_unit1.pdf*).
- **🌙 Eyes-Safe Dark Mode:** Includes a sleek Dark Mode toggle for intensive late-night revision sessions.
- **🧹 Instant Greeting & Clean Chat:** Skips expensive searches for basic greetings and allows clearing chat history between subjects.
- **✨ Exam-Focused Summarization:** Tailors answers into "Overview", "Key Concepts", and "Detailed Breakdown" for perfect exam prep.

---

## 📂 Project Structure

```text
exam-revision-bot/
│
├── app.py              # Backend logic (Flask + RAG + Ollama)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
│
├── notes/              # Place your subject PDFs here
│   ├── maths.pdf
│   ├── economics.pdf
│   └── ...
│
├── chroma_db/          # Persistent local database (auto-generated)
│
├── templates/          # Frontend layout
│   └── index.html
│
└── static/             # Assets (Aesthetic CSS & JS)
    ├── style.css
    └── script.js
```

---

## ⚙️ Installation & Running

### 1) Prepare Ollama
Download and install Ollama from [ollama.com](https://ollama.com/download), then pull the **Llama 3.2** model:
```powershell
ollama pull llama3.2:3b
```

### 2) Install Dependencies
Open your project terminal and run:
```powershell
pip install -r requirements.txt
```

### 3) Add Your Notes
Place all your subject PDFs inside the `notes/` folder. The bot will automatically categorize them based on their filenames (e.g., *Physics*, *Biology*, *Commerce*).

### 4) Run the Application
```powershell
python app.py
```

### 5) Open in Browser
Visit: `http://127.0.0.1:5000`

---

## 🧠 Supported Subjects
The bot intelligently detects and filters answers for common subjects:
- Mathematics & Business Mathematics
- Physics, Chemistry & Biology
- Computer Science & IT
- Accountancy, Commerce & Economics
- English & Literature

---

## 💡 Example Queries
- *"Explain the concept of photosynthesis."*
- *"What are the key functions of management?"*
- *"Define the LEGB rule with an example."*
- *"Give me a summary of Chapter 1."*

---

## 👩💻 Developed For
Students to make exam preparation faster, smarter, and more organized! 🎓📖✨
