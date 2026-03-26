# 实验设计：H2 Top-K 传播 vs 随机成对（合成）

## 元信息

| 字段 | 内容 |
|------|------|
| 对应假设 | **H2**：Top-K 相似传播在相同锚点预算下带来更高排序质量或更少锚点达阈 |
| 目录 | `flowtest/experiment/lab_2_topk_propagation_cost/` |

## 1. 目的

在 Embedding 与真分数**相关**（近邻在敏感序上亦相近）的合成设定下，比较：

- **随机基线**：每锚点预算仅记录一条随机成对结果；
- **传播策略**：每锚点除 \((i,j)\) 外，向 \(i\) 的 Top-K 近邻复制「\(i\) 对 \(j\) 的胜负」为派生边（带额外错误率）。

检验在**相同锚点数** \(B\) 下 Kendall τ 是否提升。

## 2. 变量与对照

- **自变量**：`anchor_budget`、`top_k`、`propagation_derive_flip`、`propagate_score_band`、`pair_flip_prob`、`embed_dim`。
- **因变量**：两种策略的 **Kendall τ**（相对金标准）。
- **控制**：同一真分数、同一 KNN 图、多种子。

## 3. 数据

- 真分数均匀或 Beta；Embedding 第一维对齐分数 + 各向噪声，使 KNN 语义上「相似字段」大致相邻序。

## 4. 判据

- **H2 倾向成立**：`mean_tau_propagate` > `mean_tau_random`（默认参数下）。

## 5. 风险

- 若 Embedding 与分数无关，传播会伤害 τ（应在 `report.md` 讨论）。

## 6. 环境（本 lab 独立）

```bash
cd flowtest/experiment/lab_2_topk_propagation_cost
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python code.py
```

## 7. 产物

`requirements.txt`、`params.json5`、`code.py`、`result.json`、`report.md`、`figures/`
