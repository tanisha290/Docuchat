"""
Standalone RAG pipeline smoke test — no Flask, no database.

Usage:
    cd backend
    python scripts/test_rag.py path/to/some.pdf "your question here"
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag_engine import process_document, answer_question  # noqa: E402


def main():
    if len(sys.argv) < 3:
        print('Usage: python scripts/test_rag.py path/to/file.pdf "your question"')
        sys.exit(1)

    file_path = sys.argv[1]
    question = sys.argv[2]
    fake_document_id = "test"

    print(f"Processing {file_path} ...")
    num_pages, num_chunks, index_path = process_document(fake_document_id, file_path)
    print(f"Extracted {num_pages} pages, built {num_chunks} chunks.")
    print(f"Index saved to: {index_path}\n")

    print(f"Question: {question}")
    result = answer_question(question=question, document_id=fake_document_id)
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {result['sources']}")


if __name__ == "__main__":
    main()
