"""Tests for chunker.py — structural invariants and edge cases."""
import os
import sys

# Add the project root (one level up from tests/) to sys.path so we can
# import chunker.py directly, without turning tests/ into a package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chunker import split_documents
from ingest import Document


def test_normal_reply_retains_question():
    """Every chunk from a normal-length reply should start with the question."""
    doc = Document(
        text=(
            "THREAD: Is it weird to go to office hours with no specific question?\n\n"
            "--- reply 1 (44 votes) ---\n"
            "No, and this is the single most common thing first years get wrong."
        ),
        source="test_thread.txt",
    )
    chunks = split_documents([doc], chunk_size=800, overlap=50)

    assert len(chunks) == 1
    assert chunks[0].text.startswith(
        "Is it weird to go to office hours with no specific question?"
    )


def test_long_reply_triggers_fallback_and_retains_question():
    """A reply longer than chunk_size should be split, with the question
    prepended to every resulting piece."""
    question = "test question?"
    long_reply = "x " * 500  # deliberately exceeds chunk_size
    doc = Document(
        text=f"THREAD: {question}\n\n--- reply 1 (1 votes) ---\n{long_reply}",
        source="fake_long_reply.txt",
    )

    chunks = split_documents([doc], chunk_size=100, overlap=20)

    assert len(chunks) > 1, "expected the long reply to trigger the fallback split"
    for chunk in chunks:
        assert chunk.text.startswith(question), (
            f"chunk {chunk.index} from {chunk.source} does not start with the question"
        )


def test_multiple_replies_produce_separate_chunks():
    """Each reply in a thread should become its own chunk, not merged together."""
    doc = Document(
        text=(
            "THREAD: First winter here — what do I need?\n\n"
            "--- reply 1 (26 votes) ---\n"
            "Layers, not a big coat.\n\n"
            "--- reply 2 (31 votes) ---\n"
            "Boots with actual tread."
        ),
        source="test_thread2.txt",
    )
    chunks = split_documents([doc], chunk_size=800, overlap=50)

    assert len(chunks) == 2
    assert chunks[0].index == 0
    assert chunks[1].index == 1


def test_malformed_document_is_skipped():
    """A document without a THREAD: header should not crash the chunker."""
    doc = Document(text="No thread header here.", source="bad.txt")
    chunks = split_documents([doc], chunk_size=800, overlap=50)

    assert chunks == []