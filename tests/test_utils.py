from langchain_core.documents import Document
from src.utils.rag_helpers import estimate_tokens, build_context, build_citations

def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcdefgh") == 2
    assert estimate_tokens(None) == 0

def test_build_context():
    docs = [
        Document(page_content="Conteúdo 1", metadata={"source": "doc1.pdf", "page": 1}),
        Document(page_content="Conteúdo 2", metadata={"source": "doc2.txt"})
    ]
    context = build_context(docs)
    assert "[Documento 1 - Fonte: doc1.pdf (página 1)]" in context
    assert "Conteúdo 1" in context
    assert "[Documento 2 - Fonte: doc2.txt]" in context
    assert "Conteúdo 2" in context

def test_build_citations():
    docs = [
        Document(page_content="Texto curto", metadata={"source": "doc1", "score": 0.9}),
        Document(page_content="A" * 600, metadata={"source": "doc2", "page": 2})
    ]
    citations = build_citations(docs)
    
    assert len(citations) == 2
    
    # Primeiro doc
    assert citations[0].source == "doc1"
    assert citations[0].relevance_score == 0.9
    assert citations[0].excerpt == "Texto curto"
    
    # Segundo doc (truncado)
    assert citations[1].source == "doc2"
    assert citations[1].page == 2
    assert len(citations[1].excerpt) <= 503
    assert citations[1].excerpt.endswith("...")

