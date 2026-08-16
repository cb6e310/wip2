# NC-HSG 小论文统一规格（综合整合版 v1.1）

> **工作标题（待结果冻结）**：*Null-Calibrated Hierarchical Semantic Generation for Evidence-Bounded EEG-to-Text*  
> **中文标题（待结果冻结）**：面向证据边界 EEG-to-Text 的零对照校准层级语义生成

本文件是 `NC_HSG_Paper_Spec.md` 与 `NC_HSG_Paper_Spec_v1.md` 的逐项审阅、冲突裁决和统一规格。它是论文、实验和实现的共同合同；不是结果报告，文中所有【新】数值均必须在正式实验前冻结，所有【核】事实在核实前不得写成论文结论。

---

## 0. 综合分析与冲突裁决

### 0.1 输入文件

| 标识 | 文件 | 用途 |
|---|---|---|
| S1 | `NC_HSG_Paper_Spec.md` | 详细版：Gate A1、零对照合同、主表、执行合同与下一任务 |
| S2 | `NC_HSG_Paper_Spec_v1.md` | 前序定量版：核心命题、主指标建议、简化执行顺序与失败路由 |

### 0.2 一致结论（直接继承）

1. 用户已锁定 \(B'=\mathrm{NC\text{-}HSG}\)，不再发散新的 B/C 主线。
2. B 的问题落在 **measurement / evidence attribution**：绝对置信度不能区分 EEG 支持与语言先验、被试/会话捷径、长度和能量混杂。
3. C 必须内化为 \(W_l\) 的定义，而不是并行插件或额外 loss；删掉 C 应退化为 B，删掉层级应退化为 direct-C。
4. 只能在严格块内置换满足交换性时使用随机化 p 值；不得把一般 surrogate 称为 exact knockoff、FDR 控制或 distribution-free guarantee。
5. 主实验必须采用 stimulus-disjoint、无 teacher forcing、无真值前缀、无测试句检索，并以 subject 为主要统计 cluster。
6. MRL / RC-MSR / ordered-z 不进入 v1 标题、摘要、主表或主线消融；只有在 NC-HSG 通过主要 Gate 后才可作为独立 v2 表示层扩展。

### 0.3 定量冲突的统一裁决

| 项目 | S1 | S2 | 统一决定 | 理由与影响 |
|---|---|---|---|---|
| 主风险预算 | α₀=0.20 | α₀=0.10 | **α₀=0.10**【新】 | 更严格，直接对应“同一风险下更具体”；0.05/0.20/0.30 仅作预注册敏感性 |
| 主 null 数量 | K=199 | K=100 | **K=199**【新】 | 使随机化 p 的最小步长为 0.005；100 不再作为主配置 |
| bootstrap | 10,000 | ≥2,000 | **10,000 次 subject-cluster paired bootstrap**【新】 | 保留详细版的可复现上限；≥2,000 仅为最低实现要求，不是 v1 主值 |
| Gate A null 条件 | N1 与 N2 均须通过 | N1–N3 至少 2/3 | **标题级主张须 N1 与 N2 均通过**【新】 | N3 只作诊断/敏感性；“2/3”不足以证明强 null 合法性，移出主 Gate |
| 主指标 | supported-unit yield (U@0.20) | Specificity@Risk(0.10) | **Specificity@Risk(α₀)**【新】 | 主指标直接量化“允许说多深”；supported-unit yield 改为次级效用指标 |
| 下一任务 | 先做 sampler + Gate A1 | 先冻结 A/数据/schema 并做 Gate A pilot | **分两段执行：先 S0–S2，后 S3–S4** | 先验证最便宜且最致命的 null 合法性，再做 schema 与语义增量；Gate 前不接自由 LLM |
| direct-C | flat global gate / fixed depth 两种表述 | 同一 W 的单标量门 | **固定为同候选集、同 W、单一全局门；可附固定 L2/L4 诊断**【补】 | 防止把 direct-C 做成稻草人；主 Gate B 只比较正式 flat 版本 |

### 0.4 证据标签

- **【源】**：输入文件或其明确引用的一手文献支持。
- **【推】**：由【源】写出推理链得到，非原文直接结论。
- **【新】**：项目级定量决定，正式结果前冻结。
- **【补】**：实现必须补齐的接口或定义。
- **【核】**：需查数据、代码、metadata、文献或人工审计后才能确认。
- **【No-Go】**：触发后停止当前标题级 claim；不得换指标、放宽 split、换数据集或加模块事后挽救。

---

## 1. 统一科学问题与论文边界

### 1.1 A+B+C → A+B′ 的因果链

```text
EEG 单 trial 语义证据稀薄，但高容量 LLM 仍能生成流畅细节
→ EB-HSG 允许分层回退，却把“能说多深”建立在绝对分数 s_l 上
→ s_l 同时受脑信号、语言先验、subject/session、长度和能量影响
→ 需要一个保留 nuisance、只破坏 trial–text 对应的结构匹配零对照
→ 定义 W_l = s_l(real) − median[s_l(null)]，以 W_l 驱动层级、回退、拒答和校准
→ 在严格 split、独立 calibration 和无 teacher forcing 下检验
→ 无 real-vs-null 增量、null 不合法或打不过简单基线即撤销标题级主张
```

### 1.2 唯一核心 scientific question

> 在有限 EEG 证据下，真实 EEG 相对结构匹配零对照的可重复增量，能否决定样本最多应输出到哪一层语义，并在相同 unsupported-unit risk 下比绝对分数路由、固定粒度和 flat direct-C 更具体？

### 1.3 标题级命题（待验证）

NC-HSG 将语义具体度绑定到 real-vs-null 增量，并在独立校准集上联合选择完整层级策略；只有在严格 stimulus/subject/session 协议与无 teacher forcing 下，且通过 Gate A1、Gate A 及 Comparison 1 后，才可声称其在同一语义风险预算中优于 EB-HSG。

### 1.4 贡献上限（最多三条）

1. **问题/诊断**：量化 EEG-to-Text 绝对层级分数的不可归因性，并检验增量是否随层级加深衰减。
2. **方法**：提出 NC-HSG，用一个 \(W_l\) 同时驱动层级细化、父子一致、回退、拒答和风险校准。
3. **协议**：建立含 Gate A1、强/弱 null 分级、双 Regime 交换性声明、语言化阶梯和失败路由的决定性评测协议。

### 1.5 明确不 claim

不声称 thought reading、逐样本绝对可靠、任意未见被试/设备/跨日保证、生成细节全部来自 EEG、exact Model-X knockoff、FDR 控制、distribution-free guarantee、或 COFETT 两名被试的人群泛化。BLEU/ROUGE/BERTScore 只能作次级可读性指标。

---

## 2. 方法定义（A、B、C、B′）

### 2.1 Backbone A（controlled，不是贡献）

固定接口：

\[
A:E\in\mathbb R^{C\times T}\xrightarrow{\text{encoder/tokenizer}}h\xrightarrow{P_\phi}z\in\mathbb R^{L\times d_{LM}}\xrightarrow{\text{frozen/PEFT LM}}\text{text}.
\]

NeuroLM 公开 checkpoint 或经核实的 A2（如 CET-MAE/E2T-PTR）只能二选一并记录 checkpoint hash、输入窗、采样率、通道处理、projector、LoRA rank/target modules、冻结范围和参数量。所有方法行共享同一 A、训练步数、optimizer、seed、候选集和评测脚本；A 不计为本文贡献。具体 checkpoint 在 V3 核实前标【核】，未核实不得训练。

### 2.2 层级语义对象与原始 B（EB-HSG）

| 层 | 语义对象 | 允许输出 | 必须满足 |
|---|---|---|---|
| L0 | 拒答 | 空 | (g^*=0) 时 utility 与 depth 均为 0 |
| L1 | 主题/意图标签 | 单标签 | 闭集标签表版本化 |
| L2 | 概念或实体—事件单元集合 | 集合 | lemma/同义词规则冻结 |
| L3 | 命题元组（主体、关系、客体、极性、有限修饰） | 元组集合 | 极性、数字和关系显式计分 |
| L4 | 仅语言化已认证 L3 单元 | 受约束文本 | 不得新增实体、数字、关系、极性、因果或修饰 |

必须存在确定投影 (P_l) 使 (P_l(Y_{l+1})=Y_l)，并先在真值端与预测端审计父子一致率。L1–L4 不得由四个互不兼容 head 独立产生；v1 使用同一带 level token 的语义解码器 (F)。

原始绝对分数为

\[
s_l(E,\hat y_l)=\log P_F(\hat y_l\mid z(E),l),
\]

或等价的冻结、无 teacher forcing、候选级兼容 score；具体 tensor contract 属【补】，必须在实现前冻结。

### 2.3 C：结构匹配零对照

零对照必须保留预定义 nuisance \(N(E)=\{subject,session,length\text{-}bin,band\text{-}power\text{-}bin,channel\text{-}covariance\}\)，同时破坏 trial–text 对应。整段 surrogate 不自动满足 coordinate-wise swap exchangeability，也不自动给出 \(\widetilde E\perp Y\mid E\)，因此：

- N1 在预定义 exchangeable block 内的严格置换可给随机化 p 值；
- N2/N3/N4 等非严格置换只给经验 null score；
- 任何情况下不得写 exact knockoff、FDR 或 distribution-free 风险保证，除非另有定理和逐项交换性验证。

### 2.4 B′：NC-HSG 的唯一新变量

对每个候选 \(\hat y_l\) 构造 \(K=199\) 个 null：

\[
W_l(E,\hat y_l)=s_l(E,\hat y_l)-\operatorname{median}_{k=1..K}s_l(\widetilde E^{(k)},\hat y_l).
\]

仅当 \(\widetilde E^{(k)}\) 来自严格块内置换时，才报告

\[
p_l=\frac{1+\sum_k\mathbf1\{s_l(\widetilde E^{(k)},\hat y_l)\ge s_l(E,\hat y_l)\}}{K+1};
\]

否则将其称为经验 null score，而非 p 值。

完整策略 \(\pi=(m_1{:}m_4,\tau_1{:}\tau_4)\) 在独立 calibration 集上联合选择：

\[
g^*_\pi(E)=\max\{l:\forall j\le l,\ W_j\ge m_j,\ s_j\ge\tau_j,\ P_{j-1}(\hat Y_j)=\hat Y_{j-1}\},
\]

\[
\pi^*=\arg\max_{\pi\in\Pi}\widehat{D}_{cal}(\pi)\quad\text{s.t.}\quad
\operatorname{UCB}_{\delta}[R_{sem}(\pi)]\le\alpha_0.
\]

校准只选择完整策略与阈值，不做表示学习、标签抽取器选择或 null 生成器调参。LLM 只接收通过的 \(\hat Y_{g^*}\) 与允许槽位。

### 2.5 单变量归因与反循环约束

主比较唯一改变 \(s_l\to W_l\)。共享 A、F、schema、projection、candidate set、split、optimizer、训练步数、参数量、seed、超参搜索次数、calibration size、\(\Pi\) 基数、\(\alpha_0,\delta\)、评测脚本和测试样本。B′ 多出的 \(K+1\) 前向由 B 的计算匹配自集成对照处理，不得把计算量差异伪装成结构收益。

禁止：test 文本拟合 schema/词表；test gold 前缀或 teacher forcing；test sentence retrieval/RAG；calibration 参与表示学习；看过 test 后刷新 null、prompt、candidate size、停止规则；生成器与 evaluator 使用不可审计的同一 judge。每次运行记录 git/config/checkpoint/schema/prompt hash。

---

## 3. 风险、效用与主指标

对样本 \(i\)，真值单元集为 \(\mathcal U_i\)，输出单元集为 \(\hat{\mathcal U}_i\)：

\[
r_i=\frac{|\hat{\mathcal U}_i\setminus\mathcal U_i|}{\max(|\hat{\mathcal U}_i|,1)},\quad
miss_i=\frac{|\mathcal U_i\setminus\hat{\mathcal U}_i|}{\max(|\mathcal U_i|,1)},
\]
\[
q_i=\frac{|\hat{\mathcal U}_i\cap\mathcal U_i|}{\max(|\mathcal U_i|,1)},\quad d_i=g^*(E_i)/4.
\]

定义 unsupported risk \(R_{sem}=E[r_i]\)、miss rate \(M_{sem}=E[miss_i]\)、supported-unit yield \(Q=E[q_i]\) 和 specificity \(D=E[d_i]\)。拒答时 \(r_i=q_i=d_i=0\)，故“永远拒答”不能刷低风险而获益。

**唯一 primary metric**：

\[
\textbf{Specificity@Risk(}\alpha_0\textbf{)}=D(\pi^*)\quad\text{with }\alpha_0=0.10.
\]

报告时必须同列给出测试集实际 \(\hat R_{sem}\)；若 \(\hat R_{sem}>\alpha_0\)，该方法的 primary 单元格标为无效。\(Q,M_{sem}\)、概念/命题 F1、父子一致率、real–null depth gap、null 深层率、ECE/Brier、BLEU/ROUGE/BERTScore 为次级或诊断指标。

### 3.1 冻结定量参数

| 参数 | v1 冻结值 | 说明 |
|---|---:|---|
| 主风险预算 \(\alpha_0\) | **0.10** | 敏感性 \(\{0.05,0.20,0.30\}\)；不得用敏感性替换主值 |
| 校准置信水平 | \(1-\delta=0.95\) | 仅在 Regime I 交换性条件下解释 |
| 每 trial null 数 | **K=199** | 敏感性 \(\{19,49,199\}\) |
| 主/试点/消融 seeds | 5 / 3 / 3 | 主表报告每 seed 与跨 seed 中位数 |
| paired cluster bootstrap | **10,000** | cluster=subject；同一 trial 成对 |
| MDE | \(\Delta D\ge0.10\) 或 \(\Delta g\ge0.25\) 层 | 两者须在 config 中指定优先级 |
| 主要确认性比较 | B′ vs B；B′ vs direct-C；B′ vs PMI | Holm，family-wise 0.05 |
| 候选预算 | L2≤20；L3≤10 | L1 类数与 L4 grammar 待核/冻结 |

---

## 4. 数据、切分与零对照合同

### 4.1 数据角色

| 数据 | 角色 | 纪律 |
|---|---|---|
| ZuCo 1.0/2.0 | primary 候选 | 被试、trial、session、采样率、通道、眼动同步、任务混用和 license 全部【核】；须做 stimulus 去重 |
| COFETT | 跨日/跨会话压力测试 | 完整采集仅 2 名被试；只能作描述性 robustness，不作人群泛化 |
| 第二独立 EEG-text 数据 | replication 候选 | 可获得性、协议与 license 未核实前不写成既定结果 |

最小记录：`trial_id, subject_id, session_id, stimulus_id, EEG, sampling/meta, text, semantic targets`。统计单位优先 subject；subject<5 时只报告描述性区间。

### 4.2 两个评测 Regime

| Regime | 切分 | 可以声称什么 |
|---|---|---|
| I | stimulus-disjoint；subject 可共享；train/cal/test 近似交换 | 可声称交换性条件下的总体期望风险控制 |
| II | subject×stimulus 联合 holdout（LOSO/跨日） | 只报外部效度、经验风险与相对排序，不声称风险保证 |

切分算法：先按 normalized stimulus ID、编辑距离和嵌入相似度去重；Regime I 用 60/20/20【新】划分 stimulus group；Regime II 对每个 held-out subject 使用不与 test 刺激重叠的 train/cal；train 内另切 inner-val；冻结 split hash。random trial split 只作为泄漏诊断，不得替代主切分。

### 4.3 Null families

| 编号 | 构造 | 保留/破坏 | 级别与用途 |
|---|---|---|---|
| N1 | subject×session×length-bin×band-power 分层内 trial–text 严格置换 | 保留 nuisance；破坏配对 | **强主 null**；唯一可给随机化 p |
| N2 | 多变量相位随机化/AAFT，匹配 PSD 与通道协方差 | 保留谱/协方差；破坏时间/事件结构 | **强主 null**；经验 null，需诊断 |
| N3 | 协方差/谱匹配有色噪声 | 保留二阶统计；破坏时间结构 | 中等强度，敏感性 |
| N4 | 被试错配 | 保留刺激侧；破坏被试特异响应 | 诊断 |
| N5 | zero/mean EEG | 破坏几乎全部 nuisance | 弱 null，上界诊断 |
| N6 | language-only | 移除 EEG | 语言先验下界 |

合同：主 \(W_l\) 必须分别以 N1、N2 报告；N3–N6 不能单独支持 brain attribution。donor pool 不得与评测 trial 重叠，采样器若含拟合成分只在 train 拟合并冻结；每 trial 记录 block ID、seed、surrogate hash。

---

## 5. Claim–Evidence Map 与 Gates

### 5.1 Claim–Evidence 表

| Claim | 实验 | 主判据 | 失败后的固定改写 |
|---|---|---|---|
| C1 零对照合法 | Gate A1：无文本 real-vs-null 判别器、nuisance probe、谱/协方差匹配、置换审计 | N1 AUC≤0.60；N2 AUC≤0.65；nuisance 恢复差≤0.05；N1 block 可审计 | 【No-Go】改称 matched corruption，删除 zero/evidence/randomization 语言 |
| C2 存在 real-vs-null 语义增量 | no-free-LLM E2；L1–L3 的 \(W_l\)、depth gap、null 深层率 | N1 与 N2 均须在 L1、L2：subject-cluster 95% CI 下界>0、Cliff \(|\delta|\ge0.20\)、≥2/3 被试同号 | 全失败→负结果/评测审计；仅 L1→主题—拒答接口 |
| C3 增量随层级衰减 | E2 层间检验 | \(W_1>W_3\) 且预注册单调趋势；Holm 校正 | 非单调先查先验/泄漏，未解释不得进主表 |
| C4 B′ 优于 B | 主表 Comparison 1 | \(\Delta D\ge0.10\)（或 0.25 层）、CI 下界>0、Holm 后显著 | 【No-Go】撤销标题级 NC-HSG 性能主张 |
| C5 层级优于 direct-C | Gate B | \(\Delta D>0\)、CI 下界>0，且 \(M_{sem}\) 不恶化>0.05 | 删除 hierarchical，收缩为 flat null-gated 方法 |
| C6 不是 PMI/语言先验 | PMI baseline、偏回归、\(\lambda\) 插值 | B′ 优势在控制 LM log-prob 后仍存在；不劣于 PMI | 【No-Go】删除 brain-evidence claim，改写为先验修正方法 |
| C7 风险校准有效 | Regime I test | \(\hat R_{sem}\le\alpha_0\)；跨 seed 不系统越界 | 删除“风险控制”措辞，仅写经验 risk–specificity |
| C8 受约束语言化不新增单元 | 同一骨架 structured/constrained/free | constrained 新增 entity/number/relation/polarity 率低于 free，且不抹平 gap | 只保留 L1–L3 结构化输出 |
| C9 外部效度 | Regime II、COFETT | 只要求相对排序描述性保持 | 限定为训练域/指定 split，不写跨被试保证 |

### 5.2 Gate A1：零对照合法性（最高优先级）

必须先于语义模型、LLM 和主表。判别器不看文本，只区分 real 与 surrogate。若 N1 AUC>0.60 或 N2 AUC>0.65，或 nuisance 恢复差>0.05，则停止 NC-HSG 命名；只能重做匹配、改称 matched corruption，或切换 TR-HSG/负结果路线。交换性不通过时禁止 p/FDR 语言，但不妨碍报告经验 null 诊断。

### 5.3 Gate A：核心现象

在严格 stimulus-disjoint split、无自由 LLM、只用结构化 L1–L3 的条件下，N1 与 N2 **两者均**满足：L1、L2 的 \(W_l\) CI 下界>0、Cliff \(|\delta|\ge0.20\)、至少 2/3 被试同号，且平均 depth gap≥0.25 层。只 L1 通过则降级为主题级接口；无任何层通过则转负结果/评测协议论文。

### 5.4 Gate B：层级独立价值

正式 direct-C 使用同一 A、F、candidate set、null score、训练/校准预算和 \(\alpha_0\)，只保留一个全局 \(W_{global}\) 门决定输出或拒答，不使用 parent-pass、逐层回退或联合层级策略。若 B′ primary 不优于 direct-C，删除 hierarchical claim，不得添加第三模块补救。

### 5.5 Generalization / Robustness Gate

- random split 单独成立不构成泛化证据；
- Regime II/COFETT 风险越界不等于方法失败，但只能作外部效度观察；
- 5 seeds 中排序反转、去掉 N1/N2 后反转、或对 (K)/预处理/被试子集高度依赖，均需降低 claim；
- 任一敏感性面板的结果不得事后替换 primary。

---

## 6. Baselines、公平性与主表

### 6.1 必须比较的行

| 行 | 方法 | 目的 |
|---|---|---|
| R0 | language-only | 语言先验下界；若接近 real，设置无信息 |
| R1 | A-only 自由完整生成 | 常规起点与过度具体风险 |
| R2 | 固定 L1/L2/L4 | 固定语义率对照 |
| R3 | A+B（EB-HSG） | 绝对分数路由，Comparison 1 对手 |
| R4 | A+B′（NC-HSG） | 本文方法 |
| R5 | A+direct-C | flat null gate，Gate B 一票否决 |
| R6 | PMI/LM prior correction | ALT-2，最危险简单解释 |
| R7 | entropy、energy、Mahalanobis、semantic entropy、LLM log-prob | 常规不确定性/OOD 对照 |
| R8 | A+B 计算匹配自集成 | 排除 (K+1) 次前向的计算收益 |
| R9 | Group-DRO、HSC/Selective Generation、GLIM/Brain-CLIPLM/SemKey（代码可用时） | 最近邻/竞争路线；协议不同时不得直接并排声称公平 |

### 6.2 公平性合同

所有行共享 A、schema、projection、split、candidate set、optimizer、训练步数、参数量、seed、calibration size、\(\Pi\) 基数、UCB 形式、\(\alpha_0,\delta\)、evaluator 和测试索引。方法专有模块的参数量、显存、超参试验数与推理前向次数必须记录。唯一理论归因变量是 score reference；计算量差异必须另有 R8。

### 6.3 主表列

主表以 Regime I 与 Regime II 分块，至少包含：

1. **Specificity@Risk(0.10)**（primary，subject-macro，95% CI）；
2. 实测 \(\hat R_{sem}\)（越界则 primary 无效）；
3. \(M_{sem}\)、\(Q\)、worst-subject specificity；
4. real depth 与 N1/N2 depth、\(\Delta depth\)、null 进入 L3/L4 概率；
5. 概念 F1、命题 F1、parent consistency；
6. BLEU/ROUGE/BERTScore（视觉上与 primary 分离，caption 明示仅可读性）。

三项确认性比较：R4 vs R3、R4 vs R5、R4 vs R6，Holm 校正；其余 exploratory。

---

## 7. 消融与分析

每个消融只回答一个归因问题：

- (W_l\to s_l)：参照系是否必要；
- 层级策略→direct-C：parent-pass/回退是否必要；
- 去父子一致性：嵌套约束是否减少关系/数字/极性错误；
- 联合策略→逐层阈值：完整 calibration 是否必要；
- N1→N3/N5：弱 null 是否高估证据；
- (K\in\{19,49,199\})：null 分布稳定性；
- median→mean/max/p：统计量敏感性；
- 去 length/band-power 分层：哪类 nuisance 匹配关键；
- structured→constrained→free：深层文本是否由 LLM 补齐；
- (s_l-lambda\log P_{LM}), (lambda\in[0,1])：PMI 连续插值；
- A 冻结 vs LoRA、眼动/词边界开关、A1/A2 backbone：外部稳健性。

### 7.1 必做分析

1. **B vs B′ 行为差异**：同一 test 计算 rank correlation、深度迁移矩阵；若 \(\rho>0.95\) 且收益不存在，机制解释可疑。
2. **Confound**：控制 length、frequency、surprisal、difficulty、subject/session、EEG amplitude/artifact；控制后残差 \(W_l\) 仍有增益才保留 brain attribution。
3. **Leakage/shortcut**：probe subject、session、stimulus ID；近重复检索审计；报告 random-vs-strict split 高估幅度。
4. **Identifiability**：真值/预测 parent consistency、盲法人工双人审计、Cohen κ；schema 不达标是 blocker。
5. **Failure cases**：低 SNR、高抽象/罕见主题、极端被试、N1/N2 边界样本、跨日 gap 消失、低风险但高 missed rate。

### 7.2 图表最低集合

F1 real/N1/N2 层级 depth 与 \(W_l\)；F2 absolute score vs \(W_l\) 风险单调性；F3 主 risk–specificity 曲线；F4 direct-C/PMI/消融；F5 Gate A1 合法性象限；F6 seed/K/null/preprocessing 稳健性；F7 Regime I→II→COFETT；F8 failure heatmap。禁止为凑数使用 t-SNE 或只展示 BLEU 曲线。

---

## 8. 执行顺序、开放项与停止合同

### 8.1 执行顺序

```text
S0  数据/许可证/metadata 审计，规范 stimulus ID，近重复去重
S1  冻结 A 接口、Regime I/II split 与 split hash；完成 leakage audit
S2  实现 N1/N2，运行 Gate A1（不接语义模型与 LLM）
S3  冻结 L1–L4 schema、projection、evaluator；盲法人工审计
S4  no-free-LLM real-vs-N1/N2 pilot，运行 Gate A
S5  实现 direct-C 与 PMI，先做 Gate B 预跑
S6  实现 NC-HSG 完整策略与 UCB/RCPS 校准
S7  Route Lock：冻结 config、metric、baseline、split、seed；解锁 test
S8  主表（5 seeds）→ S9 消融（3 seeds）→ S10 分析/失败案例
S11 Regime II、COFETT、第二 backbone/数据（若可用）
S12 写作冻结：按实际 Gate 结果重写标题、摘要、结论
```

Gate A1 之前不得实现自由 LLM、MRL、双曲几何、active acquisition、online ACI 或多种校准器；Gate A 之前不得跑大主表。

### 8.2 Frozen decisions（不得自行修改）

研究结构、B′ 身份、\(W_l\) 定义、L0–L4 schema 形式、\(\alpha_0=0.10\)、\(K=199\)、primary metric、N1/N2 主 null、subject-cluster CI、无 teacher forcing、无 test retrieval、MRL v2 降级、Gate A1→Gate A→Gate B 依赖关系。

### 8.3 Open blockers（缺失即 STOP）

1. **V1 数据**：ZuCo/COFETT 的被试、session、trial、通道、采样率、刺激重复和 license。
2. **V2 A**：exact checkpoint、输入 tensor、代码与许可证。
3. **V3 schema**：L1–L4 抽取器、projection、匹配器、人工审计方案。
4. **V4 null**：N1 block、donor pool、N2 相位/协方差实现和交换性边界。
5. **V5 statistics**：UCB/RCPS 具体形式、\(|\Pi|\)、candidate budget、近重复阈值和 calibration size。

Codex 或协作 AI 不得猜测上述项目，不得自行放宽 split、改 primary metric、换数据集或在 Gate 失败后加模块救回。

### 8.4 机器可执行 Stop 逻辑

```text
IF missing(A OR dataset_schema OR split_hash OR semantic_schema OR null_contract): STOP blocker
IF leakage_audit != PASS: STOP all comparisons
IF Gate_A1(N1 or N2) == FAIL: rename matched corruption; forbid exact/p/FDR language
IF Gate_A == FAIL: route = negative-result/audit; IF only L1 then topic-level route
IF primary(B′) <= primary(B): remove title-level performance claim
IF primary(B′) <= primary(direct-C): remove hierarchical claim
IF primary(B′) <= primary(PMI): remove brain-evidence claim
IF only random split / one seed / one subject: downgrade claim to observed-setting result
IF risk_pass AND M_sem exceeds pre-registered cap: anti-abstention FAIL
```

### 8.5 当前唯一 Next Task

**T-NEXT：冻结可复现 A 接口与 primary dataset 的最小 metadata，完成 stimulus 去重与 Regime I/II split manifest；实现 N1/N2 采样器并运行 Gate A1，完全不接语义模型、LLM 或 test 标签。**

验收交付：`data_card.md`、`split_regimeI.json`、`split_regimeII.json`、split hash、`nulls/N1`、`nulls/N2`、每 trial 采样日志、`reports/gate_a1.md`、F5。只有 Gate A1 通过后，才进入 schema 审计与 no-free-LLM Gate A。

---

## 9. 最终可写 claim（结果前的保守版本）

> 在严格、无泄漏、无 teacher forcing 的指定 EEG-to-Text 协议下，只有当真实 EEG 相对预先规定的结构匹配零对照提供可重复语义增量时，NC-HSG 才允许输出更深层语义；在独立 calibration 的风险上界内，它是否比 EB-HSG、direct-C 与固定粒度更具体，必须由 Gate A1、Gate A 与预注册 Comparison 1 的结果决定。当前文件冻结的是可证伪的研究规格，不是已经成立的实验结论。

## 10. 结果后的标题/结论收缩规则

| 结果 | 允许的最强版本 |
|---|---|
| Gate A1 失败 | 不得称 NC-HSG/null evidence；改为 matched-corruption 诊断或 TR-HSG |
| Gate A1 通过、Gate A 失败 | 负结果/评测协议论文；不得写 EEG 语义增量 |
| 仅 L1 通过 | 主题级 evidence-abstention 接口；删除 L3/L4/generation 强 claim |
| Gate A 通过、B′≤B | 保留现象与协议诊断，撤销标题级性能 claim |
| B′>B 但 B′≤direct-C | 删除 “Hierarchical”，收缩为 flat null-gated selective generation |
| B′>B/direct-C 但≤PMI | 删除 brain attribution，改写为语言先验修正 |
| 主比较通过但仅 Regime I | 只写 fixed subject-pool、stimulus-disjoint 下的结果；Regime II 仅外部效度 |
| 全部 Gate 通过 | 才可使用标题级 NC-HSG claim，且仍不得升级为 thought reading、逐样本可靠或跨设备保证 |
