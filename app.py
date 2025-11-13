import streamlit as st
import time
import re
from pubmed import PubMedRetriever
from pubmed_vectorstore import process_pubmed_articles, generate_answer

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="MediAssist AI — PubMed Research Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 MediAssist AI — PubMed Research Assistant")
st.markdown("""
Welcome to **MediAssist**, a biomedical RAG system specialized in **Intermittent Fasting (IF)** as a treatment approach for **obesity**, 
**Type 2 Diabetes**, and **Metabolic Disorders**.  
You can either provide PubMed URLs manually or let the system automatically fetch relevant research for your query.
""")

# -------------------- SIDEBAR --------------------
st.sidebar.header("📥 Document Ingestion")

# --- Three separate URL inputs ---
url_inputs = [
    st.sidebar.text_input("PubMed URL 1 (optional)", placeholder="https://pubmed.ncbi.nlm.nih.gov/12345678/"),
    st.sidebar.text_input("PubMed URL 2 (optional)", placeholder="https://pubmed.ncbi.nlm.nih.gov/23456789/"),
    st.sidebar.text_input("PubMed URL 3 (optional)", placeholder="https://pubmed.ncbi.nlm.nih.gov/34567890/")
]

if "knowledge_source" not in st.session_state:
    st.session_state["knowledge_source"] = None
if "urls" not in st.session_state:
    st.session_state["urls"] = []
if "auto_fetch_confirmed" not in st.session_state:
    st.session_state["auto_fetch_confirmed"] = False
if "processing" not in st.session_state:
    st.session_state["processing"] = False
if "urls_processed" not in st.session_state:
    st.session_state["urls_processed"] = False
if "cache_reuse_confirmed" not in st.session_state:
    st.session_state["cache_reuse_confirmed"] = False
if "last_query" not in st.session_state:
    st.session_state["last_query"] = None

# --- Ingest Button ---
if st.sidebar.button("📚 Ingest Documents"):
    # Validate URLs
    valid_url_pattern = re.compile(r"^https://pubmed\.ncbi\.nlm\.nih\.gov/\d+/?$")
    urls = [u.strip() for u in url_inputs if u.strip() and valid_url_pattern.match(u.strip())]

    if urls:
        st.session_state["knowledge_source"] = "urls"
        st.session_state["urls"] = urls
        st.session_state["urls_processed"] = False  # Mark as not yet processed
        st.sidebar.success(f"{len(urls)} valid PubMed URLs ready for ingestion.")
    else:
        st.sidebar.warning(
            "⚠️ Please enter at least one valid PubMed URL (format: https://pubmed.ncbi.nlm.nih.gov/PMID/).")

# --- Clear Cache Button ---
if st.sidebar.button("🗑️ Clear Cache & Start Fresh"):
    st.session_state["knowledge_source"] = None
    st.session_state["urls"] = []
    st.session_state["urls_processed"] = False
    st.session_state["cache_reuse_confirmed"] = False
    st.session_state["last_query"] = None
    st.sidebar.success("Cache cleared! You can now start fresh.")

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: If you don't provide URLs, the assistant can automatically search PubMed for you.")

# -------------------- MAIN QUERY AREA --------------------
st.subheader("🔍 Ask a Question")

query = st.text_input("Enter your question here:",
                      placeholder="e.g., What are the effects of intermittent fasting on insulin sensitivity?")

if st.button("🔎 Search & Generate Answer"):
    if not query.strip():
        st.error("❌ Please enter a question.")
    else:
        st.session_state["processing"] = True
        st.session_state["current_query"] = query

# Process the query
if st.session_state.get("processing"):
    query = st.session_state.get("current_query", "")

    # Check if this is a new query and we have cached data
    if (st.session_state.get("urls_processed") and
            st.session_state.get("last_query") != query and
            not st.session_state.get("cache_reuse_confirmed")):

        st.warning("⚠️ You have cached data from a previous query.")
        cache_choice = st.radio(
            "Would you like to:",
            [
                "Use cached data for this new question",
                "Provide new URLs for this question",
                "Let the system auto-fetch articles for this question"
            ],
            index=0,
            key="cache_choice_radio"
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Confirm Choice", key="confirm_cache_choice"):
                if cache_choice == "Use cached data for this new question":
                    st.session_state["cache_reuse_confirmed"] = True
                    st.rerun()
                elif cache_choice == "Provide new URLs for this question":
                    st.session_state["knowledge_source"] = None
                    st.session_state["urls_processed"] = False
                    st.session_state["cache_reuse_confirmed"] = False
                    st.info("Please provide new URLs in the sidebar and click 'Ingest Documents'.")
                    st.session_state["processing"] = False
                else:  # Auto-fetch
                    st.session_state["knowledge_source"] = None
                    st.session_state["urls_processed"] = False
                    st.session_state["cache_reuse_confirmed"] = False
                    st.session_state["auto_fetch_confirmed"] = True
                    st.rerun()

    # Case 1: User provided URLs beforehand
    elif st.session_state.get("knowledge_source") == "urls":
        # First, we need to process the URLs into the vector store if not already done
        if not st.session_state.get("urls_processed"):
            st.info("Processing provided PubMed URLs...")

            # Extract PMIDs from URLs
            pmids = []
            for url in st.session_state["urls"]:
                match = re.search(r'/(\d+)/?$', url)
                if match:
                    pmids.append(match.group(1))

            progress = st.progress(0)
            status = st.empty()

            with st.spinner("Fetching and processing your provided articles..."):
                # Fetch abstracts for the provided PMIDs
                status.text(f"📄 Fetching {len(pmids)} article abstracts...")
                articles = PubMedRetriever.fetch_pubmed_abstracts(pmids)
                progress.progress(40)
                time.sleep(0.5)

                # Process articles into vector store
                status.text("⚙️ Processing articles and updating vector store...")
                for i, msg in enumerate(process_pubmed_articles(articles)):
                    progress.progress(min(80, 40 + i * 3))
                    st.text(msg)
                time.sleep(0.5)

                progress.progress(100)
                st.session_state["urls_processed"] = True

            status.empty()
            progress.empty()
            st.success("✅ URLs processed successfully!")

        # Now generate answer using the processed URLs
        with st.spinner("Generating answer from provided articles..."):
            answer, sources, _ = generate_answer(query)

        st.success("✅ Done!")
        st.markdown("### 🧠 Answer")
        st.write(answer)
        st.markdown("#### 🔗 Sources")
        for src in sorted(set(sources)):
            st.write(f"- {src}")

        # Update tracking variables
        st.session_state["last_query"] = query
        st.session_state["processing"] = False
        st.session_state["cache_reuse_confirmed"] = False

    # Case 2: No URLs — HITL confirmation to auto-fetch from PubMed
    elif not st.session_state.get("auto_fetch_confirmed"):
        st.warning("⚠️ No URLs provided or ingested. If you have already provided URLs, please, click **Ingest Documents** button before requesting an answer. If you haven't provide any the system can auto-fetch PubMed articles related to your query.")
        confirm = st.radio("Would you like MediAssist to automatically fetch relevant articles?", ["No", "Yes"],
                           index=0, key="confirm_radio")

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Confirm"):
                if confirm == "Yes":
                    st.session_state["auto_fetch_confirmed"] = True
                    st.rerun()
                else:
                    st.info("No problem! You can add URLs in the sidebar whenever you're ready.")
                    st.session_state["processing"] = False

    # Case 3: User confirmed auto-fetch OR reusing cache
    else:
        # If reusing cache, just generate answer directly
        if st.session_state.get("cache_reuse_confirmed") and st.session_state.get("urls_processed"):
            with st.spinner("Generating answer from cached data..."):
                answer, sources, _ = generate_answer(query)

            st.success("✅ Done!")
            st.markdown("### 🧠 Answer")
            st.write(answer)
            st.markdown("#### 🔗 Sources")
            for src in sorted(set(sources)):
                st.write(f"- {src}")

            # Update tracking variables
            st.session_state["last_query"] = query
            st.session_state["processing"] = False
            st.session_state["cache_reuse_confirmed"] = False

        # Otherwise, do auto-fetch
        else:
            progress = st.progress(0)
            status = st.empty()

            with st.spinner("Fetching and processing PubMed data..."):
                # Step 1: Search PMIDs
                status.text("🔎 Searching PubMed for relevant articles...")
                pmids = PubMedRetriever.search_pubmed_articles(query, max_results=100)
                progress.progress(20)
                time.sleep(0.5)

                # Step 2: Fetch abstracts
                status.text(f"📄 Fetching {len(pmids)} article abstracts...")
                articles = PubMedRetriever.fetch_pubmed_abstracts(pmids)
                progress.progress(50)
                time.sleep(0.5)

                # Step 3: Process articles into vector store
                status.text("⚙️ Processing articles and updating vector store...")
                for i, msg in enumerate(process_pubmed_articles(articles)):
                    progress.progress(min(80, 50 + i * 2))
                    st.text(msg)
                time.sleep(0.5)

                # Step 4: Generate the RAG-based answer
                status.text("💬 Generating answer with retrieved context...")
                answer, sources, _ = generate_answer(query)
                progress.progress(100)
                time.sleep(0.5)

            st.success("✅ Auto-fetch complete!")
            st.markdown("### 🧠 Answer")
            st.write(answer)
            st.markdown("#### 🔗 Sources")
            for src in sorted(set(sources)):
                st.write(f"- {src}")

            status.empty()
            progress.empty()

            # Update tracking variables
            st.session_state["urls_processed"] = True
            st.session_state["last_query"] = query
            st.session_state["processing"] = False
            st.session_state["auto_fetch_confirmed"] = False
            st.session_state["cache_reuse_confirmed"] = False

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, and PubMed API. © 2025 MediAssist AI")