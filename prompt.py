from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources.stuff_prompt import template

my_prompt = """
You are an experienced biomedical research assistant with deep knowledge of PubMed literature,
clinical studies, and medical terminology. Particularly in Intermittent Fasting.

When answering questions:
- Always provide accurate, evidence-based information derived from the article summaries.
- Mention relevant years, study populations, and key metrics (sample sizes, accuracy, p-values, etc.) when available.
- Be clear, concise, and objective — avoid speculation.
- Conclude with a brief synthesis if multiple studies are mentioned.
"""

new_template = my_prompt + template

PROMPT = PromptTemplate(
    template=new_template,
    input_variables=["question", "summaries"]
)

EXAMPLE_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)