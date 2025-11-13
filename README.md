# 🧠 MediAssist AI — PubMed Research Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)

**An intelligent biomedical RAG system specialized in Intermittent Fasting research**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

**MediAssist AI** is a Retrieval-Augmented Generation (RAG) system designed to help researchers, healthcare professionals, and curious minds explore the latest scientific literature on **Intermittent Fasting (IF)**.

Built with LLMs and vector databases, MediAssist fetches, processes, and analyzes PubMed articles to provide evidence-based answers to your medical research questions.

---

## ✨ Features

### 🔍 **Intelligent Article Retrieval**
- Automatic PubMed search for relevant research articles
- Manual URL ingestion for targeted analysis
- Fetches up to 300 articles per query
- Smart caching system for faster repeated queries

### 🧬 **Advanced RAG Pipeline**
- Vector-based semantic search using ChromaDB
- HuggingFace embeddings for accurate similarity matching
- Context-aware answer generation using Groq's LLaMA 3.3 70B
- Source attribution with direct PubMed links

### 💡 **User-Friendly Interface**
- Clean, intuitive Streamlit web interface
- Real-time progress tracking
- Human-in-the-loop (HITL) confirmations for autonomous search. Confirmation needed due to increased API usage and token cost.
- Cache management options
- Multi-query support with data reuse

### 🎯 **Specialized Knowledge**
Optimized for research on intermittent fasting (IF) as a treatment approach for:

- Type 2 Diabetes
- Metabolic Disorders
- Obesity

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Groq API key (free tier available at [groq.com](https://groq.com))
- Hugging Face Access Token (available at [huggingface.co](https://huggingface.co/settings/tokens))

### Step 1: Clone the Repository
```bash
git clone https://github.com/pedroabestard/mediassist-ai.git
cd mediassist-ai
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_access_token_here
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 💻 Usage

### Option 1: Automatic Search
1. Enter your research question in the text input
2. Click **"🔎 Search & Generate Answer"**
3. Confirm automatic PubMed fetch when prompted
4. Wait for the system to retrieve and process articles
5. View your evidence-based answer with sources

### Option 2: Manual URL Ingestion
1. Paste up to 3 PubMed URLs in the sidebar
2. Click **"📚 Ingest Documents"**
3. Enter your question
4. Click **"🔎 Search & Generate Answer"**
5. Get answers based exclusively on your provided articles

### Cache Management
- **Reuse cached data**: Answer new questions with previously fetched articles
- **Clear cache**: Start fresh with the **"🗑️ Clear Cache & Start Fresh"** button

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                  │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│    │  URL Input   │  │  Query Input │  │ Cache Control│     │
│    └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              PubMed Retriever (pubmed.py)                   │
│  • Search PubMed API                                        │
│  • Fetch article abstracts, metadata                        │
│  • Extract PMIDs, titles, authors, journals                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│          Vector Store Manager (pubmed_vectorstore.py)       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  1. Text Chunking (RecursiveCharacterTextSplitter)  │    │
│  │  2. Embedding Generation (HuggingFace)              │    │
│  │  3. ChromaDB Storage                                │    │
│  │  4. Semantic Retrieval                              │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM Chain (Groq + LangChain)                   │
│  • Custom prompts (prompt.py)                               │
│  • RetrievalQAWithSourcesChain                              │
│  • LLaMA 3.3 70B Versatile                                  │
│  • Source attribution                                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    User Answer + Sources                    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input Stage**: User provides query and PubMed URLs (optional)
2. **Retrieval Stage**: System fetches relevant articles from PubMed
3. **Processing Stage**: Articles chunked and embedded into vector database
4. **Query Stage**: User question embedded and matched against stored vectors
5. **Generation Stage**: LLM generates answer using retrieved context
6. **Output Stage**: Answer displayed with source citations

---

## 📂 Project Structure

```
mediassist-ai/
│
├── app.py                      # Main Streamlit application
├── pubmed.py                   # PubMed API interaction
├── pubmed_vectorstore.py       # Vector DB management & RAG chain
├── prompt.py                   # LLM prompt templates
├── main.py                     # CLI interface (optional)
│
├── resources/                  # This folder will be created once you run the code
│   ├── vectorstore/            # ChromaDB persistent storage
│   └── cache/                  # Query cache storage
│
├── .env                        # Environment variables (not in repo)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔧 Configuration

### LLM Settings (pubmed_vectorstore.py)
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Model selection
    temperature=0.3,                   # Lower = more focused
    max_tokens=2000                    # Response length
)
```

### Embedding Model
```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

### Chunk Settings
```python
CHUNK_SIZE = 1000  # Characters per chunk
```

### Search Parameters
```python
max_results=300  # Articles per auto-fetch query
```

---

## 🧪 Example Queries

**Research Questions:**
- "What are the effects of intermittent fasting on insulin sensitivity?"
- "How does time-restricted eating impact weight loss in obese patients?"
- "What is the relationship between fasting and HbA1c levels in Type 2 Diabetes?"
- "Are there any risks associated with prolonged fasting periods?"
- "What fasting protocols show the best outcomes for metabolic syndrome?"

---

## 🛡️ Limitations & Disclaimer

⚠️ **Important Notice:**
- MediAssist is for **informational and research purposes only**
- Not a substitute for professional medical advice
- Always consult healthcare providers for medical decisions
- Answers based on available PubMed abstracts (not full texts)
- LLM responses may occasionally contain inaccuracies

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Improvement
- [ ] Support for full-text article processing
- [ ] Advanced filtering (date ranges, journals, authors)

---


## 🌟 Star History

If you find MediAssist helpful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ using Streamlit, LangChain, and PubMed API**

© 2025 MediAssist AI

[⬆ Back to Top](#-mediassist-ai--pubmed-research-assistant)

</div>