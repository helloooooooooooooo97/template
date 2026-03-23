# 基于 Pairwise 排序的文本分类方法

**作者**：孙久奇、曹倚铭、吴鸿、陈碧玉、张文馨

---

## 摘要

传统文本分类方法通常采用点态（pointwise）范式，直接预测每个样本的绝对类别标签。然而，这种范式在面对标注噪声或处于决策边界的模糊样本时往往表现不稳定。本文提出将文本分类问题重构为 pairwise 排序问题：通过比较样本对来学习相对类别倾向，而非直接预测绝对标签。具体而言，我们采用共享编码器对文本对进行表示，利用 RankNet 形式的 pairwise 损失进行训练，并通过 Bradley-Terry 模型将学习到的排序偏好聚合为最终分类结果。在情感分类（SST-2、IMDB）和主题分类（AG News）任务上的实验表明，所提方法在准确率上可与基于 BERT 的点态基线相当甚至略有提升，同时在标注噪声场景下展现出更强的鲁棒性。本文工作为利用相对比较信号进行文本分类提供了新的思路。

**关键词**：文本分类；Pairwise 排序；Learning to Rank；自然语言处理

---

## 1. 引言

文本分类是自然语言处理（NLP）中的基础任务，广泛应用于情感分析、主题分类、意图识别等场景。近年来，深度学习与预训练语言模型（如 BERT、RoBERTa）极大地提升了文本分类的性能，各类方法通常采用点态范式：对每个样本独立建模，直接预测其属于各类别的概率或标签。

然而，点态方法存在若干局限。首先，在标注质量不理想时，模型难以区分真实模式与噪声。其次，对于处于决策边界附近的样本，绝对标签往往难以给出稳定指导。最后，人类标注者在实践中更擅长做相对判断（如「文档 A 比文档 B 更可能属于正类」），而非精确的绝对标注。

Learning to Rank（LTR）领域中的 pairwise 方法为此提供了启示。在信息检索中，Pairwise 方法通过比较文档对来学习排序，而非直接预测每篇文档的绝对相关性得分。这种相对比较范式被认为更符合人类偏好表达方式，且在噪声环境下更具鲁棒性。

本文将文本分类问题重构为 pairwise 排序问题，并验证其可行性。主要贡献包括：（1）给出分类到排序的形式化定义及从排序到分类的映射策略；（2）提出基于预训练语言模型的 pairwise 文本分类框架；（3）在多个文本分类任务上进行实验，分析所提方法相对于点态基线的优势与适用场景。

---

## 2. 相关工作

### 2.1 Learning to Rank

Learning to Rank 通常分为三种范式。**Pointwise** 将排序问题视为回归或分类，对每个文档独立预测得分或标签。**Pairwise** 将排序转化为文档对之间的偏好关系，学习目标为使正确文档排在错误文档之前。**Listwise** 则直接对整份文档列表建模，优化列表级指标。

Pairwise 方法包括 RankNet、RankBoost、LambdaRank 等。其中 RankNet 将排序问题建模为学习 $P(d_i \succ d_j)$（文档 $d_i$ 排在 $d_j$ 前的概率），采用交叉熵损失进行优化。本文借鉴 RankNet 的思想，将文档对间的偏好关系迁移至文本分类中的类别倾向比较。

### 2.2 排序与分类的结合

已有工作探讨了将排序思想应用于分类任务。部分研究利用排序损失（如 pairwise hinge loss）作为辅助目标，提升分类边界的区分度；也有工作直接以排序作为主任务，再通过阈值或聚合策略得到类别。本文在此基础上，系统地将文本分类建模为 pairwise 排序，并给出了完整的训练与推断流程。

---

## 3. 方法

### 3.1 问题形式化

设文档集为 $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^N$，其中 $x_i$ 为文本，$y_i \in \{0, 1\}$ 为二分类标签（0 为负类，1 为正类）。传统点态方法学习映射 $f: \mathcal{X} \mapsto [0,1]$，直接预测 $P(y=1|x)$。

我们将问题重构为 pairwise 排序：对任意样本对 $(x_i, x_j)$，若 $y_i > y_j$，则希望模型学到「$x_i$ 比 $x_j$ 更倾向于正类」。形式化地，定义偏好关系：

$$
x_i \succ x_j \iff y_i > y_j
$$

学习目标为拟合条件概率：

$$
P(x_i \succ x_j \mid x_i, x_j) = P(y_i > y_j \mid x_i, x_j)
$$

训练时，从数据集中采样样本对 $(x_i, x_j)$，若 $y_i \neq y_j$ 则构成有效训练样本；$y_i = y_j$ 时无偏好，可跳过或用于正则化。

### 3.2 模型架构

模型由共享文本编码器和 pairwise 评分网络组成，整体流程如下：

```
样本对 (x_i, x_j) → 文本编码器 → 排序网络 → P(y_i > y_j) → 类别标签
```

**编码器**：采用预训练语言模型（如 BERT）作为共享编码器，将 $x_i$ 和 $x_j$ 分别编码为向量 $\mathbf{h}_i, \mathbf{h}_j \in \mathbb{R}^d$。

**Pairwise 评分**：借鉴 RankNet，定义：

$$
o_{ij} = \sigma(s_i - s_j), \quad s_i = g(\mathbf{h}_i), \quad s_j = g(\mathbf{h}_j)
$$

其中 $g: \mathbb{R}^d \mapsto \mathbb{R}$ 为单层 MLP，$\sigma$ 为 sigmoid 函数。$o_{ij}$ 表示模型预测的 $P(x_i \succ x_j)$。

**损失函数**：对有效样本对 $(x_i, x_j)$，设 $S_{ij} = 1$ 当且仅当 $y_i > y_j$，则采用交叉熵损失：

$$
\mathcal{L} = -\sum_{(i,j)} \left[ S_{ij} \log o_{ij} + (1 - S_{ij}) \log (1 - o_{ij}) \right]
$$

训练时可采用 mini-batch 内成对采样，或预采样固定数量的正负样本对以平衡计算成本。

### 3.3 从排序到分类

推断阶段需将 pairwise 偏好聚合为类别标签，可采用以下策略：

- **方案 A：锚点比较**。选取一锚点样本 $x_a$（如训练集正负类各取一代表），对测试样本 $x$ 计算 $P(x \succ x_a^+)$ 与 $P(x \succ x_a^-)$，根据与正负锚点的比较结果判定类别。

- **方案 B：Bradley-Terry 聚合**。假设存在潜在得分 $\theta_i$ 使得 $P(x_i \succ x_j) = \sigma(\theta_i - \theta_j)$。对测试集样本，通过最小化 pairwise 预测与模型输出的一致性可估计 $\theta$，再按 $\theta$ 排序并以阈值划分得到类别。

- **方案 C：投票聚合**。对测试样本 $x$，与多个参考样本构成配对，统计「$x$ 优于负类样本」的比例，超过阈值则判为正类。

本文实验主要采用**方案 A**，实现简单且与点态方法在推断复杂度上可比。

---

## 4. 实验

### 4.1 数据集

| 数据集 | 任务类型 | 类别数 | 训练集规模 | 测试集规模 |
|--------|----------|--------|------------|------------|
| SST-2 | 情感分类 | 2 | 67,349 | 872 |
| IMDB | 情感分类 | 2 | 25,000 | 25,000 |
| AG News | 主题分类 | 4 | 120,000 | 7,600 |

对于 AG News 四分类，采用「一对多」策略：每次将一类作为正类，其余三类为负类，训练四个二分类器，推断时取得分最高的类别。

### 4.2 基线方法

- **BERT-base**：标准 BERT 点态分类（[CLS] 表示 + 线性分类头）
- **RoBERTa-base**：RoBERTa 点态分类
- **BiLSTM**：词嵌入 + 双向 LSTM + 全连接层

所有方法使用相同的预训练模型（bert-base-uncased、roberta-base），batch size 为 32，学习率 $2 \times 10^{-5}$，训练 3 个 epoch。

### 4.3 评价指标

采用准确率（Accuracy）和宏平均 F1（Macro-F1，多分类任务）作为主要指标。

### 4.4 结果与分析

主实验结果（SST-2、IMDB 为二分类 Accuracy；AG News 为 Accuracy / Macro-F1）如下：

| 方法 | SST-2 | IMDB | AG News |
|------|-------|------|---------|
| BiLSTM | 84.2 | 87.1 | 91.2 / 91.0 |
| BERT-base (pointwise) | 92.3 | 93.1 | 94.1 / 93.9 |
| RoBERTa-base (pointwise) | 93.5 | 93.8 | 94.5 / 94.3 |
| **Ours (pairwise + BERT)** | **92.5** | **93.4** | **94.3 / 94.1** |
| **Ours (pairwise + RoBERTa)** | **93.7** | **94.0** | **94.6 / 94.4** |

所提 pairwise 方法在与点态方法使用相同编码器的条件下，在多数任务上取得了相当或略优的结果。这表明将分类重构为排序在文本领域是可行的。

**标注噪声鲁棒性**：在 SST-2 上随机翻转 10% 训练标签以模拟噪声。点态 BERT 准确率由 92.3% 降至 89.1%，而 pairwise 方法降至 90.2%，相对下降更小，说明相对比较对噪声更具鲁棒性。

**计算开销**：Pairwise 训练需构造样本对，每 batch 内有效对数约为 $O(n^2)$，实际中采用采样策略可将复杂度控制在可接受范围。推断阶段采用锚点比较，额外计算可忽略。

---

## 5. 结论

本文提出将文本分类重构为 pairwise 排序问题的方法，通过比较样本对学习相对类别倾向，并利用锚点比较或 Bradley-Terry 聚合得到最终分类结果。在情感分类与主题分类任务上的实验表明，所提方法在准确率上与点态基线相当甚至略优，且在标注噪声场景下展现出更好的鲁棒性。

本文工作存在若干局限：多分类需多次二分类扩展，计算成本增加；大规模 pairwise 采样对显存与时间有更高要求。未来工作可探索更高效的采样策略、listwise 扩展以及更复杂任务（如多标签分类、层次分类）上的应用。

---

## 参考文献

[1] Burges C, Shaked T, Renshaw E, et al. Learning to rank using gradient descent[C]//ICML, 2005: 89-96.

[2] Liu T Y. Learning to rank for information retrieval[J]. Foundations and Trends in Information Retrieval, 2009, 3(3): 225-331.

[3] Devlin J, Chang M W, Lee K, et al. BERT: Pre-training of deep bidirectional transformers for language understanding[C]//NAACL-HLT, 2019: 4171-4186.

[4] Socher R, Perelygin A, Wu J, et al. Recursive deep models for semantic compositionality over a sentiment treebank[C]//EMNLP, 2013: 1631-1642.

[5] Maas A L, Daly R E, Pham P T, et al. Learning word vectors for sentiment analysis[C]//ACL, 2011: 142-150.

[6] Zhang X, Zhao J, LeCun Y. Character-level convolutional networks for text classification[C]//NeurIPS, 2015: 649-657.
