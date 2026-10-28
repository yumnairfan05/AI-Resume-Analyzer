"""Semantic matching with Sentence Transformers."""
import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, runs fine on CPU


@lru_cache(maxsize=1)
def load_model():
    return SentenceTransformer(MODEL_NAME)


def split_chunks(text: str, min_len: int = 25):
    parts = re.split(r"\n+|(?<=[.!?])\s+", text)
    chunks = [p.strip(" \t•·-–*") for p in parts]
    return [c for c in chunks if len(c) >= min_len]


def semantic_match(cv_text: str, jd_text: str) -> dict:
    """For every line of the job description, find the closest line in the CV.

    Returns a 0-1 score and the JD lines that the CV covers worst.
    """
    model = load_model()
    cv_chunks = split_chunks(cv_text) or [cv_text]
    jd_chunks = split_chunks(jd_text) or [jd_text]

    cv_emb = model.encode(cv_chunks, convert_to_tensor=True, normalize_embeddings=True)
    jd_emb = model.encode(jd_chunks, convert_to_tensor=True, normalize_embeddings=True)

    sims = util.cos_sim(jd_emb, cv_emb)      # [jd_lines x cv_lines]
    best = sims.max(dim=1).values            # best CV line for every JD line
    raw = float(best.mean())

    # MiniLM cosine: ~0.15 for unrelated text, ~0.65 for a strong match
    score = min(max((raw - 0.15) / (0.65 - 0.15), 0.0), 1.0)

    ranked = sorted(zip(jd_chunks, best.tolist()), key=lambda x: x[1])
    gaps = [(line, round(s, 2)) for line, s in ranked if s < 0.38][:5]

    return {"score": score, "gaps": gaps}
