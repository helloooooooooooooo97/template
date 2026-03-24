---
name: hypothesis-experiment-lab
description: 针对待检验假设生成实验目录：在 experiment/ 下创建 lab_{草稿slug}_{实验slug}，内含实验设计 Markdown、可运行代码、同目录 requirements.txt（或等价清单），以及独立的 params.json5 便于对照与扫参；Agent 须在每个 lab 目录内单独建环境并安装依赖后再运行。在用户要验证假设、设计实验、生成实验代码、json5 参数文件、实验环境或提到 lab_ 命名时使用。
---

# 假设驱动的实验（lab 目录）

## 目标

为**单条或多条假设**产出可执行的实验包：**实验设计文档 + 代码 + `params.json5`**，统一放在仓库的 `experiment/` 下，目录名严格遵循：

```text
lab_{草稿名称slug}_{实验名称slug}
```

其中 `草稿名称slug`、`实验名称slug` 均为**小写字母、数字、连字符**（将用户给定中文或短语转写为 ASCII slug，如 `romvi-sampling`、`sparse-pairs`）。**禁止空格与路径非法字符**。

## 每实验目录内必备文件

| 文件 | 说明 |
|------|------|
| `design.md` | 实验设计，结构见 [experiment-design-template.md](experiment-design-template.md) |
| `params.json5` | **全部可调超参、路径、随机种子、输出配置**；支持 `//` 与 `/* */` 注释，便于对照实验与批跑 |
| 依赖清单 | **Python**：同目录 `requirements.txt`（**每个 lab 一份**，列全量直接依赖与建议版本下界）。**其他语言**：等价清单（如 `package.json`、`environment.yml`）并在 `design.md` 写明安装命令 |
| 代码入口 | 默认 `run.py`（Python）；若用户指定其他语言，使用对应入口文件名并在 `design.md` 中写明 |

**约束**：业务上需要对照的数值、路径、轮次、阈值等应放在 `params.json5`，代码中**避免**重复硬编码（仅允许与参数无关的常量或极短算法片段）。

## 每个实验独立环境（Agent 必须执行）

**原则**：**一个 `lab_*` 对应一套可复现的运行环境**，与仓库内其他 lab、与用户全局 Python 解耦。Agent **不得**在未安装依赖的情况下假定「环境已就绪」；也**不得**只在一个共享目录装依赖却不在文档中写明（除非用户明确要求「仅此一处 requirements」并在该实验 `design.md` 中引用路径）。

**Agent 对每个实验目录必须做到**：

1. **建环境**：在该 `lab_*` 目录下创建隔离环境（推荐 `python -m venv .venv`，或 `uv venv` / Conda 等，与 `design.md`「环境」一致）。
2. **装依赖**：使用该环境的解释器执行 `pip install -r requirements.txt`（或清单对应的 install 命令），**工作目录为该 `lab_*` 根目录**。
3. **再运行**：在同一环境中执行入口脚本（如 `python run.py` 或项目约定的 `code.py`），生成 `result.json` / 图表；若失败，根据报错补齐依赖或修正版本并**写回** `requirements.txt` 与 `design.md`。
4. **写进文档**：在 `design.md` 的「数据与可重复性 → 环境」中给出**可复制的一小段命令**（创建 venv、激活、安装、运行），便于人类与后续 Agent 重跑。

**例外（需显式说明）**：若多个 lab **故意**共用同一份上级 `requirements.txt`，须在**每个**相关 lab 的 `design.md` 中写明路径（如 `../../requirements.txt`）及安装命令；Agent 仍须对该实验执行一次安装步骤以验证可运行。

## 参数与代码

- **JSON5**：Python 使用 `json5` 库（`pip install json5`）读取；其他语言选用等价 JSON5 解析器并在 `design.md` 的「环境」中列出。
- **对照测试**：多组配置优先用 `params.json5` 内**数组**或**命名对象**（如 `variants: [{...}, {...}]`），代码循环或 CLI 选择 variant；必要时可额外提供 `params.baseline.json5` 等**同级**文件，但须在 `design.md` 说明主文件仍为 `params.json5` 或二者关系。
- **输出**：结果路径、图表目录等建议集中在 `params.json5` 的 `output` 对象中。

## 工作流

1. **对齐假设**：确认假设陈述、通过/不通过判据、与待验证草稿（若有）中的假设编号一致；不清楚时先 **3–7 条**追问。
2. **命名**：与用户确认或推断 `草稿名称slug`、`实验名称slug`，得到目录 `experiment/lab_{草稿名称slug}_{实验名称slug}/`。
3. **写 `design.md`**：按模板填写目的、变量、数据、步骤、判据、风险、产物说明。
4. **写 `params.json5`**：字段名语义化，关键项用注释说明单位与推荐扫参范围。
5. **写代码与依赖清单**：从 `params.json5` 加载配置；主流程可读；失败时给出可操作的错误信息；**在本 lab 目录**放置 `requirements.txt`（Python）或等价清单，**勿依赖未列出的隐式全局包**。
6. **建环境并跑通（本实验）**：进入该 `lab_*` 目录，按上文「每个实验独立环境」创建 venv、安装依赖、运行入口脚本，确认能产出 `result.json`（或设计约定的产物）；若无法联网安装，仍须把完整命令与预期报错说明写入 `design.md`。
7. **自检**：目录名符合 `lab_*_*`；存在 `design.md`、`params.json5`、入口代码、`requirements.txt`（或等价清单及文档说明）；无未说明的硬编码超参。

## 与现有 `experiment/` 的关系

仓库中可能已有旧实验目录（如 `lab1/`）。**新实验一律使用** `lab_{草稿名称slug}_{实验名称slug}`；不要重命名用户未要求的已有目录。
