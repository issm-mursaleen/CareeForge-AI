"""Multi-algorithm resume ranking + optional LLM explanation."""
from __future__ import annotations

import asyncio
from typing import Iterable

from beanie import PydanticObjectId
from ai_engine.extraction import extract_text
from ai_engine.llm.groq_client import GroqClient
from ai_engine.preprocessing import preprocess, preprocess_query
from ai_engine.ranking import rank_bert, rank_bm25, rank_word2vec

from ..core.config import get_settings
from ..core.exceptions import NotFound, ValidationFailed
from ..models.job_match import CandidateScore, JobMatch
from ..models.resume import Resume
from ..models.user import User
from .resume_service import ResumeService

ALGO_WEIGHTS = {"bm25": 0.2, "word2vec": 0.2, "bert": 0.6}


class RankingService:
    @staticmethod
    async def rank(
        recruiter: User,
        job_title: str,
        job_description: str,
        resume_ids: list[str],
        algorithms: list[str],
        explain_top_k: int = 3,
    ) -> JobMatch:
        resumes = await ResumeService.get_many_for_user(recruiter, resume_ids)
        if not resumes:
            raise NotFound("None of the requested resumes were found for this account")

        raw_texts = [r.raw_text for r in resumes]
        tokens = [preprocess(t) for t in raw_texts]
        query_tokens = preprocess_query(job_description)

        results = await _run_algorithms(algorithms, tokens, raw_texts, query_tokens, job_description)
        candidates = RankingService._merge_scores(resumes, results, algorithms)
        await _attach_explanations(candidates, algorithms, job_description, explain_top_k,
                                   text_by_name={r.file_name: r.raw_text for r in resumes})

        job_match = JobMatch(
            recruiter_id=recruiter.id,
            job_title=job_title,
            job_description=job_description,
            algorithms=algorithms,
            candidates=sorted(candidates, key=lambda c: c.composite or 0, reverse=True),
        )
        await job_match.insert()
        return job_match

    @staticmethod
    async def rank_raw_files(
        recruiter: User,
        job_title: str,
        job_description: str,
        file_pairs: list[tuple[str, bytes]],
        algorithms: list[str],
        explain_top_k: int = 3,
    ) -> JobMatch:
        """Rank uploaded files directly — no prior analysis required."""
        # Extract text from each file; skip any that yield no content
        docs: list[tuple[str, str]] = []
        for fname, fbytes in file_pairs:
            doc = await asyncio.to_thread(extract_text, fname, fbytes)
            if not doc.is_empty:
                docs.append((fname, doc.text))

        if not docs:
            raise ValidationFailed("No text could be extracted from the uploaded files")

        file_names = [d[0] for d in docs]
        raw_texts = [d[1] for d in docs]
        tokens = [preprocess(t) for t in raw_texts]
        query_tokens = preprocess_query(job_description)

        results = await _run_algorithms(algorithms, tokens, raw_texts, query_tokens, job_description)

        # Build candidates with generated IDs (no stored Resume documents)
        normalised = {algo: _minmax(scores) for algo, scores in results.items()}
        algos = list(algorithms)
        total_weight = sum(ALGO_WEIGHTS[a] for a in algos)
        candidates: list[CandidateScore] = []
        for i, fname in enumerate(file_names):
            composite = (
                sum(ALGO_WEIGHTS[a] * normalised[a][i] for a in algos) / total_weight
                if total_weight else 0
            )
            candidates.append(CandidateScore(
                resume_id=PydanticObjectId(),          # ephemeral — no Resume doc
                file_name=fname,
                bm25=results["bm25"][i] if "bm25" in results else None,
                word2vec=results["word2vec"][i] if "word2vec" in results else None,
                bert=results["bert"][i] if "bert" in results else None,
                composite=round(composite, 4),
            ))

        await _attach_explanations(candidates, algorithms, job_description, explain_top_k,
                                   text_by_name=dict(zip(file_names, raw_texts)))

        job_match = JobMatch(
            recruiter_id=recruiter.id,
            job_title=job_title,
            job_description=job_description,
            algorithms=algorithms,
            candidates=sorted(candidates, key=lambda c: c.composite or 0, reverse=True),
        )
        await job_match.insert()
        return job_match

    @staticmethod
    def _merge_scores(
        resumes: list[Resume],
        results: dict[str, list[float]],
        algorithms: Iterable[str],
    ) -> list[CandidateScore]:
        normalised = {algo: _minmax(scores) for algo, scores in results.items()}
        algos = list(algorithms)
        total_weight = sum(ALGO_WEIGHTS[a] for a in algos)
        out: list[CandidateScore] = []
        for i, resume in enumerate(resumes):
            composite = (
                sum(ALGO_WEIGHTS[a] * normalised[a][i] for a in algos) / total_weight
                if total_weight else 0
            )
            out.append(CandidateScore(
                resume_id=resume.id,
                file_name=resume.file_name,
                bm25=results["bm25"][i] if "bm25" in results else None,
                word2vec=results["word2vec"][i] if "word2vec" in results else None,
                bert=results["bert"][i] if "bert" in results else None,
                composite=round(composite, 4),
            ))
        return out


# ── helpers ──────────────────────────────────────────────────────────────────

async def _run_algorithms(
    algorithms: list[str],
    tokens: list[list[str]],
    raw_texts: list[str],
    query_tokens: list[str],
    job_description: str,
) -> dict[str, list[float]]:
    tasks: dict[str, asyncio.Future] = {}
    if "bm25" in algorithms:
        tasks["bm25"] = asyncio.to_thread(rank_bm25, tokens, query_tokens)
    if "word2vec" in algorithms:
        tasks["word2vec"] = asyncio.to_thread(rank_word2vec, tokens, query_tokens)
    if "bert" in algorithms:
        tasks["bert"] = asyncio.to_thread(rank_bert, raw_texts, job_description)
    return dict(zip(tasks.keys(), await asyncio.gather(*tasks.values())))


async def _attach_explanations(
    candidates: list[CandidateScore],
    algorithms: list[str],
    job_description: str,
    explain_top_k: int,
    text_by_name: dict[str, str],
) -> None:
    if explain_top_k <= 0 or not get_settings().groq_api_key:
        return
    try:
        groq = GroqClient()
        top = sorted(candidates, key=lambda c: c.composite or 0, reverse=True)[:explain_top_k]
        items = [(c.file_name, c.composite, text_by_name.get(c.file_name, "")) for c in top]
        evals = await groq.batch_explain(", ".join(algorithms), job_description, items)
        eval_by_file = {e.file_name: e for e in evals}
        for c in candidates:
            if c.file_name in eval_by_file:
                c.is_good_fit = eval_by_file[c.file_name].is_good_fit
                c.explanation = eval_by_file[c.file_name].explanation
    except Exception:  # noqa: BLE001
        pass


def _minmax(scores: list[float]) -> list[float]:
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return [0.5] * len(scores)
    return [(s - lo) / (hi - lo) for s in scores]
