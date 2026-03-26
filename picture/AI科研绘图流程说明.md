# AI 科研绘图流程说明

本文档描述一套可复用的操作流程：先用大语言模型根据论文生成「顶刊风格」科研插图提示词，再在支持绘图的模型中生成图片。按相同步骤即可适配其他领域与论文。

---

## 流程总览

| 阶段          | 工具                                             | 目的                                                  |
| ------------- | ------------------------------------------------ | ----------------------------------------------------- |
| 1. 提示词生成 | [ChatGPT](https://chatgpt.com/)                  | 识别论文领域，并输出可直接用于生图的英文/中文长提示词 |
| 2. 图片生成   | [Gemini](https://gemini.google.com/)（绘图模式） | 将提示词转为插图；可对比免费版与付费版效果            |

---

## 第一步：提示词生成（ChatGPT）

### 1.1 打开网站并新建对话

1. 打开：<https://chatgpt.com/>
2. 开启**新对话**。
3. **上传论文**（PDF 或可读附件，视情况而定）。

### 1.2 让模型判断领域

在对话中发送（可按需微调表述）：

```text
这是一篇论文，告诉我这是哪个领域的文章？
```

根据回复确认领域（例如：生命科学机制图、计算机/数据治理方法示意图等），便于后续提示词贴合该领域习惯。

**示例：** 判定`idea/paper.md`主题为数据治理与数据安全交叉（字段敏感度分级等），方法上涉及 LLM、排序学习与一致性/谱类修正；一句话可概括为「面向大规模数据库字段敏感度分级，融合大语言模型与排序学习」——具体表述以你当次对话为准。

### 1.3 请求「科研绘图设计师」式提示词

继续在同一对话中发送：

```text
你现在是一名经验丰富的科研绘图设计师，请你仔细阅读我提供的文献，理解研究内容和摘要结论等，出具一段当前领域用于绘图的提示词。
```

说明：

- 可要求模型同时给出**英文版**与**中文版**。
- 若初版过于笼统，可追加约束，例如：多分面板（A/B/C…）、白底、矢量感、Nature/Cell 风格、避免论文未支持的臆测内容等。

### 1.4（可选）通用英文模板，用于「跨领域」或加强约束

若希望模型在**不确定插图类型**时仍给出统一高质量结构，可将下面整段作为参考或附件说明，让 ChatGPT **结合你的论文改写**，而不是原样照搬：

```text
Imagine a publication-quality scientific figure that infers the dominant figure type from the provided scientific context (e.g., mechanism, workflow, pathway, or experimental design). The figure should highlight biologically or experimentally central genes, proteins, complexes, domains, cellular compartments, interactions, and relevant parameters (e.g., temperature, time points, MOI, dosage, n), prioritizing clarity and mechanistic coherence while avoiding unsupported or speculative elements. Causal directionality should be explicit, and visual encoding consistent across panels. Apply a colorblind-friendly color logic consistent with Nature-family journals, assigning colors by functional role or biological state and using neutral tones for structural elements. The visual style should benchmark Nature / Cell, with clean professional typography and clear spatial organization. Output on a white background, legible at single-column width, at journal-ready high resolution, with modular panels compatible with Adobe Illustrator.
```

注意：该模板偏「生物/实验」语境；若论文属于**计算机、数据治理、AI 方法**等，务必让 ChatGPT 参考此提示将提示词修改为第一个对话中当前领域的内容。

---

## 第二步：图片生成（Gemini）

### 2.1 打开绘图能力

1. 打开：<https://gemini.google.com/>
2. 切换到**图像生成**相关模式。
3. 将 ChatGPT 输出的提示词**完整粘贴**到输入框（优先使用与界面语言一致的版本，或尝试英中不同效果）。

### 2.2 迭代建议

- 若构图拥挤：要求「减少文字密度」「Panel 数量不变但每块更留白」。
- 若风格不对：明确写「Nature-style schematic, flat vector, no 3D render」等。
- 终稿通常在 **Adobe Illustrator** 中做字体、线宽与标注统一；生成阶段以「模块化、可拆分」为主即可。

### 2.3 免费版与付费版对比（本仓库示例）

在同一提示词下，当前分别用**免费**与**付费**能力各生成一版，可在此对比细节、一致性与可用性。

生成图片在本目录下 **`example/`** 中文件夹：

| 文件             | 建议含义                |
| ---------------- | ----------------------- |
| `English.png`    | 英文提示词 + 免费版生图 |
| `EnglishPro.png` | 英文提示词 + 付费版生图 |
| `Chinese.png`    | 中文提示词 + 免费版生图 |
| `ChinesePro.png` | 中文提示词 + 付费版生图 |

---

## 附录：案例参考（数据库字段敏感度 / Pairwise 排序方法总览图）

以下为本流程一次完整跑通时，ChatGPT 给出的**英文**与**中文**长提示词示例，主题：**大规模数据库字段敏感度分级、Pairwise 排序、Top-K 语义传播、ROMVI 全局一致性、证据链与结果面板**。其他课题请仅在 ChatGPT 步骤中重新生成，勿机械套用具体 Panel 内容。

### 附录 A — 英文提示词（示例）

```text
Imagine a publication-quality scientific figure for a computer science / data governance paper, designed as a high-end Nature-style methodological overview schematic on a white background.

The figure should infer the dominant figure type as a multi-panel workflow-and-mechanism diagram. It should visually explain a large-scale database field sensitivity ranking framework based on Pairwise comparison, Top-K semantic propagation, and ROMVI-based global consistency correction.

Panel A: Problem setting and motivation.
Show a large database schema containing many heterogeneous fields (for example: user_id, phone, zipcode, address, purchase_history, diagnosis_code, device_id), with sensitivity levels L1–L5 represented as an ordered scale.
Visually contrast the weakness of Pointwise classification versus Pairwise ranking:
- Pointwise branch: isolated field-by-field classification, unstable level assignment, semantic boundary drift, hallucinated inconsistency.
- Pairwise branch: relative comparison between two fields, clearer semantic judgment, stronger stability.
Include small visual examples of inconsistent Pointwise outputs on semantically similar fields.

Panel B: Pairwise ranking formulation.
Show two database fields entering an LLM comparator that outputs a directional preference such as "field A is more sensitive than field B".
Represent the Bradley–Terry style preference probability conceptually, with elegant mathematical annotation:
P(fi ≻ fj) or a score difference / latent sensitivity score.
Use arrows to indicate causal directionality and explicit ranking flow.

Panel C: Top-K semantic similarity propagation.
Show each field embedded into a semantic vector space, with nearest-neighbor clusters or a similarity graph.
Highlight a Top-K neighborhood around one field and show how one trusted pairwise decision propagates to semantically similar fields.
Make the reduction in comparison burden visually explicit:
from dense all-to-all comparisons O(N^2) to sparse propagated comparisons O(N log N).
Emphasize semantic constraint, similarity threshold, and controlled propagation to avoid semantic drift.

Panel D: Global consistency correction with ROMVI.
Show a noisy pairwise comparison matrix or directed comparison graph containing cyclic contradictions (A > B, B > C, C > A).
Then show ROMVI / rank-one projection transforming the noisy inconsistent matrix into a globally coherent ranking vector.
Include visual motifs for Perron–Frobenius principal eigenvector, rank-one consistency, denoising, and conflict resolution.
The transition should make clear that local noisy judgments are projected into a globally self-consistent latent sensitivity score vector.

Panel E: Explainability and evidence chain.
Show a DAG-like evidence chain from lower-sensitivity anchor fields to higher-sensitivity anchor fields.
Illustrate how a queried field's final level can be explained by:
- which lower-level anchors it outranks,
- which higher-level anchors outrank it,
- and the topological path supporting its final sensitivity assignment.
This panel should emphasize auditability, interpretability, compliance-readiness, and causal evidence tracing.

Panel F: Main results and practical value.
Summarize the reported advantages in a compact result panel with clean chart-like or badge-like visual elements:
- Pairwise + ROMVI outperforms Pointwise in Kendall's tau and accuracy,
- robust under noisy pairwise judgments,
- scalable to 100,000+ fields,
- supports GDPR / PIPL style compliance scenarios.
Use abstract, publication-safe performance visuals rather than overly detailed plots unless needed.
The result message should clearly state improved robustness, consistency, scalability, and interpretability.

Visual style requirements:
- Benchmark the visual language of Nature / Nature Machine Intelligence figures, but adapted for AI systems and data governance research.
- Use a clean modular multi-panel composition labeled A–F.
- White background, crisp vector style, journal-ready at single-column readability.
- Use a colorblind-friendly palette: blue for semantic encoding / embeddings, orange for pairwise comparison, green for globally consistent ranking output, red only for conflicts or hallucination-induced cycles, and neutral gray for structural database elements.
- Typography should be modern, minimal, sans-serif, and highly legible.
- Use consistent arrow logic, iconography, and visual encoding across all panels.
- Database fields, ranking edges, similarity clusters, matrices, and evidence chains should all be visually polished and coherent.
- Avoid speculative or unsupported components not present in the paper.
- Keep the design modular and easy to refine later in Adobe Illustrator.

The overall impression should be: a rigorous, elegant, publication-ready AI/data-governance methodology figure that clearly communicates the transition from unstable Pointwise classification to scalable, interpretable, globally consistent Pairwise ranking.
```

### 附录 B — 中文提示词（示例）

```text
请绘制一张用于计算机科学 / 数据治理论文的顶刊风格方法总览图（method overview figure），白色背景，矢量风格，高分辨率，可直接用于论文主图。整张图应为多分面（A–F）的流程-机制复合图，而不是生物机制图。

研究主题是：面向大规模数据库字段敏感度分级的自动化排序框架。核心思想是将传统 Pointwise 绝对分类，转化为 Pairwise 相对排序；再通过 Top-K 语义传播降低比较复杂度；最后利用 ROMVI 做全局一致性修正，并输出可审计的证据链。

Panel A：问题背景与现有方法局限
展示大规模数据库 schema / 字段集合（例如 user_id、phone、zipcode、address、purchase_history、diagnosis_code、device_id 等），以及 L1–L5 敏感等级。
并行对比两条路径：
1）Pointwise：逐字段独立分类，存在语义边界漂移、随机幻觉、同类字段等级不一致；
2）Pairwise：基于相对比较"谁比谁更敏感"，语义判断更稳定。
要把 Pointwise 的"不一致"可视化出来。

Panel B：Pairwise 排序建模
展示两个字段输入到 LLM 比较器中，输出"fi 比 fj 更敏感"的偏好关系。
可加入简洁公式元素，例如 P(fi ≻ fj) 或潜在敏感度分数 θi、θj。
箭头方向必须清晰，强调从局部成对比较到全局排序恢复。

Panel C：Top-K 语义传播
展示字段 embedding、语义向量空间、近邻聚类或相似度图。
突出一个字段的 Top-K 相似邻域，并展示"一次 pairwise 判断"如何传播到相似字段集合。
明确表现复杂度从 O(N^2) 降至 O(N log N)。
需要体现"相似度阈值""受限传播""避免语义漂移"等机制。

Panel D：ROMVI 全局一致性修正
展示一个含噪声的 pairwise 比较矩阵或有向图，其中存在逻辑环（如 A>B、B>C、C>A）。
然后展示 ROMVI / rank-one projection 如何把含冲突的局部判断，投影成全局一致的敏感度向量。
可加入主特征向量、秩一结构、去噪、一致性恢复等数学视觉元素，但不要过度堆公式。
重点是"从局部冲突到全局自洽"。

Panel E：可解释性与证据链
展示一个 DAG 或拓扑证据链。
说明某个字段的最终等级可以追溯到：
- 它高于哪些低等级锚点字段；
- 它低于哪些高等级锚点字段；
- 它在 L1–L5 之间的证据路径。
突出 auditability、explainability、compliance-ready。

Panel F：结果与实际价值
简洁展示主要结论：
- Pairwise + ROMVI 优于 Pointwise；
- Kendall's tau、准确率、鲁棒性更好；
- 可扩展到 100,000+ 字段；
- 支持 GDPR / PIPL 等合规场景。
用简洁、论文风格的小型结果模块或性能徽章表达，不要做成商业海报风。

风格要求：
- 参考 Nature / Cell / Nature Machine Intelligence 的图形语言，但应用于 AI 方法论文。
- 色彩需色盲友好：蓝色表示语义编码/embedding，橙色表示 pairwise 比较，绿色表示一致性修正后的全局排序结果，红色仅用于表示冲突/逻辑环，灰色用于数据库结构和背景元素。
- 所有文字用清晰无衬线字体，布局规整，逻辑方向统一。
- 图中要有数据库字段、相似图、排序边、矩阵、证据链等元素，且视觉编码保持一致。
- 避免加入论文未明确支持的模块或结论。
- 整体呈现应专业、克制、清爽，适合后续在 Adobe Illustrator 中继续精修。
```

---

## 复现检查清单

- [ ] ChatGPT 新对话已上传目标论文
- [ ] 已确认领域描述是否合理
- [ ] 已获得可粘贴的**完整**生图提示词
- [ ] Gemini 已切换到绘图模式并粘贴提示词
- [ ] 检查生成图片是否符合原文描述
- [ ] 终稿在矢量工具中统一字体与线宽

---

_文档路径：`picture/AI科研绘图流程说明.md`。示例对比图：`picture/example/`。_
