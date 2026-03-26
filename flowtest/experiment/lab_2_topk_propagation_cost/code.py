#!/usr/bin/env python3
"""H2: Top-K propagation vs random pairwise under fixed anchor budget."""
from __future__ import annotations

import json
from pathlib import Path

import json5
import numpy as np
from scipy.stats import kendalltau

ROOT = Path(__file__).resolve().parent


def load_params():
    return json5.loads((ROOT / "params.json5").read_text(encoding="utf-8"))


def gold_ranks(scores: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(-scores))


def build_embeddings(scores: np.ndarray, dim: int, noise: float, rng: np.random.Generator) -> np.ndarray:
    n = len(scores)
    rest = rng.normal(0, 1.0, size=(n, dim - 1))
    e = np.hstack([scores.reshape(-1, 1) + rng.normal(0, noise, size=(n, 1)), rest * noise])
    return e


def knn_idx(embeddings: np.ndarray, i: int, k: int) -> np.ndarray:
    d = np.linalg.norm(embeddings - embeddings[i], axis=1)
    order = np.argsort(d)
    return order[order != i][:k]


def wins_to_rank(wins: np.ndarray) -> np.ndarray:
    order = np.argsort(-wins, kind="stable")
    return np.argsort(order)


def simulate_random(
    scores: np.ndarray,
    budget: int,
    flip_p: float,
    rng: np.random.Generator,
) -> np.ndarray:
    n = len(scores)
    wins = np.zeros(n, dtype=np.float64)
    for _ in range(budget):
        i, j = rng.integers(0, n, size=2)
        if i == j:
            continue
        si, sj = scores[i], scores[j]
        i_wins = si > sj if si != sj else rng.random() < 0.5
        if rng.random() < flip_p:
            i_wins = not i_wins
        wins[i if i_wins else j] += 1
    return wins_to_rank(wins)


def simulate_propagate(
    scores: np.ndarray,
    embeddings: np.ndarray,
    budget: int,
    top_k: int,
    flip_p: float,
    derive_flip: float,
    score_band: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Each anchor compares (i,j); winner's Top-K neighbors get a derived comparison vs the loser."""
    n = len(scores)
    wins = np.zeros(n, dtype=np.float64)
    for _ in range(budget):
        i, j = rng.integers(0, n, size=2)
        if i == j:
            continue
        si, sj = scores[i], scores[j]
        i_beats_j = si > sj if si != sj else rng.random() < 0.5
        if rng.random() < flip_p:
            i_beats_j = not i_beats_j
        if i_beats_j:
            wins[i] += 1
            winner, loser = i, j
        else:
            wins[j] += 1
            winner, loser = j, i
        for k in knn_idx(embeddings, winner, top_k):
            if k in (i, j):
                continue
            if abs(float(scores[k]) - float(scores[winner])) > score_band:
                continue
            k_beats_loser = True
            if rng.random() < derive_flip:
                k_beats_loser = False
            if k_beats_loser:
                wins[k] += 1
            else:
                wins[loser] += 1
    return wins_to_rank(wins)


def main() -> None:
    p = load_params()
    n = int(p["n_items"])
    base = int(p["rng_seed"])
    n_seeds = int(p["n_seeds"])
    taus_r = []
    taus_p = []
    for s in range(n_seeds):
        rng = np.random.default_rng(base + s * 7919)
        scores = rng.uniform(0, 1, size=n)
        gold = gold_ranks(scores)
        emb = build_embeddings(
            scores,
            int(p["embed_dim"]),
            float(p["score_noise_in_embed"]),
            rng,
        )
        r_rank = simulate_random(scores, int(p["anchor_budget"]), float(p["pair_flip_prob"]), rng)
        p_rank = simulate_propagate(
            scores,
            emb,
            int(p["anchor_budget"]),
            int(p["top_k"]),
            float(p["pair_flip_prob"]),
            float(p["propagation_derive_flip"]),
            float(p.get("propagate_score_band", 0.25)),
            rng,
        )
        taus_r.append(float(kendalltau(r_rank, gold).statistic))
        taus_p.append(float(kendalltau(p_rank, gold).statistic))

    summary = {
        "hypothesis": "H2",
        "mean_tau_random": float(np.mean(taus_r)),
        "mean_tau_propagate": float(np.mean(taus_p)),
        "std_tau_random": float(np.std(taus_r)),
        "std_tau_propagate": float(np.std(taus_p)),
        "h2_propagate_better": float(np.mean(taus_p)) > float(np.mean(taus_r)),
        "seeds": n_seeds,
    }
    out = ROOT / p["output"]["result_json"]
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
