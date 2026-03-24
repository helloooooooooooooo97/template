# 阶段 4：假设回看与成稿说明（flowtest）

本文档依据 `flowtest/experiment/*/result.json` 与 `report.md`，对照 `flowtest/pipeline.md` 中 **H1–H3**。

---

## 1. 假设判定

| 假设 | 判定 | 依据 |
|------|------|------|
| **H1** | **成立** | `lab_1`：多种子下 Pairwise 的 mean τ 与 mean 分档 Acc 均高于 Pointwise（合成）。 |
| **H2** | **条件成立** | `lab_2`：在固定锚点预算与当前 `params.json5`（含 `propagate_score_band`、较低 `propagation_derive_flip`）下，`mean_tau_propagate` > `mean_tau_random`；幅度小、依赖超参。 |
| **H3** | **不成立（本代理）** | `lab_3`：Rank-centrality 式幂迭代在 0.12/0.28/0.45 翻转比例下 τ 均低于净胜场；需与论文 ROMVI 定义对齐后再验。 |

---

## 2. Pipeline 可写性与断裂点

- **可连贯撰写**：S1→S2（Pairwise 动机）→S3（Top-K 传播在受控条件下小幅提升 τ）均有实验支撑（H1/H2）。
- **断裂点**：S4 若以当前 `lab_3` 为唯一证据，**不宜**声称「ROMVI 一定优于简单聚合」；`flowtest/paper.md` 已弱化为「待与全文矩阵定义对齐的谱型后处理」。

---

## 3. 论文初稿位置

- 与本工作流对齐的精简稿：`flowtest/paper.md`。
- 若与 `idea/paper.md` 合并，需**显式修订**实验节与 ROMVI 声明，使其与 `lab_3` 结果不矛盾，或补充与论文定义一致的复现实验。

---

## 4. 完成标准自检

- [x] 结论与 `result.json` / `report.md` 可追溯一致。
- [x] `paper.md` 已标注 H3 风险与合成局限；未宣称 H3 已证实。
