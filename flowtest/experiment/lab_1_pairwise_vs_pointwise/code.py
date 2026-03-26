#!/usr/bin/env python3
"""H1: synthetic Pointwise vs Pairwise ranking quality."""
from __future__ import annotations

import json
from pathlib import Path

import json5
import numpy as np
from scipy.stats import kendalltau

ROOT = Path(__file__).resolve().parent


def load_params():
    raw = (ROOT / "params.json5").read_text(encoding="utf-8")
    return json5.loads(raw)


def true_scores(n: int, rng: np.random.Generator) -> np.ndarray:
    s = rng.uniform(0.0, 1.0, size=n)
    return s


def gold_ranks(scores: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(-scores))


def pointwise_ranks(scores: np.ndarray, noise_std: float, n_bins: int, rng: np.random.Generator) -> np.ndarray:
    n = len(scores)
    noisy = np.clip(scores + rng.normal(0, noise_std, size=n), 0.0, 1.0)
    labels = np.clip((noisy * n_bins).astype(int) + 1, 1, n_bins)
    jitter = rng.random(n) * 1e-6
    order = np.lexsort((jitter, -labels))
    return np.argsort(order)


def pairwise_ranks(
    scores: np.ndarray,
    n_samples: int,
    flip_p: float,
    rng: np.random.Generator,
) -> np.ndarray:
    n = len(scores)
    wins = np.zeros(n, dtype=np.float64)
    for _ in range(n_samples):
        i, j = rng.integers(0, n, size=2)
        if i == j:
            continue
        si, sj = scores[i], scores[j]
        i_wins = si > sj if si != sj else rng.random() < 0.5
        if rng.random() < flip_p:
            i_wins = not i_wins
        if i_wins:
            wins[i] += 1
        else:
            wins[j] += 1
    order = np.argsort(-wins, kind="stable")
    return np.argsort(order)


def tau_and_acc(pred_rank: np.ndarray, gold: np.ndarray, n_bins: int) -> tuple[float, float]:
    t = float(kendalltau(pred_rank, gold).statistic)
    n = len(gold)
    gold_labels = np.clip((gold / max(n - 1, 1) * (n_bins - 1)).round().astype(int) + 1, 1, n_bins)
    pred_labels = np.clip((pred_rank / max(n - 1, 1) * (n_bins - 1)).round().astype(int) + 1, 1, n_bins)
    acc = float(np.mean(gold_labels == pred_labels))
    return t, acc


def main() -> None:
    p = load_params()
    out_path = ROOT / p["output"]["result_json"]
    n_items = int(p["n_items"])
    n_seeds = int(p["n_seeds"])
    base = int(p["rng_seed"])

    rows = []
    for k in range(n_seeds):
        rng = np.random.default_rng(base + k * 9973)
        scores = true_scores(n_items, rng)
        gold = gold_ranks(scores)
        pr = pointwise_ranks(
            scores,
            float(p["pointwise_noise_std"]),
            int(p["n_bins"]),
            rng,
        )
        pwr = pairwise_ranks(
            scores,
            int(p["n_pairwise_samples"]),
            float(p["pairwise_flip_prob"]),
            rng,
        )
        t_p, a_p = tau_and_acc(pr, gold, int(p["n_bins"]))
        t_w, a_w = tau_and_acc(pwr, gold, int(p["n_bins"]))
        rows.append(
            {
                "seed_offset": k,
                "pointwise": {"kendall_tau": t_p, "acc_bins": a_p},
                "pairwise": {"kendall_tau": t_w, "acc_bins": a_w},
            }
        )

    def mean(key: str, sub: str) -> float:
        return float(np.mean([r[key][sub] for r in rows]))

    summary = {
        "hypothesis": "H1",
        "n_items": n_items,
        "n_seeds": n_seeds,
        "mean_pointwise_tau": mean("pointwise", "kendall_tau"),
        "mean_pairwise_tau": mean("pairwise", "kendall_tau"),
        "mean_pointwise_acc": mean("pointwise", "acc_bins"),
        "mean_pairwise_acc": mean("pairwise", "acc_bins"),
        "h1_supports_pairwise_tau": mean("pairwise", "kendall_tau") > mean("pointwise", "kendall_tau"),
        "h1_supports_pairwise_acc": mean("pairwise", "acc_bins") > mean("pointwise", "acc_bins"),
        "runs": rows,
    }
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
