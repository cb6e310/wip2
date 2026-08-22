# NC-HSG 小论文统一规格（综合整合版 v1.7，2026-08-21）

> **工作标题（待结果冻结）**：*Null-Calibrated Hierarchical Semantic Generation for Evidence-Bounded EEG-to-Text*  
> **中文标题（待结果冻结）**：面向证据边界 EEG-to-Text 的零对照校准层级语义生成

本文件是 `NC_HSG_Paper_Spec.md` 与 `NC_HSG_Paper_Spec_v1.md` 的逐项审阅、冲突裁决和统一规格，并吸收实现前的算法、随机化检验、风险校准、仓库治理与第六次输入准入审查。它是论文、实验和实现的共同合同；不是结果报告。文中所有【新】数值均必须在正式实验前冻结，所有【核】事实在核实前不得写成论文结论。v1.7 只修复 outcome-blind 的数据准入政策：把“全发布源审计无缺口”与“冻结分析子集可复现”分开，允许显式排除异常行并记录未知物理单位；不改变 v1.2–v1.6 的科学指标、阈值、Gate、split 纪律或失败路线。§12–§15 是不可改写的历史快照，§16 是当前状态与下一动作的权威增量。

> **版本权威**：v1.7 是下一次 Codex 导入后应激活的 SPEC。导入前远程 `main@bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7` 已正确激活 v1.6，并完成 run 007 的 schema-v3 event/segment correspondence：5,905 个可比较 segment 全部 exact，377 行有冻结排除理由，summary layer/reference 已绑定；绝对物理单位与少量 YTL event 异常仍未解决。v1.7 不改写 run 007 的保守 FAIL，而是修正 active admission policy：data card 的职责是记录可用分析视图、排除项与未知项，不要求原始发布的每个 row 或每个 metadata 字段都完美。下一 run 只从已提交 schema-v3 artifacts 派生 data card 和分析视图，不重新读取真实 EEG。

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
| direct-C | flat global gate / fixed depth 两种表述 | 同一 W 的单标量门 | **固定为同候选集、同 W、单一全局门；可附固定 L2/L3 与 L3+renderer 诊断**【补】 | 防止把 direct-C 做成稻草人；主 Gate B 只比较正式 flat 版本 |

### 0.4 v1.2 实现前审查裁决

| 缺口 | v1.2 裁决 | 防止的伪结论 |
|---|---|---|
| L4 只是语言化却被计作更深语义 | L4 保留为输出状态，但不增加 semantic depth；primary depth 只计 L0–L3【新】 | 仅改写成句子即可凭空提高 specificity |
| 真实 EEG 先选候选，再用同一候选做置换检验 | 冻结候选库，对 real 与每个 pseudo-real 对称重算“选择后统计量”【补】 | winner's curse 造成虚假的小 p 和大 \(W\) |
| N1 的无文本 real/null 判别 | 降级为实现 checksum；N1 合法性改由块定义、双射、作用域、覆盖和置换审计决定【补】 | 把“EEG 样本本来就相同”误写成 exchangeability 证据 |
| N1 每 trial 独立抽 donor | 改为每个 replicate 在各块内生成一次联合双射；\(K=199\) 指 199 个联合置换【补】 | 破坏随机化群结构与 subject-level 配对 |
| N2 的“相位随机化/AAFT”未定型 | primary 冻结为多变量 Fourier 共同相位增量候选，是否可用由真实数据诊断决定；AAFT 只作敏感性【补】 | 独立逐通道相位随机化意外摧毁通道协方差 |
| 同一 calibration 既挑策略又用逐策略 UCB 认证 | 必须在独立 certification split 上认证一个已选策略，或使用对整个有限 \(\Pi\) 同时有效的 LTT/多重性界【补】 | 选择偏差使风险上界失效 |
| 多 seed 被当独立样本 | 先在 trial/subject 内聚合 seeds，再以 subject 为 cluster【补】 | 人为放大有效样本量 |
| 示例 ZIP 被误当当前仓库状态 | 明确仅作格式参考；首次 Codex 任务必须从 `wip2` 实际文件保守建账【新】 | 导入其他项目的 DONE、blocker 或提交证据 |

### 0.5 证据标签

- **【源】**：输入文件或其明确引用的一手文献支持。
- **【推】**：由【源】写出推理链得到，非原文直接结论。
- **【新】**：项目级定量决定，正式结果前冻结。
- **【补】**：实现必须补齐的接口或定义。
- **【核】**：需查数据、代码、metadata、文献或人工审计后才能确认。
- **【No-Go】**：触发后停止当前标题级 claim；不得换指标、放宽 split、换数据集或加模块事后挽救。

### 0.6 v1.3 远程仓库复核裁决

本轮只读取了公开远程 `main`、治理代码、任务状态、run records 与官方数据/模型元数据；没有读取 held-out/test metric，也没有训练或运行科学模型。复核基线为 `wip2@1b836fe56970d262f4e8f3ae8262fd0abb670dbe`。

| 观察 | v1.3 裁决 | 影响 |
|---|---|---|
| 首次治理与审计已 push | 接受 `76504c6bef46664b9fb265cbdba544de9d37da99` 为治理 bootstrap 证据，接受 `1b836fe56970d262f4e8f3ae8262fd0abb670dbe` 为环境同步证据 | V0 仓库未知关闭；科学状态仍为零 |
| 19 个治理测试、validator、status 在独立 clone 中通过 | 记为治理基本功能 PASS，不把它外推为科学 acceptance | 可以继续治理加固和输入发现 |
| `CODEX_NEXT_TASK.md` 仍指向已完成的 bootstrap，且 blocker-resolution 没有 READY task | 这是可恢复的治理死锁；新增 `SPEC_V13_REVIEW` 与 `S0_INPUT_DISCOVERY_AUDIT` | 下一轮先修状态机，再做输入审计 |
| `repository_inventory.yaml`、`environment_snapshot.yaml`、`spec_implementation_matrix.yaml` 被 run 003 修改但仍标 run 002 生成 | snapshot 必须增加 `updated_by_run`/`evidence_as_of_commit`，或改用不可变 run-scoped 文件 | 防止 artifact provenance 漂移 |
| validator 把 spec 版本硬编码为 v1.2，且允许 `ROUTE_LOCK=DONE` 但 `route.locked=null` | 改为路径/声明的通用版本一致性检查；route lock DONE 时强制恰好一个合法 route 与有效 run | 防止升级死锁和空 route lock |
| `trust_align` 的 103 项环境已复制并通过 CUDA smoke | 只接受为 package/GPU 环境证据；不得因此准入其代码、数据、checkpoint 或结果 | V2 仍开放 |
| 当前仓库无数据、科学源码、checkpoint 或 result | 不直接实现 N1/N2/schema/模型；先做受限物理输入发现 | V1/V2 是唯一近期关键路径 |

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

NeuroLM 公开 checkpoint 或经核实的现有本地 A 只能按以下 outcome-blind 顺序审计；Codex 无权按 held-out 表现、代码熟悉度或下载便利自行选型：

1. 先只读审计 `/home/song/projects/trust_align` 是否存在**可复用但尚未准入**的单 trial EEG→text/semantic-score backbone。必须记录 Git commit、源文件、许可证、checkpoint 来源与 hash、输入 tensor、预处理、通道合同、训练/冻结范围和最小 smoke test；历史结果与 test metric 不得打开，也不得从该项目复制 DONE/claim。
2. 公共 fallback 冻结为官方 `NeuroLM-B + VQ` 候选：代码 `935963004/NeuroLM@0cda9876d8ce6ee07ed0c43eee5e9a6f5c24b177`（MIT）；模型仓库 `Weibang/NeuroLM@eddfff5c64a4139442f826d6c67c8369fd00f45a`。`NeuroLM-B.pt` 的官方 LFS SHA256 为 `ffe098bc138b89f8817d3710a3604498d8ecd15135080e2ca27735d05c6d29ab`、大小 `2377399148` bytes；`VQ.pt` 为 `e792c39a6a9e6d1bf4604cf63090730424f1d37f942597883d0c0a1375a2663a`、大小 `1904671888` bytes。模型卡声明 CC-BY-4.0【源】。
3. 官方 NeuroLM README/代码要求或实现了 0.1–75 Hz filtering、50/60 Hz notch、200 Hz、µV、每 token 200 samples、`standard_1020` channel index 与 mask/time tensor【源】。run 005–007 已核实本地 ZuCo 2.0 NR 为稳定的 105-channel EGI 合同、500 Hz、Cz acquisition reference、common-average processed reference，并以 5,905 个 exact segments 绑定 summary layer/reference；绝对 storage unit 与 NeuroLM channel mapping 仍未闭合【核】。因此不能声称 NeuroLM checkpoint plug-and-play，也不能先下载 4.28 GB 权重再临时发明 channel adapter。
4. 数据分析视图冻结后，由 ChatGPT/作者依据**单位依赖、通道改造、许可、可复现性和改造量**选择一个 A；不得依据 test 表现选择。当前 outcome-blind 倾向是优先审计能直接接受 105-channel release-native amplitude、并在 outer-train 内做尺度归一化的原生 frontend；NeuroLM/LaBraM 等要求明确 µV 或 128/standard-1020 映射的候选继续保留为未准入候选。该倾向不是本轮的 A 选择授权。

最终准入的 A 必须记录 checkpoint hash、输入窗、采样率、通道处理、projector、LoRA rank/target modules、冻结范围和参数量。所有方法行共享同一 A、训练步数、optimizer、seed、候选集和评测脚本；A 不计为本文贡献。具体 checkpoint 在 V2 核实前标【核】，未核实不得训练。

### 2.2 层级语义对象与原始 B（EB-HSG）

| 层 | 语义对象 | 允许输出 | 必须满足 |
|---|---|---|---|
| L0 | 拒答 | 空 | \(h^*=0\) 时 utility 与 depth 均为 0 |
| L1 | 主题/意图标签 | 单标签 | 闭集标签表版本化 |
| L2 | 概念或实体—事件单元集合 | 集合 | lemma/同义词规则冻结 |
| L3 | 命题元组（主体、关系、客体、极性、有限修饰） | 元组集合 | 极性、数字和关系显式计分 |
| L4 | 已认证 L3 的语言化状态 | 受约束文本 | 不得新增实体、数字、关系、极性、因果或修饰；不增加 semantic depth |

语义认证深度固定为 \(h\in\{0,1,2,3\}\)。L4 是 `rendered=true/false` 的输出状态，不是第四个语义层；因此它不能仅靠改写同一批 L3 单元获得额外 specificity。必须存在确定投影 \(P_2(Y_2)=Y_1\)、\(P_3(Y_3)=Y_2\)，以及语言化反投影 \(P_{4\to3}(Y_4)=Y_3\)，并先在真值端与预测端审计父子一致率。L1–L3 不得由三个互不兼容 head 独立产生；v1 使用同一带 level token 的语义解码器 \(F\)，L4 只使用冻结 grammar/slot renderer。

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

**N1 联合置换合同**【补】：`length-bin` 只能来自 EEG 可观测时长/有效窗数，不得读取测试真值文本长度；band-power bins 的边界只在 train 冻结。每个 replicate 在每个 block 内生成一次 trial 索引双射，并把同一联合置换用于该 replicate 的全部 trial，不得为每个 trial 独立抽 donor。固定点允许但必须记录；block size=1 的 trial 标记 `N1_NOT_EVALUABLE`，不得借相邻 block。\(K=199\) 表示 199 个联合块内置换，可有 Monte-Carlo 重复，不要求每个 trial 有 199 个不同 donor。N1 的 real/null EEG 边际本来相同，所以“无文本 AUC 接近 0.5”仅是索引/预处理 checksum，不是交换性证明。

**N2 候选实现合同**【补】：primary 候选为多变量 Fourier surrogate，对同一频率的全部通道施加相同随机相位增量并保持共轭对称，以保留各通道谱和线性交叉谱；只处理未 padding 的有效片段，并原样保留 mask/长度。独立逐通道相位随机化不得作为主 N2。AAFT/IAAFT 仅作敏感性，除非真实数据证明其 PSD、通道协方差、幅值分布和边界伪迹均不劣于 primary 候选。N2 是否准入完全由 Gate A1 的真实数据诊断决定。

### 2.4 B′：NC-HSG 的唯一新变量

候选选择必须先过 **selection firewall**。每层候选库 \(\mathcal C_l(x)\) 只能由 outer-train 的 schema/词表与合法非 EEG 上下文 \(x\) 构造并冻结，不能读取 test gold、test sentence retrieval、calibration label 频率或当前测试 EEG；候选库、排序和 hash 对所有方法共享。

对每个冻结候选 \(y\in\mathcal C_l(x)\) 构造 \(K=199\) 个 null：

\[
W_l(E,y)=s_l(E,y)-\operatorname{median}_{k=1..K}s_l(\widetilde E^{(k)},y).
\]

真实输出在满足父子约束的候选中按 \(W_l\) 选择，平手规则预先固定。不能先按 \(s_l(E,y)\) 选出赢家，再把赢家当作事先固定候选计算普通置换 p。

若需要 N1 随机化 p，必须把候选选择包含在预注册统计量中。默认使用

\[
T_l(E;\mathcal C_l)=\max_{y\in\mathcal C_l(x)} s_l(E,y),
\]

\[
p_l^{sel}=\frac{1+\sum_{k=1}^{K}\mathbf1\{T_l(\widetilde E^{(k)};\mathcal C_l)\ge T_l(E;\mathcal C_l)\}}{K+1}.
\]

即每个置换样本都重新在同一冻结候选库上取最大值，而不是沿用 real EEG 选出的赢家。若使用层级 path statistic，也必须把整条 path selection 作为预注册 \(T\) 对每个置换重算。候选特异 p 仅在候选独立于当前 EEG、且在置换前已外部固定时允许。只有当整个候选库、选择规则、score pipeline 与块置换满足交换性时才称 \(p_l^{sel}\) 为随机化 p；N2–N6 一律称经验 null statistic。

完整语义策略 \(\pi=(m_1{:}m_3,\tau_1{:}\tau_3)\) 在独立 calibration 流程中联合选择：

\[
h^*_\pi(E)=\max\{l\in\{1,2,3\}:\forall j\le l,\ W_j\ge m_j,\ s_j\ge\tau_j,\ [j=1\ \lor\ P_j(\hat Y_j)=\hat Y_{j-1}]\},
\]

\[
\pi^*=\arg\max_{\pi\in\Pi}\widehat{D}_{cal}(\pi)\quad\text{s.t.}\quad
\operatorname{UCB}_{\delta}[R_{sem}(\pi)]\le\alpha_0.
\]

若没有层通过则 \(h^*=0\)。L4 renderer 只在 \(h^*=3\) 时接收已认证槽位，其成功与否另报，不改变 \(h^*\)。校准只选择完整策略与阈值，不做表示学习、标签抽取器选择或 null 生成器调参。若同一 calibration 数据用于搜索 \(\Pi\)，风险认证必须使用独立 `cal-cert`，或使用对整个有限 \(\Pi\) 同时有效并计入多重性的 LTT/上界；逐策略点态 UCB 不能在选出最优策略后直接宣称有效。LLM 只接收通过的 \(\hat Y_{h^*}\) 与允许槽位。

### 2.5 单变量归因与反循环约束

主比较唯一改变 \(s_l\to W_l\)。共享 A、F、schema、projection、candidate set、split、optimizer、训练步数、参数量、seed、超参搜索次数、calibration size、\(\Pi\) 基数、\(\alpha_0,\delta\)、评测脚本和测试样本。B′ 多出的 \(K+1\) score 由 B 的计算匹配自集成对照处理，不得把计算量差异伪装成结构收益。N1 必须缓存/复用 donor trial 的 real EEG embedding；N2 只在模型冻结后批量生成与缓存 surrogate score，禁止把 199 倍完整 LLM 解码写进训练循环。

禁止：test 文本拟合 schema/词表；test gold 前缀或 teacher forcing；test sentence retrieval/RAG；用当前 test EEG 动态扩候选；calibration 参与表示学习；看过 test 后刷新 null、prompt、candidate size、停止规则；生成器与 evaluator 使用不可审计的同一 judge。每次运行记录 git/config/checkpoint/schema/candidate/prompt hash。

---

## 3. 风险、效用与主指标

对样本 \(i\)，先把完整真值 L1–L3 投影为带 level type 的互斥原子并集
\(\mathcal U_i^{\le3}=\mathcal U_{i,1}\uplus\mathcal U_{i,2}\uplus\mathcal U_{i,3}\)。L1 topic、L2 concept/entity-event、L3 proposition 各自有冻结 matcher；同一字符串处在不同层仍是不同 typed atom。L4 不增加原子。模型输出只包含被认证到 \(h\) 的 \(\hat{\mathcal U}_i^{\le h}\)：

\[
r_i=\frac{|\hat{\mathcal U}^{\le h}_i\setminus\mathcal U^{\le3}_i|}{\max(|\hat{\mathcal U}^{\le h}_i|,1)},\quad
miss_i=\frac{|\mathcal U^{\le3}_i\setminus\hat{\mathcal U}^{\le h}_i|}{\max(|\mathcal U^{\le3}_i|,1)},
\]
\[
q_i=\frac{|\hat{\mathcal U}^{\le h}_i\cap\mathcal U^{\le3}_i|}{\max(|\mathcal U^{\le3}_i|,1)},\quad d_i=h^*(E_i)/3.
\]

定义 unsupported risk \(R_{sem}=E[r_i]\)、miss rate \(M_{sem}=E[miss_i]\)、supported-unit yield \(Q=E[q_i]\) 和 specificity \(D=E[d_i]\)。拒答时 \(r_i=q_i=d_i=0\)、\(miss_i=1\)（真值非空时），故“永远拒答”不能刷低风险而获益。`render_success`、`new_unit_rate_L4` 与受约束文本质量独立报告，绝不进入 \(D\)。

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
| 主/试点/消融 seeds | 5 / 3 / 3 | 主表报告每 seed；推断时先在 subject 内聚合 seed，不把 seed 当独立样本 |
| paired cluster bootstrap | **10,000** | cluster=subject；同一 trial 成对 |
| MDE | **\(\Delta D\ge0.10\)** | 等价于平均至少 0.30 个 L1–L3 语义层；不再用与归一化不一致的 0.25 层替代 |
| 主要确认性比较 | B′ vs B；B′ vs direct-C；B′ vs PMI | Holm，family-wise 0.05 |
| 候选预算 | L2≤20；L3≤10 | L1 类数与 L4 grammar 待核/冻结；候选库必须过 selection firewall |

### 3.2 Calibration 与统计单位合同

1. \(\Pi\) 必须是跑 test 前冻结的有限集合；记录每个策略及其 hash，不能连续黑盒调参后只保存赢家。
2. V5 必须在两种合法流程中二选一：`cal-select → cal-cert` 两段式，或在同一 calibration 上对全部 \(\Pi\) 做同时有效的 LTT/多重性风险认证。未冻结前不得使用“risk control”措辞。
3. 风险目标是 fixed subject-pool 下的 subject-macro expectation。trial 先在 subject 内聚合，seed 再在 subject 内聚合，最后 subject 才进入 cluster bootstrap/风险上界。
4. 若可用独立 subject 数不足以支撑所选 concentration bound，只报告经验 risk–specificity，不得把 trial-level i.i.d. 界移植到相关 trial。
5. calibration 只认证一个冻结 evaluator 的 loss；任何 schema、matcher、judge 或 null 诊断的选择必须更早在 train/inner-val 完成。

---

## 4. 数据、切分与零对照合同

### 4.1 数据角色

| 数据 | 角色 | 纪律 |
|---|---|---|
| ZuCo 2.0 task 1 Natural Reading（NR） | **primary 数据候选；分析视图待 v1.7 落账** | 官方论文报告 18 名有效参与者、349 句；自然阅读最贴合本文一般 EEG→text 问题。run 005–007 已核实许可、同源性、schema 与 5,905-row 可复现分析视图；v1.7 只需把排除和未知单位写入 data card，不把 TSR 的显式关系搜索任务混入 primary |
| ZuCo 2.0 task 2 Task-Specific Reading（TSR） | robustness/任务偏移 | 官方论文报告 390 句；参与者主动搜索关系类型，不能与 NR 无标记混池。先作为同设备同 session 的任务偏移面板，不进入 primary 训练/阈值选择 |
| ZuCo 1.0 | 后续 replication 候选 | ZuCo 2.0 与 1.0 存在已知 stimulus overlap；任何联合或迁移实验必须先做跨版本 stimulus group 去重 |
| COFETT | 跨日/跨会话压力测试 | 2026 年预印本报告完整采集仅 2 名被试；只能作描述性 robustness，不作人群泛化，且可得性/license 仍【核】 |
| 第二独立 EEG-text 数据 | replication 候选 | 可获得性、协议与 license 未核实前不写成既定结果 |

优先 ZuCo 2.0 NR 是额度效益与任务匹配决定，不是数据已准入结论。官方论文还报告：19 人采集后排除 1 人、每名有效参与者在一个 100–180 分钟 session 内读完 739 句、14 个约 50 句的交替任务 block、EEG 原始采样率 500 Hz/128 通道、预处理分析保留 105 个 scalp channel；这些只能用于核对物理 metadata，不能替代文件审计。NR/TSR 内约 8% 重复句、与 ZuCo 1.0 的 100 个 NR/85 个 TSR overlap 必须进入全局 stimulus group【源】。

官方 OSF 节点 `2urht` 是 public，论文称数据 freely available。v1.3 审计只读取 `attributes.node_license` 的空 copyright holder/year，漏掉了 `relationships.license`：该关系解析到 OSF license `563c1cf88c5e4a3877f9e96a`，名称为 **CC-By Attribution 4.0 International**【源】。因此“需要作者另给许可证”不再是用户 blocker；下一 run 必须保存节点响应、许可证响应、请求时间与响应 SHA256，并用官方两个 Python reader 的 OSF SHA256 对照本地副本，建立本地树与官方节点的可追溯关系。论文页面的出版许可仍不能替代这条数据节点许可证据。

首次仓库审计若证明 ZuCo 2.0 不在授权路径或关键字段不可恢复，必须建立 blocker并回到作者裁决，不能静默切到别的数据。最小记录：`trial_id, subject_id, session_id, task_id, block_id, stimulus_id, EEG, sampling/meta, text, semantic targets`。统计单位优先 subject；subject<5 时只报告描述性区间。

### 4.2 两个评测 Regime

| Regime | 切分 | 可以声称什么 |
|---|---|---|
| I | stimulus-disjoint；subject 可共享；train/cal/test 近似交换 | 只可声称固定 subject-pool、未来刺激分布下的总体期望风险控制 |
| II | subject×stimulus 联合 holdout（LOSO/跨日） | 只报外部效度、经验风险与相对排序，不声称风险保证 |

切分算法：先按 normalized stimulus ID、document/paragraph、编辑距离和冻结嵌入相似度建立不可拆分 stimulus group；近重复阈值只在看 test 结果前冻结。Regime I 用 60/20/20【新】划分 stimulus group；Regime II 对每个 held-out subject 使用不与 test 刺激重叠的 train/cal；train 内另切 inner-val；冻结 split hash。所有预处理拟合、schema/词表、候选库和 null bin edges 都只读相应 outer-train。random trial split 只作为泄漏诊断，不得替代主切分。

### 4.3 Null families

| 编号 | 构造 | 保留/破坏 | 级别与用途 |
|---|---|---|---|
| N1 | subject×session×length-bin×band-power 分层内 trial–text 严格置换 | 保留 nuisance；破坏配对 | **强主 null**；唯一可给随机化 p |
| N2 | 多变量 Fourier 共同相位增量；AAFT/IAAFT 仅敏感性 | 目标是保留 PSD/线性交叉谱，破坏时间/事件锁定结构 | **强主 null 候选**；经验 null，须以 Gate A1 准入 |
| N3 | 协方差/谱匹配有色噪声 | 保留二阶统计；破坏时间结构 | 中等强度，敏感性 |
| N4 | 被试错配 | 保留刺激侧；破坏被试特异响应 | 诊断 |
| N5 | zero/mean EEG | 破坏几乎全部 nuisance | 弱 null，上界诊断 |
| N6 | language-only | 移除 EEG | 语言先验下界 |

合同：主 \(W_l\) 必须分别以 N1、N2 报告；N3–N6 不能单独支持 brain attribution。N1 的 donor 是**同一评测 split 与同一预定义 block 内**的置换成员，不能从 train/cal 借 donor；“donor 不与评测 trial 重叠”仅适用于需要外部拟合/生成 donor pool 的 N3/N4，不适用于严格随机化 N1。任何采样器的拟合成分只在 train 拟合并冻结；每 trial/replicate 记录 split、block ID、permutation ID、fixed-point 标志、seed 和 surrogate hash。

在实现 N1 前必须先输出 block feasibility：每个 split/subject/session 的 block-size 分布、singleton 比例、可评估覆盖率、199 次联合置换的唯一率与固定点率。此项是 outcome-blind protocol audit；覆盖不足时先回到 V4，不得合并 block 或放宽 nuisance 以追求 Gate 通过。

---

## 5. Claim–Evidence Map 与 Gates

### 5.1 Claim–Evidence 表

| Claim | 实验 | 主判据 | 失败后的固定改写 |
|---|---|---|---|
| C1 零对照合法 | Gate A1：N1 block/双射/作用域审计；N2 无文本判别器、nuisance probe、谱/交叉谱/协方差与边界伪迹诊断 | N1 审计全 PASS 且 checksum AUC≤0.60；N2 AUC≤0.65；nuisance 恢复差≤0.05；N2 二阶统计在预注册容差内 | 【No-Go】改称 matched corruption，删除 zero/evidence/randomization 语言 |
| C2 存在 real-vs-null 语义增量 | no-free-LLM E2；L1–L3 的 \(W_l\)、depth gap、null 深层率 | N1 与 N2 均须在 L1、L2：subject-cluster 95% CI 下界>0、Cliff \(\delta\ge0.20\)、≥2/3 被试为正 | 全失败→负结果/评测审计；仅 L1→主题—拒答接口 |
| C3 增量随层级衰减 | E2 层间检验 | \(W_1>W_3\) 且预注册单调趋势；Holm 校正 | 非单调先查先验/泄漏，未解释不得进主表 |
| C4 B′ 优于 B | 主表 Comparison 1 | \(\Delta D\ge0.10\)、CI 下界>0、Holm 后显著 | 【No-Go】撤销标题级 NC-HSG 性能主张 |
| C5 层级优于 direct-C | Gate B | \(\Delta D>0\)、CI 下界>0，且 \(M_{sem}\) 不恶化>0.05 | 删除 hierarchical，收缩为 flat null-gated 方法 |
| C6 不是 PMI/语言先验 | PMI baseline、偏回归、\(\lambda\) 插值 | B′ 优势在控制 LM log-prob 后仍存在；不劣于 PMI | 【No-Go】删除 brain-evidence claim，改写为先验修正方法 |
| C7 风险校准有效 | Regime I cal-cert 与 test | 预注册的 simultaneous/独立认证上界≤\(\alpha_0\)，且 test \(\hat R_{sem}\le\alpha_0\)；跨 seed 不系统越界 | 删除“风险控制”措辞，仅写经验 risk–specificity |
| C8 受约束语言化不新增单元 | 同一骨架 structured/constrained/free | constrained 新增 entity/number/relation/polarity 率低于 free，且不抹平 gap | 只保留 L1–L3 结构化输出 |
| C9 外部效度 | Regime II、COFETT | 只要求相对排序描述性保持 | 限定为训练域/指定 split，不写跨被试保证 |

### 5.2 Gate A1：零对照合法性（最高优先级）

必须先于语义模型、LLM 和主表，并拆成两个不可互相替代的子门：

1. **A1-N1 structural**：block 只用预注册 nuisance；每个 replicate 在 block 内为双射；无跨 split 借 donor；singleton/固定点/覆盖完整 ledger；同 seed 重跑 byte-identical；selection-aware statistic 对每个 pseudo-real 对称重算。任何一项失败都禁止随机化 p。N1 无文本 AUC≤0.60 只检查实现没有把 real/null 走不同预处理路径。
2. **A1-N2 empirical**：预注册判别器不看文本，只区分 real 与 surrogate；同时测 subject/session/length/power probe、每通道 PSD、cross-spectrum/协方差、幅值分布、端点不连续、padding/mask。N2 AUC>0.65、任一主 nuisance 恢复差>0.05，或任一冻结二阶统计容差失败，则 N2 不准入。

标题级 NC-HSG 要求 A1-N1 与 A1-N2 都 PASS。仅 N1 失败时可保留“matched corruption”经验分数但不得称随机化 p；仅 N2 失败时不得用弱 N3/N5 替代并继续 brain-attribution 主张。低 AUC 是必要而非充分条件。

### 5.3 Gate A：核心现象

在严格 stimulus-disjoint split、无自由 LLM、只用结构化 L1–L3、通过 selection firewall 的条件下，N1 与 N2 **两者均**满足：L1、L2 的 \(W_l\) subject-cluster 95% CI 下界>0、Cliff \(\delta\ge0.20\)、至少 2/3 被试方向为正，且平均 semantic-depth gap≥0.25 层。Cliff 不能取绝对值；负方向永远不能算 PASS。只 L1 通过则降级为主题级接口；无任何层通过则转负结果/评测协议论文。

### 5.4 Gate B：层级独立价值

正式 direct-C 使用同一 A、F、candidate set、null score、训练/校准预算和 \(\alpha_0\)，只保留一个全局 \(W_{global}\) 门决定输出或拒答，不使用 parent-pass、逐层回退或联合层级策略。若 B′ primary 不优于 direct-C，删除 hierarchical claim，不得添加第三模块补救。

### 5.5 Generalization / Robustness Gate

- random split 单独成立不构成泛化证据；
- Regime II/COFETT 风险越界不等于方法失败，但只能作外部效度观察；
- 5 seeds 中排序反转、去掉 N1/N2 后反转、或对 \(K\)/预处理/被试子集高度依赖，均需降低 claim；
- 任一敏感性面板的结果不得事后替换 primary。

---

## 6. Baselines、公平性与主表

### 6.1 必须比较的行

| 行 | 方法 | 目的 |
|---|---|---|
| R0 | language-only | 语言先验下界；若接近 real，设置无信息 |
| R1 | A-only 自由完整生成 | 常规起点与过度具体风险 |
| R2 | 固定 L1/L2/L3；另报 L3+renderer | 固定语义率对照；renderer 不算更深语义 |
| R3 | A+B（EB-HSG） | 绝对分数路由，Comparison 1 对手 |
| R4 | A+B′（NC-HSG） | 本文方法 |
| R5 | A+direct-C | flat null gate，Gate B 一票否决 |
| R6 | PMI/LM prior correction | ALT-2，最危险简单解释 |
| R7 | entropy、energy、Mahalanobis、semantic entropy、LLM log-prob | 常规不确定性/OOD 对照 |
| R8 | A+B 计算匹配自集成 | 排除 \(K+1\) 次前向的计算收益 |
| R9 | Group-DRO、HSC/Selective Generation、GLIM/Brain-CLIPLM/SemKey（代码可用时） | 最近邻/竞争路线；协议不同时不得直接并排声称公平 |

### 6.2 公平性合同

所有行共享 A、schema、projection、split、candidate set、optimizer、训练步数、参数量、seed、calibration size、\(\Pi\) 基数、UCB 形式、\(\alpha_0,\delta\)、evaluator 和测试索引。方法专有模块的参数量、显存、超参试验数与推理前向次数必须记录。唯一理论归因变量是 score reference；计算量差异必须另有 R8。

### 6.3 主表列

主表以 Regime I 与 Regime II 分块，至少包含：

1. **Specificity@Risk(0.10)**（primary，subject-macro，95% CI）；
2. 实测 \(\hat R_{sem}\)（越界则 primary 无效）；
3. \(M_{sem}\)、\(Q\)、worst-subject specificity；
4. real semantic depth 与 N1/N2 semantic depth、\(\Delta depth\)、null 进入 L3 概率；L4 render success/new-unit rate 单列；
5. 概念 F1、命题 F1、parent consistency；
6. BLEU/ROUGE/BERTScore（视觉上与 primary 分离，caption 明示仅可读性）。

三项确认性比较：R4 vs R3、R4 vs R5、R4 vs R6，Holm 校正；其余 exploratory。

---

## 7. 消融与分析

每个消融只回答一个归因问题：

- \(W_l\to s_l\)：参照系是否必要；
- 层级策略→direct-C：parent-pass/回退是否必要；
- 去父子一致性：嵌套约束是否减少关系/数字/极性错误；
- 联合策略→逐层阈值：完整 calibration 是否必要；
- N1→N3/N5：弱 null 是否高估证据；
- \(K\in\{19,49,199\}\)：null 分布稳定性；
- median→mean/max/p：统计量敏感性；
- 去 length/band-power 分层：哪类 nuisance 匹配关键；
- structured→constrained→free：深层文本是否由 LLM 补齐；
- \(s_l-\lambda\log P_{LM}\)，\(\lambda\in[0,1]\)：PMI 连续插值；
- A 冻结 vs LoRA、眼动/词边界开关、A1/A2 backbone：外部稳健性。

### 7.1 必做分析

1. **B vs B′ 行为差异**：同一 test 计算 rank correlation、深度迁移矩阵；若 \(\rho>0.95\) 且收益不存在，机制解释可疑。
2. **Confound**：控制 length、frequency、surprisal、difficulty、subject/session、EEG amplitude/artifact；控制后残差 \(W_l\) 仍有增益才保留 brain attribution。
3. **Leakage/shortcut**：probe subject、session、stimulus ID；近重复检索审计；报告 random-vs-strict split 高估幅度。
4. **Identifiability**：真值/预测 parent consistency、盲法人工双人审计、Cohen κ；schema 不达标是 blocker。
5. **Failure cases**：低 SNR、高抽象/罕见主题、极端被试、N1/N2 边界样本、跨日 gap 消失、低风险但高 missed rate。

### 7.2 图表最低集合

F1 real/N1/N2 层级 depth 与 \(W_l\)；F2 absolute score vs \(W_l\) 风险单调性；F3 主 risk–specificity 曲线；F4 direct-C/PMI/消融；F5 Gate A1 合法性象限；F6 seed/K/null/preprocessing 稳健性；F7 Regime I→II→COFETT；F8 failure heatmap。禁止为凑数使用 t-SNE 或只展示 BLEU 曲线。

### 7.3 预注册 debug 定位表

| 观测 | 首查位置 | 固定动作 |
|---|---|---|
| N1 无文本 AUC 明显高于 0.5 | real/null 是否走了不同 normalization、padding、重复次数或索引路径 | 先修实现并重跑 checksum；不得调整 block 让 AUC 下降 |
| N1 singleton/固定点过多 | block key 过细、metadata 缺失、session 误解析 | 报 feasibility blocker；不得结果驱动合并 block |
| N2 AUC 高或边界能被识别 | FFT 端点、padding 后再变换、逐通道独立相位、幅值重映射 | 修正为有效片段上的多变量共同相位；重新跑全部二阶诊断 |
| \(W_l\) 很大但 language-only 同样大 | 候选选择偏差、LM prior、test candidate 泄漏 | 审 selection firewall、对称 pseudo-real 统计量和 PMI baseline |
| L3 通过率高但 parent consistency 低 | 多 head 不一致、projection/matcher bug、数字/极性漏计 | 阻断 Gate A；修 schema/evaluator，不调阈值 |
| calibration PASS、test risk 系统越界 | 同一 cal 选择与认证、trial i.i.d. 假设、seed 当样本、policy grid 未计多重性 | 降级为经验风险；重建 cal-cert/LTT 合同，不碰 test 阈值 |
| NC-HSG 只比 B 快/稳而不比 R8 好 | 额外 \(K+1\) 计算或 ensemble 收益 | 撤销结构收益；保持计算匹配对照 |
| L4 让 primary 提升 | depth 实现仍把 renderer 当语义层 | 视为 metric bug；L4 只能影响 render 指标 |

---

## 8. 执行顺序、开放项与停止合同

### 8.1 执行顺序

```text
G0  【DONE】首次仓库审计；建立 persistent project context、validator、状态快照与证据清单
G0.5 治理加固；修复 stale next task、blocker-resolution 死锁、artifact provenance 与版本/route-lock validator
G0.6 受限输入发现；只审计授权项目根与官方公共候选的 metadata、代码、许可和兼容性，不读历史 test metric
S0  数据/许可证/metadata 审计，规范 stimulus ID，近重复去重
S1  冻结 A 接口、Regime I/II split 与 split hash；完成 leakage audit
S2a outcome-blind N1 block feasibility；冻结 N1/N2 实现合同
S2b 实现 N1/N2，运行 Gate A1（不接语义模型与 LLM）
S3  冻结 L1–L3 schema、typed units、projection、evaluator 与 L4 renderer；盲法人工审计
S4  冻结 candidate selection firewall；no-free-LLM real-vs-N1/N2 pilot，运行 Gate A
S5  冻结 cal-select/cal-cert 或 simultaneous LTT；实现 NC-HSG、direct-C 与 PMI
S6  Gate B 与 Comparison 1 预跑；按 Gate 结果决定路线
S7  Route Lock：冻结 config、metric、baseline、split、seed；解锁 test
S8  主表（5 seeds）→ S9 消融（3 seeds）→ S10 分析/失败案例
S11 Regime II、COFETT、第二 backbone/数据（若可用）
S12 写作冻结：按实际 Gate 结果重写标题、摘要、结论
```

Gate A1 之前不得实现自由 LLM、MRL、双曲几何、active acquisition、online ACI 或多种校准器；Gate A 之前不得跑大主表。

### 8.2 Frozen decisions（不得自行修改）

研究结构、B′ 身份、\(W_l\) 定义、L0–L3 semantic depth、L4 仅 renderer、\(\alpha_0=0.10\)、\(K=199\)、primary metric、N1/N2 主 null、selection-aware 随机化统计量、subject-cluster CI、无 teacher forcing、无 test retrieval、MRL v2 降级、Gate A1→Gate A→Gate B 依赖关系。

### 8.3 Blocker ledger（缺失即 STOP）

0. **V0 仓库【CLOSED】**：公开 `main@bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7` 已完成治理 bootstrap、环境同步、治理加固、输入发现和三轮定向 NR 审计；关闭 V0 不代表任何科学模型或 Gate 已实现。
1. **G1 治理连续性【CLOSED】**：run 005 建立动态 active-SPEC fail-closed 回归检查，run 007 已把全部入口同步到 v1.6。下一 run 只需按同一机制激活 v1.7，并修复 active admission policy 与 YTL active 叙述；不得改写旧 run。
2. **V1 数据【POLICY REPAIR READY】**：run 007 已证明 18×349=6,282、6,282/6,282 material occurrence、5,911 个 finite multisample、367 个 nonfinite placeholder、4 个 single-sample exclusion，以及 5,905/5,905 event-valid segment exact correspondence。冻结分析视图为 5,905 行；排除集合为 377 行的并集：367 nonfinite placeholder、4 finite single-sample（同时落入 event anomaly）和 6 个额外 finite-multisample event-unresolved rows。YTL event anomaly 的 active 路径必须包含 NR3、NR5、NR6；单位写成 `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`。这些是 data-card 限制与未来 unit-sensitive A blocker，不再是 data card/stimulus identity 的永久 blocker。下一 run 只从 committed schema-v3 ledgers 派生分析视图与 data card，不读取真实 EEG、不修 event、不猜 unit。
3. **V2 A【OPEN，候选已盘点】**：`TRUST_ALIGN_A1_SPECTRAL`、`TRUST_ALIGN_LABRAM_A3` 与官方 `NeuroLM-B+VQ` 已形成 outcome-blind candidate ledger，但未选择唯一 A。A1 spectral 无预训练 checkpoint/项目级 license；LaBraM 和 NeuroLM 仍有单位、通道、adapter 与统一 score API 缺口。v1.7 完成 data card 后仍不选 A、不下载权重；未知 unit 只阻断 unit-sensitive A，而不阻断 stimulus identity/split 的 outcome-blind 建设。
4. **V3 schema**：L1–L3 抽取器、typed-unit evaluator、projection、L4 renderer、匹配器和人工审计方案。
5. **V4 null**：N1 block feasibility/联合置换、N2 共同相位实现、真实数据容差和交换性边界。
6. **V5 statistics**：cal-select/cal-cert 或 simultaneous LTT 的二选一、具体 bound、\(|\Pi|\)、candidate budget、近重复阈值和 calibration size。
7. **V6 selection**：各层候选来源、冻结时点、父子路径、对称 pseudo-real 统计量与 test-time 可用输入。

Codex 或协作 AI 不得猜测上述项目，不得自行放宽 split、改 primary metric、换数据集或在 Gate 失败后加模块救回。

### 8.4 机器可执行 Stop 逻辑

```text
IF project_memory_system != PASS OR repository_audit != PASS: STOP implementation
IF missing(A OR dataset_schema OR split_hash OR semantic_schema OR null_contract): STOP blocker
IF leakage_audit != PASS: STOP all comparisons
IF N1_structural != PASS: forbid randomization-p language
IF Gate_A1(N1 or N2) == FAIL: rename matched corruption; forbid zero/evidence/FDR language
IF candidate_selection_is_not_symmetric: forbid p and Gate_A
IF calibration_selects_and_certifies_with_pointwise_bound_on_same_data: forbid risk-control claim
IF Gate_A == FAIL: route = negative-result/audit; IF only L1 then topic-level route
IF primary(B′) <= primary(B): remove title-level performance claim
IF primary(B′) <= primary(direct-C): remove hierarchical claim
IF primary(B′) <= primary(PMI): remove brain-evidence claim
IF only random split / one seed / one subject: downgrade claim to observed-setting result
IF risk_pass AND M_sem exceeds pre-registered cap: anti-abstention FAIL
```

### 8.5 当前唯一 Next Task

**T5-CODEX：在 `wip2@bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7` 上修复数据准入政策，并从 schema-v3 冻结 5,905-row 分析视图与 data card。**

本任务先激活 v1.7，并新增 `SPEC_V17_REVIEW → S0_DATA_ADMISSION_POLICY_REPAIR → S0_DATA_CARD`。它只能读取仓库中已提交的 schema-v3 manifest/JSONL/correspondence/license/hash 证据，不能重新读取服务器真实 EEG、访问外部来源、重跑 targeted/broad audit 或重 hash 大文件。任务必须保留 full-release diagnostic FAIL，但用显式 exclusion policy 派生 5,905-row analysis view；data card 必须记录 377 个 exclusions、NR3/NR5/NR6 event anomalies、未知 release-native amplitude 和 unit-sensitive use 禁令。修复 auditor 中只列 NR3/NR6 的硬编码回归风险，但不改写 run 007 或 schema-v3 artifacts。完成后 `S0_DATA_CARD=DONE`、`S0_STIMULUS_ID=READY`，然后停止；不得顺手做 split、选择 A、实现模型/null/schema、训练或运行 Gate。精确执行文本见交付 ZIP 根目录 `CODEX_NEXT_TASK.md`。

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

---

## 11. v1.5 研究依据与引用义务

以下只支持协议设计或待核事实，不代表本项目仓库已经具备相应数据、代码或许可。

1. ZuCo 2.0 的官方数据论文报告 18 名参与者与 739 个英文句子，见 [Hollenstein et al., LREC 2020](https://aclanthology.org/2020.lrec-1.18/)。仓库实际文件仍须 V1 审计。
2. COFETT 的 2026 年原始预印本报告 128 通道、teacher-forcing-free 评测与两名完整采集被试，见 [Zhang et al., arXiv:2607.18749](https://arxiv.org/abs/2607.18749)。两名被试不能支持人群泛化。
3. NeuroLM 的模型结构、公开实现与 checkpoint 只能按官方论文/仓库核实，见 [Jiang et al., ICLR 2025](https://openreview.net/forum?id=Io9yFt7XH7)；被列为候选不等于已准入本项目 tensor contract。
4. 风险控制的有限样本主张必须匹配 holdout、loss 和交换性条件，见 [Bates et al., Distribution-Free Risk-Controlling Prediction Sets](https://arxiv.org/abs/2101.02703)；从有限策略集合选择再认证的多重性问题参见 [Angelopoulos et al., Learn then Test](https://arxiv.org/abs/2110.01052)。
5. 多变量 phase-randomized surrogate 应同时考虑 auto- 与 cross-correlation，见 [Prichard & Theiler, Physical Review Letters 73, 951](https://link.aps.org/doi/10.1103/PhysRevLett.73.951)。这支持 N2 的候选算法，不替代真实数据 Gate A1。
6. 随机化 p 必须把预先固定的统计流程应用到置换数据；本项目额外把候选选择纳入对称 pseudo-real 统计量。一般置换框架可参见 [Ramdas et al., arXiv:2204.13581](https://arxiv.org/abs/2204.13581)。
7. NeuroLM 官方代码仓库声明其为 ICLR 2025 官方实现并使用 MIT license，见 [`935963004/NeuroLM`](https://github.com/935963004/NeuroLM)；本项目冻结审计 commit `0cda9876d8ce6ee07ed0c43eee5e9a6f5c24b177`，不是无版本的 `main`。
8. NeuroLM 官方模型仓库列出 `NeuroLM-B.pt`、`NeuroLM-L.pt`、`NeuroLM-XL.pt` 与 `VQ.pt`，见 [`Weibang/NeuroLM`](https://huggingface.co/Weibang/NeuroLM)。本项目只把 B+VQ 作为公共 fallback 候选，官方文件 hash/size 只用于将来下载校验，不等于已准入本地 A。
9. ZuCo 2.0 官方论文给出的公共数据入口是 [OSF `2urht`](https://osf.io/2urht/)；其 [OSF API node](https://api.osf.io/v2/nodes/2urht/) 的 `relationships.license` 指向 license `563c1cf88c5e4a3877f9e96a`，后者名称为 CC-By Attribution 4.0 International。下一 run 必须把精简响应与 hash 保存为本地准入证据。
10. ZuCo 作者团队的后续基准论文给出预处理细节、24 个被排除的 EGI 标签以及 common-average reference，见 [Hollenstein et al., Frontiers in Psychology 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9878684/)；通道顺序与坐标仍须从本地 `EEG.chanlocs` 核对，不能只抄论文。
11. 同一作者团队论文明确说明每个 sentence block 前有 3 个 practice sentences，且所有被试的 block 与句子顺序相同；这支持把每个 `nr_[1-7].csv` 的前三行标作 practice，但精确 block occurrence 仍必须由 18 名被试的 349-slot hash 序列逐位相等来证明，不能仅凭总数推断。
12. 作者维护的 ZuCo benchmark 仓库中，[关于 `sentenceData/rawData` 单位的 issue #5](https://github.com/norahollenstein/zuco-benchmark/issues/5) 仍为 open；2024-04-18 有 repository collaborator 回答“microvolt”，但提问实例明确是 ZuCo 1.0 `task1-SR/resultsZAB_SR.mat`。该回答是重要的 field-level context，却不能在无跨版本/数组同一性证据时直接绑定 ZuCo 2.0 NR 两个发布数组。论文中的 μV 阈值同样不能单独完成 storage binding。

## 12. 第二次迭代状态与变更记录

### 12.1 当前能确认的项目状态

- 远程证据：`main@1b836fe56970d262f4e8f3ae8262fd0abb670dbe`；其父提交 `76504c6bef46664b9fb265cbdba544de9d37da99` 建立项目治理，当前提交同步 `trust_align` 的冻结包环境。
- 独立复核：`python3 -m unittest discover -s tests -p 'test_project_memory.py'` 为 19/19 PASS；`python3 scripts/check_project_state.py` 为 `tasks=35, done=4`；`project_status.py` 与 `git diff --check` exit 0。
- 已完成且只属治理/环境：`SPEC_V12_REVIEW`、`S0_GOVERNANCE_BOOTSTRAP`、`S0_REPOSITORY_AUDIT`、`S0_ENVIRONMENT_SYNC`。
- 当前仓库不存在数据、科学源码、checkpoint 或 result；环境包含科学包不等于 backbone 准入。
- 当前 active blockers：V1–V6；其中近期关键路径只有 V1 数据与 V2 backbone。G1 是本轮新识别的治理连续性缺口。
- 任何示例 ZIP 或 `trust_align` 历史结果中的 DONE、claim、hash、route、metric 仍不可导入。
- 当前禁止：读取历史/test metric、训练、批量下载数据/权重、实现 N1/N2/schema/NC-HSG、运行任何 Gate 或主实验。

### 12.2 本轮治理复核发现

1. 基本状态恢复可用，但项目没有表示“如何解除 blocker”的 READY task，因此合法状态也可能永久停住。
2. 根 `CODEX_NEXT_TASK.md` 已过期；若新 Codex 只按入口恢复，可能重复执行已完成任务。
3. 三个治理 snapshot 在 run 003 被修改，却仍把 `generated_by_run` 留在 run 002；需要显式 revision provenance。
4. validator 的 spec-version 检查硬编码 v1.2，阻断正常版本升级；route lock 的反向约束不完整。
5. `S0_ENVIRONMENT_SYNC` 的证据充分限定为环境，但它不是原始关键路径任务；接受其产物，不把它变成科学准入。

### 12.3 v1.3 相对 v1.2 的实质变更

1. 将 V0 仓库未知关闭到精确远程 commit，并记录独立复核命令。
2. 新增 G1 治理连续性 blocker，以及 `SPEC_V13_REVIEW → S0_INPUT_DISCOVERY_AUDIT` 的可执行解锁路径。
3. 冻结 ZuCo 2.0 NR 为 primary 数据候选、TSR 为任务偏移 robustness；未核 license 前仍不可下载/准入。
4. 冻结官方 NeuroLM-B+VQ 为公共 fallback 候选及其代码/checkpoint commit、hash、size 和预处理事实；真实通道兼容前不可下载/准入。
5. 明确下一轮只做受限本地 source discovery、兼容性矩阵与严格条件准入，不把可用包环境当作 backbone。
6. 要求 validator 支持通用 spec 版本一致性、非空唯一 route lock 和 artifact revision provenance。
7. v1.2 的 `alpha_0`、K、primary metric、N1/N2、Gate、calibration、failure route 与统计单位全部保持不变。

### 12.4 v1.2 相对 v1.1 的历史变更

1. semantic depth 从 L0–L4 改为 L0–L3；L4 保留为受约束 renderer，因此 \(d_i=h_i/3\)。
2. 修正候选选择偏差，置换 p 使用包含候选选择的对称 pseudo-real 统计量。
3. N1 从 per-trial donor 改为 replicate-level 联合块内双射，并新增 block feasibility 前门。
4. N1 无文本 AUC 降级为 checksum；N1 合法性由结构审计决定。
5. N2 primary 候选改为跨通道共同相位增量；AAFT/IAAFT 降为敏感性。
6. calibration 新增 selection/certification 分离或 simultaneous LTT 的硬约束。
7. Cliff gate 从 \(|\delta|\ge0.20\) 修正为方向明确的 \(\delta\ge0.20\)。
8. MDE 统一为 \(\Delta D\ge0.10\)，消除与 0.25 层并列造成的口径冲突。
9. 增加首次仓库治理阶段、机器 Stop 条件和精确 debug 定位表。

v1.2 与 v1.3 的全部修改均发生在任何本项目训练结果或 held-out metric 被本轮读取之前，属于 outcome-blind 规格修订。

## 13. 第三次迭代状态与变更记录

### 13.1 对 `main@250ca9a` 的独立复核

- 远程 `main`/HEAD 为 `250ca9a67cf386784005a1edbbfe502d7df6f192`，commit message 为 `chore: harden context and audit input sources`；相对 `1b836fe` 新增/修改 21 个文件。
- 本地干净 clone 中，34 个 project-memory tests、7 个 input-audit tests、validator、status 和 `git diff --check` 全部通过；`PROJECT_STATE.yaml` 为 stage 0 BLOCKED、38 tasks、7 DONE、无 READY task。
- 已完成工作只证明治理加固和 outcome-blind 输入发现可复现：本地 ZuCo 2.0 NR/TSR 树、三个 A 候选及官方 NeuroLM metadata 已盘点；没有数据准入、A 选择、训练、Gate 或结果。
- `artifacts/admission/input_source_inventory.yaml` 为约 1.9 MB、54,129 行、8,020 entries 的全量快照，其中 ZuCo 2.0 有 1,457 entries。它可保留作 run 004 证据，但不得重复生成或作为日常 active inventory；下一 run 只产出紧凑的 NR 定向 manifest。

### 13.2 新发现的治理与审计缺口

1. 根 `AGENTS.md` 明确写 v1.2 为 active SPEC，其他入口写 v1.3；按 `AGENTS.md` 自身规则应报告 `STATE_SPEC_CONFLICT`。现有 validator/test fixture 没物化或检查 `AGENTS.md`，所以“全绿”不代表入口一致。
2. 宽扫描器先以路径含 `datasets` 判定 `HASH_SKIPPED_DATA_FORMAT`，导致 ZuCo 官方目录内的两个小型 `.py` reader 也未 hash/read；这不是安全违规，但说明宽扫描不能替代定向准入。
3. 根 `CODEX_NEXT_TASK.md` 把“六项数据准入条件”误写成“v1.3 section 6.2”，而 SPEC §6.2 实为公平性合同。下一 run 必须把六项条件写进 task acceptance 或明确引用 run 004 handoff §6.2，避免伪引用。
4. run 004 将“用户另给 license”写成最小动作，但官方 OSF API 已提供可识别 license；该 blocker 结论应撤销，不要求用户重复提供已有公共证据。

### 13.3 v1.4 的 outcome-blind 研究更新

1. 官方 OSF node `2urht` 的 `relationships.license.data.id` 为 `563c1cf88c5e4a3877f9e96a`；对应官方 API 的 license name 为 `CC-By Attribution 4.0 International`。该证据关闭“无可识别公共 license”，但本地副本同源性仍须以小文件 hash/路径树核对。
2. 官方 OSF `scripts/python_reader` 只有两个文件：`read_matlab_files.py`（1,610 bytes，SHA256 `daf147dee64cf53ae55050a3d19d0ea37d8811057cd9de3cfb2bc7f29fb91712`）和 `data_loading_helpers.py`（10,137 bytes，SHA256 `90e3bab7d082891b4b53fcb154286d8a73eea0f3fa89a312176025f035cfa71c`）。本地文件 size 与之相同，下一 run 只需算本地 hash 完成强同源核对。
3. ZuCo 团队 2023 benchmark 说明最终使用 105 EEG electrodes、common-average reference，并给出排除标签 `E1,E8,E14,E17,E21,E25,E32,E48,E49,E56,E63,E68,E73,E81,E88,E94,E99,E107,E113,E119,E125,E126,E127,E128`。这是物理核对预期，不替代本地 `EEG.chanlocs`。
4. 当前本地 NR inventory 含 18 个 summary MAT、126 个 block EEG、126 个 corrected ET 和 7 个 task-material CSV；每个受试者 349 sentence slots，summary 中 `content/rawData/word` 字段存在。官方 OSF metadata 列出的 18 个 NR summary 合计 `34,591,109,519` bytes，每个文件都带 SHA256，且 18 个本地 size 已逐一与官方一致。下一 run 应把 admitted input scope 限定为这 18 个 NR summary MAT、7 个 NR material CSV、2 个 reader 及恢复 metadata 所需的代表性/全体 NR preprocessed headers，只补 local SHA256，不 hash 整个 117 GB 下载归档或 TSR/raw 数据。
5. A 的 outcome-blind 选择仍不成熟：A1 spectral 是无 checkpoint 的随机初始化前端；LaBraM 与 NeuroLM 均缺本地物理接口闭合。下一轮只完成数据准入并回传 channel/unit/reference 事实，随后由 ChatGPT/作者选 A。

### 13.4 本轮没有改变的内容

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、subject-cluster inference、无 teacher forcing、Gate A1→A→B、calibration 二选一和所有失败路线全部保持不变。v1.4 仍在任何 held-out/test metric 或训练结果被读取前冻结。

## 14. 第四次迭代状态与准入纠错合同

### 14.1 对 `main@d6751ea` 的独立复核

- 远程 `main`/HEAD 为 `d6751eadd96b2f651e5dbd1bfd5366679688ce4d`，commit message 为 `fix: guard active spec and admit ZuCo NR metadata`；worktree clean。
- `python3 -m unittest discover -s tests -p 'test_project_memory.py'` 为 38/38 PASS，`test_audit_input_sources.py` 为 8/8 PASS，`check_project_state.py`、`project_status.py` 与 `git diff --check` 均 exit 0。当前独立环境缺少 `h5py`，所以没有把本地未运行的 8 个 targeted-audit tests 冒充为复现；run 005 的服务器记录称其为 PASS。
- run 005 正确完成 active-SPEC guard、许可证与 27/27 local↔OSF SHA256 核对，也正确恢复 18 名被试、349 slots、126 个 NR preprocessed blocks、105 通道、稳定坐标、500 Hz、Cz acquisition reference 与 common-average processed reference。
- 以上成功不支持 run 005 的两句 active 结论：`0 missing assignments` 和 `condition 3 only fails on unit`。脚本实现与自身 artifacts 已反证这两句。

### 14.2 已由 committed artifacts 证明的缺口

| 缺口 | 可复现事实 | active 裁决 |
|---|---|---|
| EEG 占位符被算作 present | 6,282 行中 367 行 `raw_shape=[1,1]`、axis unresolved，且全局 `raw_nonfinite_count=367`；脚本只用 `size>0` 判断 present，所以它们全被写成 `raw_data_present=true, missing_reason=null` | 这 367 行必须标成 non-finite invalid placeholder，而不是 EEG present；逐 subject/block 计数进入 ledger |
| 单样本序列未单列 | 另有 4 行 `raw_shape=[1,105]`，均在 YTL；它们轴向合法但只有一个 sample | 标成 `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED`，不得与可用多样本序列混计；在 source/adapter 合同决定前不准入模型 |
| block occurrence 未恢复 | 180 行因 5 个跨 block 重复文本被写成 `block=null` | 文本 hash 只定义 stimulus group，不能定义 occurrence；必须用材料行顺序恢复 block/line |
| event 只验字段名 | condition 3 只检查 `latency`/`type` 名称存在，没有读取值域、有限性、单调性、边界或句子事件映射 | 在未形成 event semantic contract 前不得声称 event/trial recoverable |
| summary layer 被错误外推 | `summary_raw_data_layer` 由另一个 preprocessed EEG 文件的 `processed_reference` 直接赋值，没有证明 `sentenceData/rawData` 来自或等于该层 | summary `rawData` 与 `EEG/data` 的 layer/reference/unit 必须分别有 source binding；不能由邻接文件推断 |
| condition 3 谓词不完整 | 当前谓词只合取 channel/coordinate、500 Hz、reference、event field names、唯一 unit | 即便未来发现 unit，旧谓词也会在 367 invalid cells、180 null blocks 和未知 event semantics 下错误 PASS；必须改成显式子谓词 ledger |

367 个 invalid placeholders 的 subject 计数为：YFR 106、YAC 102、YRH 52、YAK 51、YFS 13、YRK 10、YMD 7、YLS 6、YRP 6、YSL 6、YDR 3、YMS 3、YSD 1、YTL 1。按可恢复 block occurrence 计数为：block 1/2/3/4/5/6/7 分别 9/121/52/39/67/60/19。该计数来自已提交 hash/shape ledger，不读取 EEG 值或结果指标。

### 14.3 block occurrence 的确定性恢复

每个 task-material CSV 有 53/53/54/53/53/52/52 行，共 370 行。官方 procedure 说明每个 block 前有 3 个 practice sentences。对 7 个 CSV 各排除前 3 行后得到 50/50/51/50/50/49/49 行，共 349 行。把它们按 block 1→7、原 line order 拼接后：

1. 与每名被试 `slot=1..349` 的 normalized stimulus SHA256 **349/349 逐位相等**；
2. 18 名被试全部成立，合计 6,282/6,282；
3. 因此重复文本仍共享 `stimulus_sha256`，但每次呈现的 `block_id`、`material_line` 与 occurrence 可由 slot 唯一恢复；
4. 下一脚本必须把“逐位全等”写成 fail-closed assertion。只要任一被试、任一 slot 不等，block mapping 整体 FAIL，不得退回 hash-to-set 猜测。

### 14.4 修正后的 EEG cell 与 condition-3 合同

每行必须同时记录 `raw_reference_present`、`raw_nonempty`、`raw_numeric`、`raw_shape`、`raw_axis_contract`、`raw_finite_count`、`raw_nonfinite_count`、`eeg_cell_state` 与 `missing_or_exclusion_reason`。冻结最小状态：

- `VALID_FINITE_MULTISAMPLE`：numeric、shape `[T,105]`、`T>=2`、全部 finite；
- `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED`：shape `[1,105]` 且 finite；
- `NONFINITE_PLACEHOLDER`：有引用/元素但没有可用 finite time series，包括已见 `[1,1] NaN`；
- `PARTIAL_NONFINITE`、`EMPTY`、`MISSING_REFERENCE`、`INVALID_AXIS`：按名字 fail closed；
- 不能因引用存在或 `size>0` 就清空 missing reason。

condition 3 只能在以下 machine-readable 子谓词全部 PASS 时 PASS：

1. subject/session/task 与 18×349 slot 完整；
2. practice-excluded material sequence 与所有 subject slot 逐位相等，block/line/occurrence 无 null；
3. summary expected fields 完整，所有 EEG cell 均被互斥分类，missing/exclusion counts 与逐行 ledger 一致；
4. channel order、coordinate、sampling、acquisition reference、processed reference 全体一致；
5. event 值域、latency 合法性及其与 block/trial/sentence 边界的语义映射有物理或 release-source 证据；
6. summary `sentenceData/rawData` 与 preprocessed `EEG/data` 各自的 layer、reference 与 physical unit 有 release-applicable binding；
7. 所有不一致文件和例外均已枚举，且 data-card exclusion policy 已冻结。

缺失 cell 本身不必使数据集永久不可用，因为 `S0_DATA_CARD` 本来要求枚举 missing cells；但在状态分类、排除规则和有效样本数未冻结前，不能把它们称为“0 missing”或准入。四个单样本 cell 暂不猜测原因，也不采用 200-sample 等 backbone 特定阈值。

### 14.5 unit/source 研究结论与停止线

ZuCo 作者论文明确以 μV 给出预处理阈值，并明确 processed data 使用 common-average reference；这支持 `paper_intended_voltage_scale=µV`。官方发布数组没有可读 unit attribute。作者维护仓库 issue #5 的 collaborator 答复给出 microvolt，但提问实例属于 ZuCo 1.0 SR；在未证明跨版本或当前数组同一性前，它仍是 non-binding context。通用 EEGLAB 习惯也依赖 import format。因此 active ZuCo 2.0 NR storage binding 仍为 `UNRESOLVED`。

下一 run 只允许在 OSF wiki/README、小型 release scripts、MAT attrs/header、作者论文或作者公开答复中寻找绑定。可接受证据必须明确指向实际发布的 `sentenceData/rawData` 和/或 `EEG/data`；论文阈值、图轴、数值量级、另一数据集或一般工具默认均不能单独把 unit 改为 verified。若 bounded search 无结果，应记录 negative evidence 与 source hashes 后停止，不做更广搜索。

### 14.6 v1.5 下一状态

- 新增 `SPEC_V15_REVIEW` 与 `S0_ZUCO2_NR_ADMISSION_REPAIR`；后者完成纠错审计即可 DONE，不等于 admission PASS。
- run 005、旧 manifest/report 保留不可变；修正版使用 schema version 2、新文件或明确 supersession 字段，不静默覆盖历史证据含义。
- 预期 `S0_DATA_CARD` 仍 BLOCKED，除非 corrected condition 3 与其余五项全部 PASS。若 unit/layer/event 任何一项 unresolved，就不生成 data card。
- `S0_A_INTERFACE`、训练、N1/N2、semantic schema 和所有 Gates 继续 BLOCKED；不得利用本次纠错提前选择 backbone。

### 14.7 v1.5 未改变的科学决定

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、subject-cluster inference、无 teacher forcing、Gate A1→A→B、calibration 二选一和全部失败路线保持不变。v1.5 的所有新事实均来自 outcome-blind 物理 metadata、hash、shape 与代码路径审计，没有读取 held-out/test metric 或训练结果。

## 15. 第五次迭代状态与 event-segment correspondence 合同

### 15.1 对 `main@c807a2e` 的独立复核

- 远程 `main` 为 `c807a2e83fad02763193a6c1db81fd26db19fd97`，commit message 为 `fix: repair ZuCo NR admission predicates`，worktree clean。
- 独立环境复现 `test_project_memory.py` 38/38、`test_audit_input_sources.py` 8/8、validator、status 与 `git diff --check`。独立环境仍缺 `h5py`，所以 schema-v2 targeted tests 未在本地冒充复现；run 006 记录服务器为 12/12 PASS。
- schema-v2 的 6,282-row ledger、349 occurrence mapping、367/4/5,911 cell classes、六项 `PASS,PASS,FAIL,PASS,PASS,PASS` 与 data-card absence 相互一致。run 006 保守地停止是正确的。
- 官方 OSF Data format wiki 内容 SHA256 为 `3cc1b85c021042d93db4f077145b84e6c3beebad3a474f6781746a6a40dbdbb4`，明确给出 task-1 的 `10/11` 与 `12/13/15` 语义；该 hash 与 run 006 source audit 一致。

### 15.2 run 006 仍缺的可证伪环节

| 缺口 | committed evidence | v1.6 裁决 |
|---|---|---|
| control-sentence occurrence 未进入 event 合同 | 每名被试聚合均为 `10=11=303`、`12=13=15=46`，`303+46=349`；现有代码只对 `10→11` 做开闭状态机 | 句子 occurrence 必须是 `10→11` 普通句与 `12→13` control 句的有序并集；`15` 是 control-question response，不是第 350 个句子 |
| 两个 YTL anomaly 只给文件名 | 现有 manifest 只写 pair boolean，没有 occurrence ordinal、相邻 code class 或可复现修复/排除边界 | schema-v3 必须给 sanitized anomaly ledger；只有 source-defined pairing或 exact segment identity 能修复，不能按最近邻猜 |
| summary layer/reference 没有做物理同一性测试 | 现有脚本只读取两类数组 metadata；未比较 event-defined `EEG/data` slice 与 `sentenceData/rawData` | 允许 chunked equality，不输出值；全局唯一 exact convention 才能把 summary layer/reference 绑定到 preprocessed layer/reference |
| source verdict 由代码常量生成 | `SOURCE_RETRIEVED_AT_UTC`、外部 content hashes 和 verdict 写死在 Python 函数中，CLI 没有 release-source evidence 输入 | 外部证据必须进入 versioned cache，由脚本验证 URL、hash、locator 与 applicability 后导出 verdict；常量只能是 schema/允许值，不得是事实 verdict |
| all-PASS 分支未实现 | `main()` 在 admission PASS 时抛出 `DATA_CARD_GENERATION_NOT_IMPLEMENTED_FOR_UNEXPECTED_ALL_PASS_RESULT`，manifest 又固定 `data_card_generated: false` | 必须实现并测试真正的条件式 data card；当前真实 run 是否 PASS 仍由证据决定 |
| ledger consistency 对缺文本的合成边界不严 | `valid_count` 按 cell class 计算，而 summary 中缺文本只把 row 的 `admissible_sentence_eeg` 改 false | valid/excluded 汇总必须来自最终 row admission flag，并 assert 与 cell class、content policy、segment policy 一致 |

### 15.3 冻结的 task-1 event occurrence contract

1. 对每个 block 按 latency 顺序读取 event `type`，只允许官方映射中的句子/控制问题 code 和已枚举的 block marker；未知 code 保留 count 与 hashed class，不进入句子配对。
2. `10` 打开 `ORDINARY_SENTENCE`，只能由后续 `11` 关闭；`12` 打开 `CONTROL_SENTENCE`，只能由后续 `13` 关闭。两个状态不能嵌套或交叉。
3. `15` 必须发生在对应 control sentence 的 `13` 之后、下一句 onset 之前；它记录 control-question answer，不生成新 occurrence。
4. 每个 subject 的七个 block 合计必须正好产生 303 个 ordinary 与 46 个 control occurrences，共 349。每个 block 的总 occurrence count 必须等于材料合同的 `50,50,51,50,50,49,49`。
5. occurrence 按 block 1→7、onset latency 递增，与已经证明的 material slot 1→349 对齐。该对齐依赖 shared order 与 count，不使用刺激文本或 EEG 值。
6. 任何 orphan finish、nested onset、wrong finish class、missing `15`、extra `15`、fractional/越界 latency 或 block count mismatch 都生成精确 anomaly；不得静默忽略。
7. 两个 YTL 文件必须由该完整状态机重新判定。若 anomaly 只存在于旧的 `10/11` 投影而在完整 `10/11 + 12/13/15` 合同下消失，记录 `OLD_PROJECTION_FALSE_ANOMALY`；否则保留 FAIL。

schema-v3 每个 occurrence 至少记录：

```text
subject, block, block_occurrence_index, global_slot, material_line
sentence_class, onset_code, finish_code, control_response_present
onset_latency_valid, finish_latency_valid, event_pair_state
summary_cell_state, summary_samples, segment_samples
segment_correspondence_state, final_admission_candidate, exclusion_reason
```

不得提交 event latency 数值、EEG 数值或刺激原文；可提交 code、计数、ordinal、shape 与 verdict。

### 15.4 summary↔preprocessed segment correspondence

目标仅是核对两个 release arrays 是否为同一物理层，不做信号分析或性能选择。

1. `EEG/data` 只按 occurrence window 分块读取；`sentenceData/rawData` 只按对应 slot 的引用分块读取。禁止整体载入 block 或 summary。
2. 方向由已验证 shape 固定为 preprocessed `[channels,samples]` 与 summary `[samples,channels]`；只允许 transpose，不允许重参考、滤波、缩放、插值、标准化或 tolerance-based 近似。
3. latency 使用 EEGLAB one-based 语义。可预注册一个很小的 endpoint convention grid，例如 finish exclusive 与 finish inclusive；grid 在真实比较前冻结。只能选择一个对所有 comparable rows 全局一致且唯一 exact-match 的 convention，不能逐行挑选或最大化 match rate。
4. equality 为 dtype-aware finite exact equality；若 dtype 不同，可额外做无损 canonical numeric equality，但两种 verdict 分开。不得用相关系数、高相关、量级相似或均值方差作为 layer binding。
5. `NONFINITE_PLACEHOLDER`、`FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED` 与其他非 admissible cell 进入 exclusion ledger，不要求 segment equality；但其 occurrence/event contract 仍须可恢复。
6. 对 5,911 个 finite multisample rows，输出 overall/by subject/by block 的 `EXACT_MATCH`、`SHAPE_MISMATCH`、`VALUE_MISMATCH`、`EVENT_UNRESOLVED` counts。只提交计数与状态，不提交 participant waveform hash 或差值。
7. 只有所有 final-admission candidates 在同一个全局 convention 下 exact match，`summary_layer_bound` 和 `summary_reference_bound` 才能继承 preprocessed `EEG/data` 的 layer/reference。否则保持 FAIL，并列出最小路径/ordinal blocker。
8. exact correspondence 只能证明两数组数值层相同，不能单独证明 physical unit。`preprocessed_unit_bound` 与 `summary_unit_bound` 仍须独立 author/release evidence，或由未来 SPEC 明确批准 unit-invariant interface；本 run 不做后者。

### 15.5 release-source evidence cache

新增紧凑、可复核的 `zuco2_nr_release_source_evidence.yaml`。至少包含 source URL、retrieval UTC、raw response SHA256、normalized claim SHA256、source type、release applicability、array/event binding、短 locator 与 verdict。允许的来源限于 v1.5 已列的 OSF wiki、ACL paper、Frontiers/PMC paper和作者维护 issue/comments；不保存整篇文章或 license legal text。

targeted auditor 新增 `--release-source-evidence`，并执行：

- URL 必须在 allowlist；
- hash、claim schema 与 applicability 必须存在；
- event mapping 从 cache claim 读取，不从 `EVENT_TRIGGER_MAPPING` 事实常量直接判 PASS；
- unit/layer verdict 从 local evidence 与 cache claims 合成；
- cache 缺失、tamper 或 scope 不足均 fail closed；
- retrieval timestamp 只在 provenance 外层，不参与 scientific ID，保证核心输出 byte-stable。

### 15.6 condition 3 与 data-card 分支

保留 v1.5 全部 condition-3 子谓词，并新增：

```text
ordinary_control_event_partition_complete
control_response_contract_valid
event_occurrence_count_exact
event_to_material_slot_alignment_exact
segment_convention_global_unique
segment_correspondence_complete
source_evidence_cache_valid
```

`event_semantics_bound` 只能在 source mapping 与完整 physical occurrence contract 同时 PASS 时 PASS。`summary_layer_bound`、`summary_reference_bound` 只能由 exact correspondence 升级。unit predicates 独立。

六项全 PASS 时，脚本必须生成 `artifacts/data_card.yaml` 与 `reports/data_card.md`，明确最终 admitted/excluded counts 与数组 contract；不得继续 A-interface。任一 FAIL 时，不生成 data card，`S0_DATA_CARD` 保持 BLOCKED，并把失败子谓词完整写进 active blocker。

### 15.7 v1.6 下一状态

- 新增 `SPEC_V16_REVIEW` 与 `S0_ZUCO2_NR_SEGMENT_CORRESPONDENCE`；bounded run 完成后后者 DONE，不等于 data admission PASS。
- run 005、run 006 与 schema-v1/v2 artifacts 保持不可变；schema-v3 使用新文件名并明确 supersession 边界。
- 若 layer/reference/event 通过而 unit 仍 FAIL，active blocker 必须缩为 unit predicates，并生成一个未发送的精确作者询问草稿；不得自动联系作者。
- 若任何 event/segment predicate FAIL，保留最小物理路径/ordinal blocker；不得回退到广泛搜索或相关性猜测。
- `S0_A_INTERFACE`、split、N1/N2、semantic schema、训练和所有 Gates 均继续等待 data card。本轮不选择 A。

### 15.8 v1.6 未改变的科学决定

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、subject-cluster inference、无 teacher forcing、Gate A1→A→B、calibration 二选一和全部失败路线保持不变。v1.6 不读取 held-out/test outcome，不运行任何模型，也不把 event/segment audit 当作实验结果。

## 16. 第六次迭代状态与 exclusion-tolerant 数据准入合同

### 16.1 对 `main@bf958fe` 的独立复核

- 远程 `main` 为 `bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7`，commit message 为 `fix: verify ZuCo NR segment correspondence`；公开 checkout 在复核前为 clean。
- 独立环境复现 `test_project_memory.py` 38/38、`test_audit_input_sources.py` 8/8、validator 与 status；validator 为 `tasks=45, done=14`。独立环境没有 `h5py`，所以没有把未运行的 targeted tests 冒充为复现；run 007 记录服务器为 20/20 PASS。
- 接受 run 007 的物理证据：每名被试 `303` 个 ordinary + `46` 个 control occurrences；5,911 个 finite-multisample cells；全局唯一 finish-inclusive convention；5,905/5,905 event-valid segments exact；summary layer/reference 绑定到 preprocessed common-average layer；六项仍为 `PASS,PASS,FAIL,PASS,PASS,PASS`；没有生成 data card。
- 这些证据支持一个冻结的可用子集，但不支持“所有发布 row 都有效”、当前数组单位已知、任何 backbone 已兼容、或任何科学 Gate 已通过。

### 16.2 run 007 的 active-state 缺口

| 缺口 | committed evidence | v1.7 裁决 |
|---|---|---|
| YTL active 叙述漏掉 NR5 | schema-v3 `files_with_semantic_anomaly` 列出 NR3、NR5、NR6；event occurrence ledger 中 6 个 finite-multisample `EVENT_UNRESOLVED` 分布为 block 3=`1`、block 5=`1`、block 6=`4`；但 `ytl_anomaly_verdicts` 的路径集合被代码硬编码为 NR3/NR6，run/state/handoff 也只写 NR3/NR6 | 旧 artifact/run 保持不可变；v1.7 active review、data card 和 state 必须写 NR3/NR5/NR6。auditor 的 future-summary 路径必须从所有 YTL semantic-anomaly files 动态产生，并有 NR5 回归测试 |
| 数据准入把“文档完整”误写成“零缺口” | `S0_DATA_CARD.acceptance` 明确要求枚举 exclusions/missing cells，并未要求所有 row 有效；schema-v3 已给每一行冻结 final flag 与非空 exclusion reason | data card 应记录可用范围和限制，不应因已枚举、已排除的坏 row 永久不存在 |
| unit blocker 的作用域过宽 | unit 未绑定会使 NeuroLM 等 µV-sensitive adapter 不安全，但 stimulus ID、subject-stimulus assignment、split grouping 与 data-card 文档本身不依赖把 release amplitude 命名为 µV | unit 写成 `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`；禁止 unit-sensitive conversion/model admission，但不再阻断 data card、stimulus identity 或 split construction |
| full-release audit 与 analysis-view admission 混为一个布尔值 | strict condition 3 因 unit 和 10 个 event-invalid occurrences FAIL；与此同时，5,905-row final flag 已合取 content、finite multisample、valid event occurrence 与 exact segment | 保留 strict full-release diagnostic `FAIL`；另建 machine-readable analysis-view admission，只有后者决定 data card 与可用行 |

该修订发生在任何训练、held-out/test outcome、模型比较或 Gate 之前；它不根据性能放宽协议，而是修复治理语义。数据文档的目的本来就是把 composition、provenance、recommended use 与 limitations 暴露给下游，而不是宣称数据无缺失。

### 16.3 冻结分析视图

输入只能是 run 007 已提交的 schema-v3 artifacts；不得为本合同重新读取真实 EEG。

```text
all physical subject-slot rows                         6,282
VALID_FINITE_MULTISAMPLE cells                        5,911
analysis-view admitted rows                           5,905
analysis-view excluded union                            377
  NONFINITE_PLACEHOLDER                                 367
  FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED                    4
  additional finite-multisample EVENT_UNRESOLVED          6
```

四个 single-sample rows 同时落入 event-invalid 集合，所以排除 union 不是各原因简单相加。builder 必须由逐行 `final_admission_candidate` 重算 union 并断言 `5905+377=6282`；不得用 aggregate 相减掩盖重叠。

analysis-view row 必须满足以下合取：

```text
content_present
AND eeg_cell_state == VALID_FINITE_MULTISAMPLE
AND event_occurrence_valid
AND segment_correspondence_state == EXACT_MATCH
AND final_exclusion_reason is null
```

输出只保留可定位与复现所需的非敏感字段：subject/session/task/block/slot/material line/occurrence ID/stimulus SHA256、shape/length、channel count 与 source locator。不得写 stimulus 原文、event latency、EEG 数值、waveform hash 或 outcome。

### 16.4 v1.7 数据准入语义

必须同时保存两个结论，禁止互相覆盖：

1. `full_release_diagnostic.status=FAIL`：原样引用 schema-v3 的 failed subpredicates；说明 unit 未绑定、NR3/NR5/NR6 有 event anomalies。该结论用于数据质量与 future repair，不决定已冻结子集是否可用。
2. `analysis_view_admission.status=PASS`：只有在 6,282 行全部分类、5,905 admitted rows 全部满足上节合取、377 exclusions 全有理由、source/license/hash/assignment 可追溯且无 outcome 读取时成立。

六项数据准入的 condition 3 改成“可复现 analysis view、完整 exclusion ledger、已知/未知 metadata 明示”，不再要求 full release 的每个 row 或每个 unit predicate PASS。data card 必须显式写：

- `physical_unit_status: UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`；
- `unit_inference_performed: false`；
- `unit_sensitive_use: PROHIBITED_UNTIL_S0_A_INTERFACE`；
- admitted/excluded counts 与 exclusion overlap；
- event anomaly files 为 NR3、NR5、NR6；
- 18 subjects、1 session、NR task、349 slots/subject、105 channels、500 Hz、Cz acquisition reference、common-average processed reference、finish-inclusive exact segment convention；
- 27/27 OSF identity evidence复用 run 005，不能声称本轮重 hash；
- intended use 仅限未来严格 split 后的 NC-HSG 协议，不能把 data-card PASS 外推为 model/Gate PASS。

### 16.5 blocker 与任务图更新

新增：

```text
SPEC_V17_REVIEW
  -> S0_DATA_ADMISSION_POLICY_REPAIR
  -> S0_DATA_CARD
  -> S0_STIMULUS_ID (READY, 本 run 不执行)
```

`S0_DATA_CARD` 的产物增加 versioned 5,905-row analysis-view ledger/summary。`B_V1_DATA_NOT_PRESENT` 在 analysis-view/data-card 验证后关闭；新建 `B_V1_UNIT_UNBOUND_FOR_UNIT_SENSITIVE_A`，只阻断 `S0_A_INTERFACE`、`S0_A1_FRONTEND`、`S0_A1_ADMISSION` 与任何需要 µV conversion 的 candidate，不得阻断 `S0_STIMULUS_ID` 或后续纯身份/split 工件。`B_V2_BACKBONE_NOT_PRESENT` 继续阻断 A。

最终 active state 应为 stage 0 `READY`、`last_completed_task=S0_DATA_CARD`、`recommended_next_task=S0_STIMULUS_ID`。如果 committed schema-v3 输入 hash、行数、final flag、exclusion reason、NR5 anomaly 或任一 data-card acceptance 不一致，则 fail closed，保持 `S0_DATA_CARD=BLOCKED`，不得修改期望值迎合现状。

### 16.6 下一轮的 A 研究边界

NeuroLM 官方预处理明确要求 200 Hz、0.1–75 Hz、50/60 Hz notch 和 µV，因此当前未知 unit 仍足以阻断其直接准入。v1.7 不用跨版本 issue 回复把 ZuCo 2.0 NR 强行命名为 µV，也不下载 NeuroLM/LaBraM 权重。data card 完成后，ChatGPT/作者应优先比较：

1. 能直接接受 `release-native amplitude`、在 outer-train 内冻结尺度归一化且保留 105-channel contract 的原生 spectral frontend；
2. 需要 µV 与 channel adapter 的 NeuroLM/LaBraM 候选。

选择标准只允许兼容性、许可、复现性、改造量和计算成本，不得读取 test/held-out performance。v1.7 本身不选择 A。

### 16.7 v1.7 未改变的科学决定

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、subject-cluster inference、无 teacher forcing、stimulus-disjoint split、Gate A1→A→B、calibration 二选一和全部 failure routes 保持不变。v1.7 不读取 held-out/test outcome，不实现科学模型，不训练，也不运行 Gate。
