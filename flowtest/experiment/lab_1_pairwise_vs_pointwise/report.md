# 实验报告：lab_1（H1）

## 结论

- **H1 成立**（合成设定）：`h1_supports_pairwise_tau` 与 `h1_supports_pairwise_acc` 均为 `true`。
- Pairwise 在 **Kendall τ** 与 **五级分档 Acc** 上均优于 Pointwise。

## 数字摘要（`result.json`）

| 指标 | Pointwise | Pairwise |
|------|-----------|----------|
| mean Kendall τ | 0.422 | 0.562 |
| mean Acc（分档） | 0.364 | 0.453 |

- `n_items=80`，`n_seeds=20`，详见同目录 `result.json` 中 `runs`。

## 解释与局限

- 未调用真实 LLM；Pairwise 侧使用净胜场排序，与全文「BT + ROMVI」完整管线仍有差距。
- Pointwise 与 Pairwise 的「调用预算」可比性为近似（80 次档观测 vs 400 条成对采样），正式论文需统一预算口径。
