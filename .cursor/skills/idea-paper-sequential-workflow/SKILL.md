---
name: idea-paper-sequential-workflow
description: 按仓库内固定顺序推进研究写作：先 idea/think.md 与 idea/pipeline.md，再按 experiment/experiment.md 落地 lab 实验，继而 idea/conclude.md 收束与成稿，最后 idea/review.md 审稿修订至终稿。在用户按模板写论文、要求按 think→pipeline→experiment→conclude→review 顺序、或整合假设—实验—论文时使用。
---

# 顺序化论文写作工作流

## 原则

- **顺序**：`idea/think.md` → `idea/pipeline.md` → `experiment/`（遵循 `experiment/experiment.md`）→ `idea/conclude.md` → `idea/review.md`。
- **不跳步**：进入下一阶段前，上一阶段的产出应已满足该阶段文件中的要求；若用户从中途介入，先**补全或确认**缺失的上游内容，再往下写。
- **单一事实源**：各阶段的具体写法与检查项以对应 Markdown 文件为准；本技能只规定**顺序、衔接关系与完成标准**。

## 阶段 1：`idea/think.md`

**目标**：把领域问题想清楚，作为后续 pipeline 的起点。

按该文件要求组织思考：

1. 领域难点在哪？
2. 目前前沿/既有方案解决了哪些难点？
3. 目前前沿/既有方案遗留了哪些难点？为什么？

**完成标准**：能明确写出「难点清单」与「现有 pipeline / 解决边界」，可直接支撑阶段 2 画流水线。

## 阶段 2：`idea/pipeline.md`

**目标**：把想法压成可验证的数据处理 pipeline 与**编号假设**。

按该文件要求：

- 总结数据处理 pipeline，**每个环节**有详细说明。
- 每个环节至少 **两种可行路径**，并写清各路径的**前提、假设、验证思路**。
- 假设以**列表 + 编号**呈现，每条有详细说明，便于阶段 3 一一对应实验。

**完成标准**：假设编号稳定、可映射到 `lab_{编号}_{实验名}`；无编号则先在阶段 2 补全后再建实验目录。

## 阶段 3：`experiment/experiment.md` 与 `experiment/` 下 lab

**目标**：为**每个假设**设计可执行验证，目录与文件结构遵循 `experiment/experiment.md`。

要点（与仓库规约一致）：

- 每个实验单独文件夹：`lab_{假设编号}_{实验名称}`。
- 至少包含：`design.md`、`params.json5`、`code.py`（或 `code/`）、`result.json`、`report.md`、`figures/`。
- **环境与可运行性**：每个 `lab_*` **单独**具备依赖清单（如 `requirements.txt`）；Agent **须在该 lab 目录内**创建/使用隔离环境、安装依赖后再运行代码生成结果（详见技能 `hypothesis-experiment-lab` 中「每个实验独立环境」），不得默认「全局已装好」。

**落地时**：读取并遵循项目技能 `hypothesis-experiment-lab`（`lab_` 命名、模板、扫参习惯、**每实验建环境并安装依赖**）。

**完成标准**：每个待验假设都有对应实验设计或可解释的「暂不实验」决策（若用户明确缩小范围，须在文档中写明范围与风险）。

## 阶段 4：`idea/conclude.md`

**目标**：根据实验结果回看 pipeline 假设，判断成立与否，并给出分析与理由。

- 若能构成**完整 pipeline**：基于该 pipeline 与既有资料，写出**标准格式论文**；项目内成稿位置一般为 `idea/paper.md`（体例可对照 `idea-paper-codevelopment` 与 `paper-structure-reference.md`）。
- 若假设链断裂：仍按该文件要求写清**哪些成立/不成立**及原因，并说明论文可写部分与缺口。

**完成标准**：结论与 `report.md` / `result.json` 一致可追溯；论文结构完整或明确标注未完成块。

## 阶段 5：`idea/review.md`

**目标**：对照论文全文做结构化审稿，修订直至可定终稿。

必须覆盖该文件中列出的主问题与「其他需要检查」各类项（动机、方法、实验、泛化、贡献、表达等）。

**流程**：发现问题 → **修改论文（及相关结论/实验表述若需一致）** → 再审；无问题或修订完成后，输出**终稿**（仍以 `idea/paper.md` 或用户指定的终稿路径为准）。

**完成标准**：对审查清单中的每一项有简要判断与理由；终稿与实验、结论无矛盾。

## 与其他技能的分工

| 阶段 | 可协同技能 |
|------|------------|
| 2 | `idea-pipeline-draft`（与 pipeline/假设草稿高度重叠时可参考其输出模板） |
| 3 | `hypothesis-experiment-lab`（建 lab、design/params/code） |
| 4–5 | `idea-paper-codevelopment`（追问、文献、按 `idea/paper.md` 体例扩展） |

## 进度检查（可复制）

```
顺序化论文写作进度：
- [ ] idea/think.md：难点与现有方案边界已写清
- [ ] idea/pipeline.md：环节、双路径、编号假设与验证思路已齐
- [ ] experiment/：各 lab_* 符合 experiment.md；result/report 与假设对应
- [ ] idea/conclude.md：假设判定与（若可）论文初稿已对齐实验
- [ ] idea/review.md：清单逐条回应；修订后终稿已定
```

## 额外说明

- 需要**网上核实**的论断：在阶段 2–4 按需检索；引用须可核验，禁止编造链接（与 `idea-pipeline-draft` 一致）。
- 用户若要求只写某一阶段，仍应**快速核对**上游文件是否足以支撑，避免逻辑断链。
