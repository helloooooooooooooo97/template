#!/usr/bin/env python3
"""H3: ROMVI-style power iteration vs net wins under flipped pairwise noise."""
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


def rank_from_scores(s: np.ndarray) -> np.ndarray:
    order = np.argsort(-s, kind="stable")
    return np.argsort(order)


def build_w_matrix(
    scores: np.ndarray,
    n_samples: int,
    flip_ratio: float,
    rng: np.random.Generator,
    eps: float,
) -> np.ndarray:
    n = len(scores)
    w = np.zeros((n, n), dtype=np.float64)
    edges = []
    for _ in range(n_samples):
        i, j = rng.integers(0, n, size=2)
        if i == j:
            continue
        si, sj = scores[i], scores[j]
        i_beats_j = si > sj if si != sj else rng.random() < 0.5
        edges.append((i, j, i_beats_j))
    m = max(1, int(round(flip_ratio * len(edges))))
    flip_idx = rng.choice(len(edges), size=m, replace=False)
    for idx in flip_idx:
        i, j, b = edges[idx]
        edges[idx] = (i, j, not b)
    for i, j, i_beats_j in edges:
        if i_beats_j:
            w[i, j] += 1.0
        else:
            w[j, i] += 1.0
    return w


def romvi_scores(w: np.ndarray, power_iter: int, tol: float, eps: float, teleport: float = 0.15) -> np.ndarray:
    """Rank-centrality-style: from loser j walk to winner i with prob ∝ w[i,j]; plus uniform teleport."""
    n = w.shape[0]
    # P[j,i] ∝ w[i,j] (i beat j); rows of P sum to 1
    col = w.sum(axis=0) + eps
    p = np.zeros((n, n), dtype=np.float64)
    for j in range(n):
        for i in range(n):
            p[j, i] = w[i, j] / col[j]
    p = (1.0 - teleport) * p + teleport / n
    p /= p.sum(axis=1, keepdims=True) + eps
    v = np.ones(n) / n
    for _ in range(power_iter):
        nv = p.T @ v
        s = nv.sum() + eps
        nv = nv / s
        if np.linalg.norm(nv - v, 1) < tol:
            break
        v = nv
    return v


def netwin_scores(w: np.ndarray) -> np.ndarray:
    return (w - w.T).sum(axis=1)


def run_seeds(
    n: int,
    n_seeds: int,
    base_seed: int,
    n_pair_samples: int,
    flip_ratio: float,
    eps: float,
    power_iter: int,
    tol: float,
    teleport: float,
) -> tuple[list[float], list[float]]:
    taus_r: list[float] = []
    taus_n: list[float] = []
    for s in range(n_seeds):
        rng = np.random.default_rng(base_seed + s * 4243)
        scores = rng.uniform(0, 1, size=n)
        gold = gold_ranks(scores)
        w = build_w_matrix(scores, n_pair_samples, flip_ratio, rng, eps)
        v = romvi_scores(w, power_iter, tol, eps, teleport)
        nw = netwin_scores(w)
        r_rank = rank_from_scores(v)
        n_rank = rank_from_scores(nw)
        taus_r.append(float(kendalltau(r_rank, gold).statistic))
        taus_n.append(float(kendalltau(n_rank, gold).statistic))
    return taus_r, taus_n


def main() -> None:
    p = load_params()
    n = int(p["n_items"])
    base = int(p["rng_seed"])
    n_seeds = int(p["n_seeds"])
    eps = float(p["eps"])
    power_iter = int(p["power_iter"])
    tol = float(p["tol"])
    teleport = float(p.get("teleport", 0.15))
    n_pair = int(p["n_pair_samples"])
    noises = p.get("noise_flip_ratios")
    if not noises:
        noises = [float(p["noise_flip_ratio"])]

    sweep = []
    primary_flip = float(p["noise_flip_ratio"])
    primary_entry: dict | None = None
    pr_taus_r: list[float] = []
    pr_taus_n: list[float] = []
    for flip in noises:
        taus_r, taus_n = run_seeds(n, n_seeds, base, n_pair, float(flip), eps, power_iter, tol, teleport)
        entry = {
            "noise_flip_ratio": float(flip),
            "mean_tau_romvi": float(np.mean(taus_r)),
            "mean_tau_netwins": float(np.mean(taus_n)),
            "h3_romvi_better_or_tie": float(np.mean(taus_r)) >= float(np.mean(taus_n)),
        }
        sweep.append(entry)
        if abs(float(flip) - primary_flip) < 1e-9:
            primary_entry = entry
            pr_taus_r, pr_taus_n = taus_r, taus_n
    if primary_entry is None:
        primary_entry = sweep[0]
        pr_taus_r, pr_taus_n = run_seeds(
            n, n_seeds, base, n_pair, float(primary_entry["noise_flip_ratio"]), eps, power_iter, tol, teleport
        )

    summary = {
        "hypothesis": "H3",
        "mean_tau_romvi": primary_entry["mean_tau_romvi"],
        "mean_tau_netwins": primary_entry["mean_tau_netwins"],
        "std_tau_romvi": float(np.std(pr_taus_r)),
        "std_tau_netwins": float(np.std(pr_taus_n)),
        "h3_romvi_better_or_tie": primary_entry["h3_romvi_better_or_tie"],
        "seeds": n_seeds,
        "noise_sweep": sweep,
        "h3_any_noise_romvi_wins": any(x["h3_romvi_better_or_tie"] for x in sweep),
    }
    out = ROOT / p["output"]["result_json"]
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
