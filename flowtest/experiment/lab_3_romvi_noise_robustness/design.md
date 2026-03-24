# 实验设计：H3 谱型聚合 vs 净胜场（合成）

## 元信息

| 字段 | 内容 |
|------|------|
| 对应假设 | **H3**：成对观测含噪时，谱型全局聚合比净胜场更稳 |
| 目录 | `flowtest/experiment/lab_3_romvi_noise_robustness/` |

## 1. 目的

在翻转成对胜负的噪声下，比较 **Rank-centrality 式 ROMVI 代理**（败者 → 胜者的 Markov 链 + `teleport`，对 \(P^\top\) 幂迭代）与 **净胜场** 基线的 Kendall τ。可选 `noise_flip_ratios` 扫参，见 `result.json` 中 `noise_sweep`。

## 2. 变量与对照

- **自变量**：`noise_flip_ratio`（主表）、`noise_flip_ratios`、`n_pair_samples`、`n_items`、`teleport`。
- **因变量**：`mean_tau_romvi`、`mean_tau_netwins`。
- **控制**：同一真序、同一随机种子协议。

## 3. 数据与可重复性

- **数据**：合成均匀分数与全序金标准。
- **随机性**：`rng_seed`、`n_seeds` 在 `params.json5`。
- **环境（本 lab 独立）**：

```bash
cd flowtest/experiment/lab_3_romvi_noise_robustness
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python code.py
```

## 4. 步骤概要

1. 采样 `n_pair_samples` 条有序对，据真序记胜负，得 \(W_{ij}\)（\(i\) 胜 \(j\) 的次数）。
2. 按比例翻转部分边的胜负。
3. **ROMVI 代理**：构造转移矩阵 \(P_{j,i} \propto W_{i,j}\)（自败者走向胜者），行归一并混入 `teleport`；迭代 \(\mathbf{v} \leftarrow P^\top \mathbf{v}\)（L1 归一）。
4. **Baseline**：\(\sum_j (W_{ij}-W_{ji})\) 排序。

## 5. 判据

- 若主 `noise_flip_ratio` 下 `h3_romvi_better_or_tie` 为真则直接支持 H3；否则依据 `noise_sweep` 讨论**在何噪声模型下**谱型方法可能仍值得保留（本仓库当前结果见 `report.md`）。

## 6. 风险

- 与正文「秩一 / Frobenius」叙述可能不完全同构；结论外推需统一符号与矩阵定义。

## 7. 产物

`requirements.txt`、`params.json5`、`code.py`、`result.json`、`report.md`、`figures/`
