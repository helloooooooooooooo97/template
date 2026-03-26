# 实验报告：lab_2（H2）

## 结论

- **H2 在当前参数下成立**：`h2_propagate_better` 为 `true`（`mean_tau_propagate` > `mean_tau_random`）。
- 操作化定义：**固定锚点预算** \(B\)（`anchor_budget`），比较「仅随机成对」与「锚点 + Top-K 派生边（带 `propagate_score_band` 过滤）」的 Kendall τ。

## 数字摘要

| 策略 | mean τ | std τ |
|------|--------|-------|
| random | 0.303 | 0.050 |
| propagate | 0.308 | 0.058 |

## 解释与局限

- 收益幅度小，且依赖 `top_k`、`propagation_derive_flip`、`propagate_score_band`；**Embedding 与真序不对齐**时传播可能劣于随机（需在真实 schema 上复验）。
- 与 pipeline 原文「更少询问」的表述对应关系：本实验验证的是**同等锚点调用下的 τ**，而非单独测「达阈所需锚点数」；若需后者应增改 `code.py` 与 `design.md`。
