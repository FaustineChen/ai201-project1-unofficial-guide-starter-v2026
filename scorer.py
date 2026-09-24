import re

from rapidfuzz import fuzz


def _normalize_text(text: str) -> str:
    """Normalize a string so fuzzy comparison is less sensitive to spacing/punctuation."""
    if text is None:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def judge(question, expects, answer, results) -> bool:
    """
    given question and expects
    results is from retrival
    """

    return expects.lower().strip() in answer.lower()


def judge_rapidfuzz(question, expects, answer, results) -> bool:
    """Use rapidfuzz to judge whether the generated answer matches the expected answer.

    This is a fuzzy comparison, so it is more tolerant than direct substring checks.
    It handles small wording differences, punctuation, and ordering changes.
    """
    expected = _normalize_text(expects)
    generated = _normalize_text(answer)

    if not expected or not generated:
        return False

    if expected == generated:
        return True

    score = max(
        fuzz.ratio(expected, generated),
        fuzz.partial_ratio(expected, generated),
        fuzz.token_set_ratio(expected, generated),
    )
    return score >= 80


"""
use LLM as judge -> expensive
use rapidfuzz to write judge function

0 library = no library
"""


def retrivalHit(expects, results) -> bool:
    """
    any part of my expect in the results
    """
    return any(expects.strip().lower() for chunk in results);


question = "Is it difficult to change major to different department?"
original_expects = "Change direction in third year usually need an extra semester." 
answer = "Changing your major is administratively trivial because it just involves a form, but whether it is difficult depends on the direction and whether your previously taken credits map onto the new requirements" 

print(judge_rapidfuzz(question, original_expects, answer, results=None))


rephrased_expects = "Changing majors is usually easy administratively, but it depends on how well your completed credits fit the new major. Switching into a very different department may delay graduation, so it’s best to check with the new department’s adviser."
print(judge_rapidfuzz(question, rephrased_expects, answer, results=None))