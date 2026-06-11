"""Minimal chat UI for the procurement RAG assistant."""
import streamlit as st
from src.rag import ProcurementRAG

st.set_page_config(page_title="UK Procurement RAG", page_icon="📑")
st.title("UK Procurement Contracts Assistant")
st.caption(
    "Ask questions about UK public sector contracts. "
    "Data: Contracts Finder, licensed under the Open Government Licence v3.0."
)


@st.cache_resource
def load_rag():
    return ProcurementRAG()


rag = load_rag()

question = st.text_input("Your question", placeholder="e.g. Which IT contracts were awarded over £1m?")
if question:
    with st.spinner("Searching contracts..."):
        result = rag.answer(question)
    st.markdown("### Answer")
    st.write(result["answer"])
    with st.expander("Sources used"):
        for d in result["sources"]:
            st.text(d["text"])
