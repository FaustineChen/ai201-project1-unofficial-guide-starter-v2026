"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import re
import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?
    """
    """
    Splits each thread into (question + one reply) chunks, using the
    THREAD / --- reply N (votes) --- structure instead of fixed windows.

    The question is prepended to every chunk, including sub-chunks produced
    when a single reply is too long to fit in chunk_size — see criterion 4.
    """

    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    reply_pattern = re.compile(
        r"--- reply \d+ \(\d+ votes\) ---\s*\n(.*?)(?=\n--- reply \d+|\Z)",
        re.DOTALL,
    )

    chunks: list[Chunk] = []
    for doc in documents:
        question_match = re.match(r"THREAD:\s*(.+)", doc.text)
        if not question_match:
            continue                                 # skip if doesn't match expected format
        question = question_match.group(1).strip()

        index = 0
        for reply_match in reply_pattern.finditer(doc.text):
            reply_text = reply_match.group(1).strip()
            combined = f"{question}\n\n{reply_text}"

            if len(combined) <= chunk_size:
                chunks.append(
                    Chunk(
                        text=combined,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

                # check every chunk resulting from a thread split retains the original question
                assert combined.startswith(question), (
                    f"Chunk from {doc.source} does not start with the question"
                )

            else:
                # Reply itself is too long — window over just the reply,
                # re-attaching the question to every resulting piece.
                start = 0
                budget = chunk_size - len(question) - 2         # room left for reply text
                while start < len(reply_text):
                    piece = reply_text[start : start + budget].strip()
                    if piece:
                        combined_piece = f"{question}\n\n{piece}"
                        chunks.append(
                            Chunk(
                                text=combined_piece,
                                source=doc.source,
                                index=index,
                                produced_by="chunker.py::split_documents",
                            )
                        )
                        index += 1
                    start += budget - overlap

                    # check every chunk resulting from a thread split retains the original question
                    assert combined_piece.startswith(question), (
                        f"Split chunk from {doc.source} does not start with the question"
                    )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))

    # TEST
    print("Below are chunked text")
    for chunk in chunks:
        print(chunk.text)
        print("=" * 60)
