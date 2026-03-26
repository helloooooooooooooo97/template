# 实验设计：H1 Pairwise vs Pointwise（合成）

## 元信息

| 字段 | 内容 |
|------|------|
| 对应假设 | **H1**：Pairwise 相对 Pointwise 更有利于恢复真实敏感序 |
| 目录 | `flowtest/experiment/lab_1_pairwise_vs_pointwise/` |

## 1. 目的

在**不调用真实 LLM**的前提下，用可控合成数据检验：在可比预算与噪声下，成对比较聚合排序是否比五级绝对标签更接近真序。

## 2. 变量与对照

- **自变量**：观测机制（Pointwise / Pairwise）、随机种子、`n_pairwise_samples`、`pairwise_flip_prob`、`pointwise_noise_std`。
- **因变量**：与金标准排序的 **Kendall τ**；五级分档后的 **Accuracy**（分位数对齐映射）。
- **控制**：同一组真分数、同一 `n_items`、重复 `n_seeds` 次取均值。
- **基线**：Pointwise 五级量化 vs Pairwise 胜负加总排序。

## 3. 数据与可重复性

- **数据**：合成一维敏感分数 → 全序即金标准。
- **随机性**：`rng_seed` 在 `params.json5`。
- **环境**：Python 3.10+；本目录 `requirements.txt`。安装与运行：

```bash
cd flowtest/experiment/lab_1_pairwise_vs_pointwise
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python code.py
```

## 4. 步骤概要

1. 生成真分数并得金标准排序。
2. 模拟 Pointwise：分数加噪后量化为 1–`n_bins`，再导出排序。
3. 模拟 Pairwise：按预算随机采样对，按真序胜负并依 `pairwise_flip_prob` 翻转，用净胜场排序。
4. 计算 τ 与分档 Acc，写入 `result.json`。

## 5. 判据

- **H1 倾向成立**：多种子下 Pairwise 的 **mean_tau** 与 **mean_acc** 均高于 Pointwise（合成设定下预期如此；若参数极端可反转，记录在 `report.md`）。

## 6. 风险与局限

- 非真实 LLM 语义；仅验证**信息论式**的「相对比较 vs 绝对档」差异。
- 未覆盖 S3 传播与 S4 ROMVI（见 H2/H3）。

## 7. 产物

- `requirements.txt`、`params.json5`、`code.py`、`result.json`、`report.md`、`figures/`（可选）
