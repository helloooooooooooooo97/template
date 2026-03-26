# 大规模字段敏感度排序：Pairwise、语义传播与全局聚合（flowtest 精简稿）

> 本稿服务于 `flowtest` 顺序化工作流，实验仅含 **合成** 可复现 lab；与 `idea/paper.md` 并存时需手动合并并统一符号。

## 摘要

在数据治理场景下，对海量 schema 字段做敏感度排序面临绝对档不稳定与成对比较成本高的问题。本文在 **flowtest** 流水线中验证：**H1** 合成设定下 Pairwise 优于 Pointwise（Kendall τ 与分档 Acc）；**H2** 在嵌入与真分数对齐、且带分数带过滤的传播策略下，固定锚点预算时 Top-K 传播略优于纯随机成对采样；**H3** 在当前 Rank-centrality 代理实现下未优于净胜场，全文 ROMVI 叙述需与矩阵定义对齐后重验。

**关键词**：敏感度排序；Pairwise；Top-K 传播；谱聚合；合成实验

---

## 1. 引言与动机

合规要求对字段分级，Pointwise LLM 易出现边界漂移与不一致。将任务转为成对比较并做全局聚合是自然方向，但需处理 **预算** 与 **噪声**（见 `flowtest/think.md`）。

---

## 2. 方法概要（与 pipeline 一致）

1. 字段 Embedding（合成中用分数相关向量代替）。
2. **Pairwise** 或 Pointwise 获取观测（lab 用模拟器）。
3. **Top-K 传播**：锚点胜负向胜者近邻复制派生边，并用 `propagate_score_band` 抑制语义漂移。
4. **全局聚合**：基线为净胜场；**lab_3 中「ROMVI」指 Rank-centrality 式代理**（败者→胜者 Markov 链 + teleport + \(P^\top\) 幂迭代），**不等价**于 `idea/paper.md` 中未对齐实现的 Frobenius 秩一表述。

---

## 3. 实验（合成）

| 实验 | 假设 | 结论要点 |
|------|------|----------|
| `lab_1_pairwise_vs_pointwise` | H1 | τ：0.42→0.56；Acc：0.36→0.45（均值，见 `result.json`） |
| `lab_2_topk_propagation_cost` | H2 | 同等锚点预算下 τ：0.303→0.308（依赖超参） |
| `lab_3_romvi_noise_robustness` | H3 | 谱型代理 τ 低于净胜场（多噪声档） |

**可重复性**：各 lab 目录内 `python3 -m venv .venv && pip install -r requirements.txt && python code.py`。

---

## 4. 讨论

- **H3**：在修订 ROMVI 与转移矩阵构造前，实验结果支持「优先报告净胜场 / BT 等基线」，谱方法作为探索性对照。
- **外推**：真实 LLM、真实 10^5 规模与法规档位映射仍未在本目录验证。

---

## 5. 结论

Pairwise 与受控传播在合成管线中获得 **H1/H2** 支持；**H3** 在当前实现下**未**支持，后续工作应统一数学对象与实验再写主文贡献表述。
