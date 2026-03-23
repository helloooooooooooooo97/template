# Lab1 实验报告：采样级别对 ROMVI 算法的影响

**实验目标**：在 $N=1000$ 规模、20% 幻觉率下，对比不同采样级别对 Pointwise、ROMVI-Base、ROMVI-Plus 三种方法排序质量（Kendall's τ）的影响。

---

## 1. 实验配置

所有超参数定义于 `params.json5`（支持注释）：

| 参数类 | 参数 | 说明 |
|--------|------|------|
| 全局 | `n_fields` | 字段规模 1000 |
| 全局 | `noise_rate` | LLM 幻觉率 20% |
| 全局 | `n_trials` | 每级别重复 5 次 |
| Pointwise | `noise_scale` | 得分噪声幅度 0.4 |
| ROMVI | `max_iter` | 幂迭代最大步数 200 |
| ROMVI | `alpha` | 随机游走重启概率 0.98 |
| ROMVI-Plus | `n_anchors` | 锚点数量 10 |
| ROMVI-Plus | `anchor_weight` | 锚点边权重 1.0 |

采样级别定义见 `params.json5` 中 `sampling_levels`。

---

## 2. 实验结果

运行 `python3 code.py` 后，结果保存于 `results.json`，并生成以下图表（保存在 `figures/`）：

| 图表 | 文件名 | 说明 |
|------|--------|------|
| 柱状图 | `01_bar_comparison.png` | 三种方法在各采样级别下的 Kendall's τ |
| 折线图 | `02_line_trend.png` | τ 随实际询问数变化趋势（对数横轴） |
| 误差棒图 | `03_bar_with_error.png` | 带 n_trials 标准差的柱状图 |
| 热力图 | `04_heatmap.png` | 采样级别 × 方法 的 τ 矩阵 |
| 比例图 | `05_sampling_ratio.png` | τ 随采样比例 (%) 变化 |
| 汇总表 | `06_summary_table.png` | 数值结果表格 |
| **性能** | `07_runtime.png` | 各方法运行时间对比 |
| **性能** | `08_quality_cost.png` | 排序质量 vs LLM 询问数（质量-开销权衡） |
| **性能** | `09_perf_summary.png` | 性能开销汇总表（询问数 + 时间） |

---

## 3. 主要结论

### 排序质量

1. **Pointwise**：τ 稳定在 ~0.76，与采样密度无关，受单点噪声上限约束。
2. **ROMVI-Base**：τ 随采样密度单调上升，存在约 10% 的转折点，超过后显著优于 Pointwise。
3. **ROMVI-Plus**：在极稀疏场景下，锚点可提供基准校准；在数据充足时与 ROMVI-Base 接近。
4. **采样建议**：实际部署应结合 Top-K 传播与锚点，在低采样时保证鲁棒性。

### 性能开销

1. **询问数**：Pointwise 固定 $N=1000$ 次；ROMVI-Base = 采样对数；ROMVI-Plus = 采样对数 + $N \times$ 锚点数（锚点与全表比较）。
2. **运行时间**：Pointwise 最快（仅随机采样）；ROMVI 随矩阵规模与迭代次数增长，极限级（满量）最耗时。
3. **质量-开销权衡**：图 `08_quality_cost.png` 展示在相同询问预算下，Pairwise 范式通过冗余与逻辑一致性可获得更高 τ；极稀疏时需锚点校准以弥补信息不足。

### 复杂度限制

当前实现的时间与空间复杂度均为 **$O(N^2)$**（矩阵规模与满量 Pairwise 询问）。在 $N \approx 10^5$ 时，满量需约 $5 \times 10^9$ 次比较，不可行。论文提出的 **Top-K 语义相似性传播** 将询问数降至 $O(N \log N)$，通过「一比多推」在保持质量的前提下大幅降低复杂度；本实验在 $N=1000$ 小规模下验证质量与开销的权衡。

---

## 4. 复现

```bash
cd experiment/lab1 && python3 code.py
```

依赖：`numpy`, `scipy`, `matplotlib`, `json5`
