# 实验报告：lab_3（H3）

## 结论

- **H3 在本代理设定下不成立**：主噪声比 `noise_flip_ratio=0.12` 下 `mean_tau_romvi`（≈0.549）**低于** `mean_tau_netwins`（≈0.761）；`noise_sweep` 中 0.28、0.45 两档同样为净胜场更优。
- `h3_any_noise_romvi_wins` 为 `false`。

## 数字摘要（节选）

| noise_flip_ratio | mean τ (ROMVI 代理) | mean τ (net wins) |
|------------------|---------------------|-------------------|
| 0.12 | 0.549 | 0.761 |
| 0.28 | 0.434 | 0.616 |
| 0.45 | 0.136 | 0.204 |

## 解释与后续

- 当前 ROMVI 实现为 **Rank-centrality + teleport**，与 `idea/paper.md` 中 Frobenius 秩一叙述**可能不等价**；需在方法与实验对齐后重验 H3。
- 可能方向：换用与论文一致的 \(M\) 构造、BT MLE、或仅在**高度稀疏/结构噪声**体制下比较。
