# flowtest 实验规约

根据 `flowtest/pipeline.md` 中的 **H1–H3**，每个假设对应一个目录：

- `lab_1_pairwise_vs_pointwise`
- `lab_2_topk_propagation_cost`
- `lab_3_romvi_noise_robustness`

## 每个 `lab_*` 目录至少包含

| 文件 | 说明 |
|------|------|
| `design.md` | 假设、变量、步骤、判据 |
| `params.json5` | 全部超参（含注释）；支持扫参 |
| `requirements.txt` | **本 lab 专用**；Agent/人类在该目录 `venv` 内 `pip install -r` |
| `code.py` | 可运行入口；读 `params.json5`，写 `result.json`，可选写 `figures/` |
| `result.json` | 由代码生成，供 `conclude.md` 追溯 |
| `report.md` | 对结果与假设是否成立的简要结论 |
| `figures/` | 图表输出目录 |

## 与仓库根目录 `experiment/` 的关系

- `flowtest/experiment/` **仅服务本工作流副本**；与 `idea/` 旁路的实验目录相互独立。
- 命名遵循：`lab_{假设编号}_{实验名称}`（下划线连接，全小写）。
