"""
Lab1: 采样级别对 ROMVI 算法的影响 (N=1000)
对比不同采样密度下 Pointwise、ROMVI-Base、ROMVI-Plus 的 Kendall's τ 与性能开销
所有超参数从 params.json5 读取，可视化全部结果
"""
import json
import json5
import time
import numpy as np
from pathlib import Path
from itertools import combinations
from scipy.stats import kendalltau
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


def load_params(path="params.json5"):
    with open(Path(__file__).parent / path, encoding="utf-8") as f:
        return json5.load(f)


def build_sampled_M(n_fields, gt_scores, pairs, noise_rate, rng):
    """根据采样的 pairs 构建偏好矩阵 M"""
    M = np.zeros((n_fields, n_fields))
    for i, j in pairs:
        is_correct = rng.random() > noise_rate
        if (gt_scores[i] > gt_scores[j]) == is_correct:
            M[i, j] += 1.0
        else:
            M[j, i] += 1.0
    return M


def build_M_with_anchors(n_fields, gt_scores, pairs, noise_rate, anchor_indices, rng, anchor_weight):
    """ROMVI-Plus: 采样矩阵 + 锚点无噪比较"""
    M = build_sampled_M(n_fields, gt_scores, pairs, noise_rate, rng)
    for i in range(n_fields):
        for a in anchor_indices:
            if i == a:
                continue
            if gt_scores[i] > gt_scores[a]:
                M[i, a] += anchor_weight
            else:
                M[a, i] += anchor_weight
    return M


def romvi_power_iteration(M, max_iter, alpha, tol):
    """ROMVI 幂迭代"""
    n = M.shape[0]
    row_sums = M.sum(axis=1)
    row_sums[row_sums == 0] = 1.0
    M_norm = M / row_sums[:, None]
    M_smooth = alpha * M_norm + (1 - alpha) / n
    v = np.ones(n) / n
    for _ in range(max_iter):
        v_next = M_smooth.T @ v
        v_next /= v_next.sum()
        if np.abs(v_next - v).sum() < tol:
            break
        v = v_next
    return v

def run_experiment(params):
    """运行多采样级别实验"""
    n_fields = params["n_fields"]
    noise_rate = params["noise_rate"]
    n_trials = params["n_trials"]
    rng_seed = params["rng_seed"]
    pw_scale = params["pointwise"]["noise_scale"]
    romvi = params["romvi"]
    romvi_plus = params["romvi_plus"]
    levels = params["sampling_levels"]

    full_pairs = n_fields * (n_fields - 1) // 2
    gt_scores = np.linspace(0, 1, n_fields)
    anchor_indices = np.linspace(0, n_fields - 1, romvi_plus["n_anchors"], dtype=int)
    rng = np.random.default_rng(rng_seed)

    results = []
    all_pairs = list(combinations(range(n_fields), 2))

    for level in levels:
        name = level["name"]
        n_pairs = min(level["n_pairs"], full_pairs)
        tau_pw_list, tau_base_list, tau_plus_list = [], [], []

        time_pw_list, time_base_list, time_plus_list = [], [], []
        n_anchors = len(anchor_indices)
        n_calls_plus = n_pairs + n_fields * n_anchors  # 采样 + 锚点比较

        for trial in range(n_trials):
            chosen = rng.choice(len(all_pairs), size=n_pairs, replace=False)
            pairs = [all_pairs[i] for i in chosen]

            # Pointwise
            t0 = time.perf_counter()
            pw_noise = (rng.random(n_fields) - 0.5) * pw_scale
            pw_scores = np.clip(gt_scores + pw_noise, 0, 1)
            tau_pw, _ = kendalltau(gt_scores, pw_scores)
            time_pw_list.append(time.perf_counter() - t0)
            tau_pw_list.append(tau_pw)

            # ROMVI-Base
            t0 = time.perf_counter()
            M_base = build_sampled_M(n_fields, gt_scores, pairs, noise_rate, rng)
            v_base = romvi_power_iteration(
                M_base, romvi["max_iter"], romvi["alpha"], romvi["tol"]
            )
            tau_base, _ = kendalltau(gt_scores, v_base)
            time_base_list.append(time.perf_counter() - t0)
            tau_base_list.append(abs(tau_base))

            # ROMVI-Plus
            t0 = time.perf_counter()
            M_plus = build_M_with_anchors(
                n_fields, gt_scores, pairs, noise_rate,
                anchor_indices, rng, romvi_plus["anchor_weight"]
            )
            v_plus = romvi_power_iteration(
                M_plus, romvi["max_iter"], romvi["alpha"], romvi["tol"]
            )
            tau_plus, _ = kendalltau(gt_scores, v_plus)
            time_plus_list.append(time.perf_counter() - t0)
            tau_plus_list.append(abs(tau_plus))

        results.append({
            "level": name,
            "p_percent": level["p_percent"],
            "n_pairs": n_pairs,
            "n_calls_pw": n_fields,
            "n_calls_base": n_pairs,
            "n_calls_plus": n_calls_plus,
            "tau_pw": float(np.mean(tau_pw_list)),
            "tau_base": float(np.mean(tau_base_list)),
            "tau_plus": float(np.mean(tau_plus_list)),
            "tau_pw_std": float(np.std(tau_pw_list)),
            "tau_base_std": float(np.std(tau_base_list)),
            "tau_plus_std": float(np.std(tau_plus_list)),
            "time_pw_s": float(np.mean(time_pw_list)),
            "time_base_s": float(np.mean(time_base_list)),
            "time_plus_s": float(np.mean(time_plus_list)),
        })

    return results


def visualize(results, params):
    """生成全部可视化图表"""
    out_dir = Path(__file__).parent / params["output"]["figures_dir"]
    out_dir.mkdir(exist_ok=True)

    levels = [r["level"] for r in results]
    x = np.arange(len(levels))
    width = 0.25

    # 1. 主结果柱状图：三种方法在不同采样级别下的 Kendall's τ
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars1 = ax1.bar(x - width, [r["tau_pw"] for r in results], width, label="Pointwise", color="#2ecc71")
    bars2 = ax1.bar(x, [r["tau_base"] for r in results], width, label="ROMVI-Base", color="#3498db")
    bars3 = ax1.bar(x + width, [r["tau_plus"] for r in results], width, label="ROMVI-Plus", color="#e74c3c")
    ax1.set_ylabel("Kendall's τ")
    ax1.set_xlabel("采样级别")
    ax1.set_title("不同采样级别下三种方法的 Kendall's τ 对比 (N=1000, 20% 噪声)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(levels)
    ax1.legend()
    ax1.set_ylim(0, 1.05)
    ax1.grid(axis="y", alpha=0.3)
    fig1.tight_layout()
    fig1.savefig(out_dir / "01_bar_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig1)

    # 2. 折线图：Kendall's τ vs 采样密度
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    n_pairs = [r["n_pairs"] for r in results]
    ax2.plot(n_pairs, [r["tau_pw"] for r in results], "o-", label="Pointwise", color="#2ecc71", linewidth=2)
    ax2.plot(n_pairs, [r["tau_base"] for r in results], "s-", label="ROMVI-Base", color="#3498db", linewidth=2)
    ax2.plot(n_pairs, [r["tau_plus"] for r in results], "^-", label="ROMVI-Plus", color="#e74c3c", linewidth=2)
    ax2.set_xlabel("实际 Pairwise 询问数")
    ax2.set_ylabel("Kendall's τ")
    ax2.set_title("Kendall's τ 随采样密度变化趋势")
    ax2.legend()
    ax2.set_ylim(0, 1.05)
    ax2.grid(alpha=0.3)
    ax2.set_xscale("log")
    for i, r in enumerate(results):
        ax2.annotate(f"{r['n_pairs']/1000:.0f}k", (r["n_pairs"], r["tau_plus"]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out_dir / "02_line_trend.png", dpi=150, bbox_inches="tight")
    plt.close(fig2)

    # 3. 带误差棒的柱状图
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    pw_means = [r["tau_pw"] for r in results]
    base_means = [r["tau_base"] for r in results]
    plus_means = [r["tau_plus"] for r in results]
    pw_stds = [r["tau_pw_std"] for r in results]
    base_stds = [r["tau_base_std"] for r in results]
    plus_stds = [r["tau_plus_std"] for r in results]
    ax3.bar(x - width, pw_means, width, yerr=pw_stds, label="Pointwise", color="#2ecc71", capsize=3)
    ax3.bar(x, base_means, width, yerr=base_stds, label="ROMVI-Base", color="#3498db", capsize=3)
    ax3.bar(x + width, plus_means, width, yerr=plus_stds, label="ROMVI-Plus", color="#e74c3c", capsize=3)
    ax3.set_ylabel("Kendall's τ")
    ax3.set_xlabel("采样级别")
    ax3.set_title("Kendall's τ 对比（含 n_trials 标准差）")
    ax3.set_xticks(x)
    ax3.set_xticklabels(levels)
    ax3.legend()
    ax3.set_ylim(0, 1.1)
    ax3.grid(axis="y", alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(out_dir / "03_bar_with_error.png", dpi=150, bbox_inches="tight")
    plt.close(fig3)

    # 4. 热力图：采样级别 × 方法
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    data = np.array([
        [r["tau_pw"] for r in results],
        [r["tau_base"] for r in results],
        [r["tau_plus"] for r in results],
    ])
    im = ax4.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)
    ax4.set_xticks(np.arange(len(levels)))
    ax4.set_xticklabels(levels)
    ax4.set_yticks([0, 1, 2])
    ax4.set_yticklabels(["Pointwise", "ROMVI-Base", "ROMVI-Plus"])
    for i in range(3):
        for j in range(len(levels)):
            ax4.text(j, i, f"{data[i, j]:.3f}", ha="center", va="center", fontsize=11)
    ax4.set_title("Kendall's τ 热力图")
    fig4.colorbar(im, ax=ax4, label="Kendall's τ")
    fig4.tight_layout()
    fig4.savefig(out_dir / "04_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig4)

    # 5. 采样比例 vs τ（按 p_percent 排序）
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    p_percent = [r["p_percent"] * 100 for r in results]
    ax5.plot(p_percent, pw_means, "o-", label="Pointwise", color="#2ecc71")
    ax5.plot(p_percent, base_means, "s-", label="ROMVI-Base", color="#3498db")
    ax5.plot(p_percent, plus_means, "^-", label="ROMVI-Plus", color="#e74c3c")
    ax5.set_xlabel("采样比例 (%)")
    ax5.set_ylabel("Kendall's τ")
    ax5.set_title("Kendall's τ 随采样比例变化")
    ax5.legend()
    ax5.set_ylim(0, 1.05)
    ax5.grid(alpha=0.3)
    fig5.tight_layout()
    fig5.savefig(out_dir / "05_sampling_ratio.png", dpi=150, bbox_inches="tight")
    plt.close(fig5)

    # 6. 汇总表格图
    fig6, ax6 = plt.subplots(figsize=(12, 4))
    ax6.axis("off")
    table_data = [
        [r["level"] for r in results],
        [f"{r['n_pairs']:,}" for r in results],
        [f"{r['tau_pw']:.4f}" for r in results],
        [f"{r['tau_base']:.4f}" for r in results],
        [f"{r['tau_plus']:.4f}" for r in results],
    ]
    col_labels = ["采样级别", "实际询问数", "Pointwise τ", "ROMVI-Base τ", "ROMVI-Plus τ"]
    table = ax6.table(
        cellText=table_data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colColours=["#ecf0f1"] * 5,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    ax6.set_title("实验结果汇总表", fontsize=14, pad=20)
    fig6.tight_layout()
    fig6.savefig(out_dir / "06_summary_table.png", dpi=150, bbox_inches="tight")
    plt.close(fig6)

    # 7. 运行时间对比（秒）
    fig7, ax7 = plt.subplots(figsize=(10, 5))
    x7 = np.arange(len(levels))
    w7 = 0.25
    ax7.bar(x7 - w7, [r["time_pw_s"] for r in results], w7, label="Pointwise", color="#2ecc71")
    ax7.bar(x7, [r["time_base_s"] for r in results], w7, label="ROMVI-Base", color="#3498db")
    ax7.bar(x7 + w7, [r["time_plus_s"] for r in results], w7, label="ROMVI-Plus", color="#e74c3c")
    ax7.set_xticks(x7)
    ax7.set_xticklabels(levels)
    ax7.set_ylabel("运行时间 (秒)")
    ax7.set_xlabel("采样级别")
    ax7.set_title("各方法运行时间对比 (单 trial 均值)")
    ax7.legend()
    ax7.grid(axis="y", alpha=0.3)
    fig7.tight_layout()
    fig7.savefig(out_dir / "07_runtime.png", dpi=150, bbox_inches="tight")
    plt.close(fig7)

    # 8. 质量-开销权衡：Kendall's τ vs LLM 询问数
    fig8, ax8 = plt.subplots(figsize=(9, 6))
    n_calls_pw = results[0]["n_calls_pw"]
    mean_tau_pw = np.mean([r["tau_pw"] for r in results])
    ax8.scatter(n_calls_pw, mean_tau_pw, s=120, marker="o", label="Pointwise", color="#2ecc71", zorder=3)
    ax8.plot([r["n_calls_base"] for r in results], [r["tau_base"] for r in results], "s-", label="ROMVI-Base", color="#3498db", linewidth=2, markersize=8)
    ax8.plot([r["n_calls_plus"] for r in results], [r["tau_plus"] for r in results], "^-", label="ROMVI-Plus", color="#e74c3c", linewidth=2, markersize=8)
    ax8.axvline(n_calls_pw, color="#2ecc71", linestyle="--", alpha=0.4)
    ax8.set_xlabel("LLM 询问数 (Pairwise 等价)")
    ax8.set_ylabel("Kendall's τ")
    ax8.set_title("排序质量 vs 调用开销 (Pointwise 固定 1000 次)")
    ax8.legend()
    ax8.set_xscale("log")
    ax8.set_ylim(0, 1.05)
    ax8.grid(alpha=0.3)
    fig8.tight_layout()
    fig8.savefig(out_dir / "08_quality_cost.png", dpi=150, bbox_inches="tight")
    plt.close(fig8)

    # 9. 性能汇总表（含时间与询问数）
    fig9, ax9 = plt.subplots(figsize=(14, 5))
    ax9.axis("off")
    perf_table = [
        [r["level"] for r in results],
        [f"{r['n_calls_pw']:,}" for r in results],
        [f"{r['n_calls_base']:,}" for r in results],
        [f"{r['n_calls_plus']:,}" for r in results],
        [f"{r['time_pw_s']:.4f}s" for r in results],
        [f"{r['time_base_s']:.4f}s" for r in results],
        [f"{r['time_plus_s']:.4f}s" for r in results],
    ]
    perf_cols = ["采样级别", "PW 询问数", "Base 询问数", "Plus 询问数", "PW 时间", "Base 时间", "Plus 时间"]
    tbl = ax9.table(
        cellText=perf_table,
        colLabels=perf_cols,
        loc="center",
        cellLoc="center",
        colColours=["#ecf0f1"] * 7,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.1, 2)
    ax9.set_title("性能开销汇总", fontsize=14, pad=20)
    fig9.tight_layout()
    fig9.savefig(out_dir / "09_perf_summary.png", dpi=150, bbox_inches="tight")
    plt.close(fig9)

    print(f"[OK] 已保存 9 张图表至 {out_dir}")


def main():
    base = Path(__file__).parent
    params = load_params()
    print("运行实验 (N={}, 噪声率={}%)...".format(params["n_fields"], params["noise_rate"] * 100))
    results = run_experiment(params)
    visualize(results, params)
    out_path = base / params["output"]["results_path"]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"params": params, "results": results}, f, ensure_ascii=False, indent=2)
    print(f"[OK] 结果已保存至 {out_path}")
    print("\n排序质量 (Kendall's τ):")
    print(f"{'采样级别':<10} {'询问数':<10} {'Pointwise':<10} {'ROMVI-Base':<10} {'ROMVI-Plus':<10}")
    print("-" * 52)
    for r in results:
        print(f"{r['level']:<10} {r['n_pairs']:<10} {r['tau_pw']:<10.4f} {r['tau_base']:<10.4f} {r['tau_plus']:<10.4f}")
    print("\n性能开销 (秒/trial):")
    print(f"{'采样级别':<10} {'Pointwise':<12} {'ROMVI-Base':<12} {'ROMVI-Plus':<12}")
    print("-" * 48)
    for r in results:
        print(f"{r['level']:<10} {r['time_pw_s']:<12.4f} {r['time_base_s']:<12.4f} {r['time_plus_s']:<12.4f}")


if __name__ == "__main__":
    main()
