# flowtest：顺序化论文工作流（从 0 起）

本目录**镜像** `.cursor/skills/idea-paper-sequential-workflow` 的路径约定，与 `idea/` 并行，便于独立跑通全流程。

## 路径对照

| 阶段 | 本目录中的文件 |
|------|----------------|
| 1 | `flowtest/think.md` |
| 2 | `flowtest/pipeline.md` |
| 3 | `flowtest/experiment/experiment.md` 与 `flowtest/experiment/lab_*` |
| 4 | `flowtest/conclude.md`（论文成稿建议：`flowtest/paper.md`） |
| 5 | `flowtest/review.md` |

## 进度检查

```
顺序化论文写作进度（flowtest）：
- [x] flowtest/think.md：难点与现有方案边界已写清
- [x] flowtest/pipeline.md：环节、双路径、编号假设与验证思路已齐
- [x] flowtest/experiment/：各 lab_* 含 requirements.txt、result.json、report.md
- [x] flowtest/conclude.md：假设判定与 paper 对齐实验
- [x] flowtest/review.md：清单逐条回应；flowtest/paper.md 作为本线终稿
```

## 运行实验（每个 lab 独立环境）

```bash
cd flowtest/experiment/lab_1_pairwise_vs_pointwise
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python code.py

cd ../lab_2_topk_propagation_cost
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python code.py

cd ../lab_3_romvi_noise_robustness
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python code.py
```

依赖在各 `lab_*/requirements.txt`（内容一致时可复制，但**勿省略**各 lab 文件以满足技能规约）。
