# RC-HSG 小论文统一规格（A1 full outer-train admission 版 v2.5，2026-08-24）

> **v2.5 single-pass full outer-train A1 admission freeze.** 本版本完整继承 v2.4 已通过的
> early Regime-I split/data/A-path leakage firewall、v2.3 的 107-row bounded real frontend
> evidence、44-row short no-read 路由、joint split、test lock 与 RC-HSG 科学重构；以本文
> §24 冻结 `S0_A1_ADMISSION` 的单次 streaming read、run-014 evidence reuse、full-frontend
> inference、metadata-only ledger、确定性三镜像输出、B_V9 closure 和 run-016 状态迁移。
> 发生冲突时，§24 对 full outer-train admission 具有最高权威；§23 的 early leakage PASS、
> §22 的 loader/panel 证据、§§20–21 的 RC-HSG/A-interface 决定和 §§14–19 的物理事实保持
> 有效。不得重复读取已验收的 107-row panel，也不得读取 short/cal/test arrays。

> **v2.4 no-new-real-value A-path leakage-audit freeze.** 本版本完整继承 v2.3 已通过的
> 107-row bounded real A-frontend self-check、44-row short no-read ledger、3,390-row 未读边界、
> joint split、test lock 与 RC-HSG 科学重构；以本文 §23 冻结 `S0_LEAKAGE_AUDIT` 的唯一
> 证据边界、机械断言、负向 mutation tests、确定性产物和 run-015 状态迁移。发生冲突时，
> §23 对 early split/data/A-path leakage audit 具有最高权威；§22 的真实值读取结果与完整
> admission 边界、§§20–21 的 RC-HSG/A-interface 决定、§§14–19 的物理事实保持有效。
> 本审计不得打开 production HDF5，也不得重跑真实 frontend validator；后期完整 method
> leakage 仍只由 `S0_METHOD_LEAKAGE_AUDIT` 决定。

> **v2.3 bounded real-frontend self-check freeze.** 本版本完整继承 v2.2 已实现的
> clean-room A interface、5,905-row population、73-row forced-L0 路由、joint split、
> test lock 与 RC-HSG 科学重构；以本文 §22 冻结 `S0_A1_FRONTEND` 唯一允许的真实 EEG
> 读取范围和验证算法，并把早期 data/A leakage audit 与尚未具备实现前提的后期 method
> leakage audit 拆开。发生冲突时，§22 对真实数组读取白名单、审计面板、loader、数值/
> mask/device 检查、产物、任务依赖和 run-014 范围具有最高权威；§§20–21 的其余决定、
> §§14–19 的物理事实及旧 run provenance 保持有效。

> **v2.2 outcome-blind A-interface freeze.** 本版本完整继承 v2.1 已激活的
> RC-HSG 科学重构、数据治理、5,905-row analysis view、342 stimulus groups、joint
> split、test lock、subject-macro population 与 reference/calibration 失败路由；以本文
> §21 冻结 `S0_A_INTERFACE` 的唯一实现合同，并纠正“短于 500 samples 就从总体
> fail admission”的歧义。发生冲突时，§21 对 A 的输入轴、归一化、频谱、窗口、模型、
> 短片段路由、任务依赖和 run-013 范围具有最高权威；§20 的其余 RC-HSG 决定继续有效，
> §§14–19 的物理事实不变。v2.1 与 run 012 保持不可改写 provenance。

> **v2.1 author-level redesign freeze.** 本版本在任何 semantic outcome、held-out
> prediction、calibration result 或 test value 被读取之前冻结。它完整继承 v2.0
> 的数据治理、5,905-row analysis view、342 stimulus groups、确定性 joint split、
> test lock、subject-macro population、无 teacher forcing、无 test retrieval 与
> provenance 纪律；但以本文 §20 取代旧 §§0.2–10 中以 `W_l` evidence increment
> 和 `Gate A1 → Gate A → Gate B` 为核心的科学解释与任务依赖。发生冲突时，
> 数据、identity 与 split 的物理事实以 §§14–19 为准，科学问题、方法、Gate、
> baseline、失败路由与下一任务以 §20 为准。旧文字只作版本 provenance，不得
> 被实现者重新激活。

> **工作标题（待结果冻结）**：*Reference-Calibrated Hierarchical Semantic Generation for Reliability-Aligned EEG-to-Text Generalization*  
> **中文标题（待结果冻结）**：面向可信泛化对齐的参照校准层级 EEG-to-Text 生成

本文件继承 v1.2–v2.4 的算法审查、风险纪律、仓库治理、输入准入、stimulus
identity/grouping、run-011 joint-split/population 证据、run-012 RC-HSG activation 与
run-013 synthetic A-interface、run-014 bounded real-frontend、run-015 early leakage evidence。
它是论文、实验和实现的共同合同，不是结果报告。§12–§19 是不可改写的历史/物理证据；
§20 是 RC-HSG 科学重构；§21 是 synthetic A-interface 与短片段路由；§22 是真实
frontend 自检与 leakage 分层；§23 是 early A-path leakage audit；§24 是当前 full
outer-train A1 admission 与下一动作的权威增量。Codex 只负责实现已冻结决定，
不得重新研究 reference priority、feature/model family、split、Gate、backbone、短片段
处理、真实数据审计抽样策略、leakage 证据范围或 full-admission scan policy。

> **版本权威**：v2.5 是下一次 Codex 导入后应激活的 SPEC。导入前远程
> `main@07c37b3bb77c3cf396116078b64687dcebb9ee03` 已完成 run 015 及 audit CLI executable
> mode correction，当前恰有 71 tasks、35 DONE、8 SKIPPED、27 BLOCKED，唯一 READY/推荐
> 任务为 owner=`CODEX` 的 `S0_A1_ADMISSION`。下一 run 只实现 §24：复用 run-014 的
> 107-row PASS，单次流式读取剩余 3,390 eligible outer-train arrays，形成全部 3,541-row
> outer-train ledger，关闭 B_V9，并以唯一 READY `S0_N1_BLOCK_FEASIBILITY` 停止；不得
> 重读 panel、读取 short/cal/test、训练、计算 outcome/power summary、执行 N1/N2 或 Gate。

---

## 0. 综合分析与冲突裁决

### 0.1 输入文件

| 标识 | 文件 | 用途 |
|---|---|---|
| S1 | `NC_HSG_Paper_Spec.md` | 详细版：Gate A1、零对照合同、主表、执行合同与下一任务 |
| S2 | `NC_HSG_Paper_Spec_v1.md` | 前序定量版：核心命题、主指标建议、简化执行顺序与失败路由 |
| S3 | `NC_HSG_to_RC_HSG_v2_0_scientific_redesign_decision_record.md` | author-level RC-HSG redesign basis；由 v2.1 §20 形成 active、可执行裁决 |

### 0.2 历史一致结论（科学解释已由 §20 supersede）

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
| ZuCo 2.0 task 1 Natural Reading（NR） | **primary 数据已完成 data-card 准入；stimulus grouping 待冻结** | 官方论文报告 18 名有效参与者、349 句；自然阅读最贴合本文一般 EEG→text 问题。run 005–008 已核实许可、同源性、schema、5,905-row 可复现分析视图与 377-row exclusion union；run 008 已生成 data card。v1.8 只补 stimulus source binding 与 similarity diagnostic，不做 split，也不把 TSR 的显式关系搜索任务混入 primary |
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

0. **V0 仓库【CLOSED】**：公开 `main@b72ed5ab9720b7a922f7d1c6d8681cb646c344ab` 已完成治理 bootstrap、环境同步、治理加固、输入发现、三轮定向 NR 审计与 run 008 data-card 准入；关闭 V0 不代表任何科学模型或 Gate 已实现。
1. **G1 治理连续性【CLOSED】**：run 005 建立动态 active-SPEC fail-closed 回归检查，run 008 已把全部入口同步到 v1.7，并使 `S0_STIMULUS_ID` 成为唯一 recommendation。v1.8 必须按同一机制修复该任务的信息可执行性，不得改写旧 run。
2. **V1 数据【DATA CARD DONE；STIMULUS SOURCE DIAGNOSTIC READY】**：run 008 已冻结 5,905-row analysis view、377-row exclusion union 和 data card；strict full-release diagnostic 仍 FAIL，unit 仍为 `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`。当前 committed stimulus artifacts 只有 349 slot hashes、344 unique hashes、长度与 5 个 exact duplicate groups，没有 stimulus text、document ID 或 paragraph ID。它们足以验证 exact duplicates，却不足以计算 edit distance、semantic embedding 或 paraphrase。下一 run 只允许读取已经 run-005 27/27 SHA256 绑定的 7 个小型 NR material CSV，生成不含原文的 source binding 与 similarity diagnostic；不得把 block adjacency 猜成 document/paragraph，也不得在看到 diagnostic 前由 Codex 自选 near-duplicate threshold。
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

**T6-CODEX：在 `wip2@b72ed5ab9720b7a922f7d1c6d8681cb646c344ab` 上完成 stimulus source binding 与全对 similarity diagnostic；不冻结 near-duplicate grouping threshold，不做 split。**

本任务先激活 v1.8，并新增 `SPEC_V18_REVIEW → S0_STIMULUS_SOURCE_BINDING → S0_STIMULUS_SIMILARITY_DIAGNOSTIC → S0_STIMULUS_GROUP_POLICY_REVIEW(READY, owner=ChatGPT/author)`。它只读取 7 个已经 run-005 SHA256 绑定的 NR material CSV、schema-v3 material/hash ledger、5,905-row analysis view 和 data card；禁止读取 EEG、event latency、outcome 或历史结果。输出必须重新证明 370 rows、21 practice exclusions、349 task slots、344 unique normalized identities、5 exact duplicate groups和 58,996 个 unique-identity unordered pairs，并生成不含原文/embedding vector 的 edit/Jaccard/frozen-embedding diagnostic。Codex 不得凭经验选择 grouping threshold、声称 paraphrase verified、构造 split、选择 A、训练或运行 Gate。精确执行文本见交付 ZIP 根目录 `CODEX_NEXT_TASK.md`。

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

## 17. 第七次迭代状态与 stimulus-identity 诊断合同

### 17.1 对 `main@b72ed5a` 的独立复核

- 远程 `main` 为 `b72ed5ab9720b7a922f7d1c6d8681cb646c344ab`，commit message 为 `fix: admit bounded ZuCo NR analysis view`；相对 `bf958fe` 新增 run 008、analysis-view builder、5,905-row ledger、data card 与 NR5 future-summary regression。
- 独立环境复现 `test_build_zuco2_nr_analysis_view.py` 11/11、`test_project_memory.py` 38/38、`test_audit_input_sources.py` 8/8、validator、status 与 `git diff --check`。validator 为 `tasks=47, done=17`，stage 0 READY，唯一 recommendation 为 `S0_STIMULUS_ID`。
- 独立环境缺 `h5py`，所以 `test_audit_zuco2_nr.py` 在 import 时明确失败；没有把 run 008 的服务器 21/21 targeted tests 冒充为本地复现。
- 从四个 committed schema-v3 inputs 独立重建的 analysis view、summary、data card 和 report 与 commit 逐 byte 相同，SHA256 分别为 `0751259f...12ff`、`5e387ef3...6181`、`d9331bfe...0f84`、`b64b0e74...58b0`。接受 run 008 的 5,905/377/6,282、NR3/NR5/NR6、unknown-unit 与 no-outcome 边界。
- 没有读取真实 EEG、held-out/test outcome、历史 predictions/metrics 或 `trust_align` 结果树；没有训练、选择 A、构造 split 或运行 Gate。

### 17.2 当前 `S0_STIMULUS_ID` 的信息缺口

已提交的 `zuco2_nr_stimulus_manifest_v3.jsonl` 与 `zuco2_nr_analysis_view_v1.jsonl` 不含 stimulus text、document ID 或 paragraph ID。它们只含 salt-free SHA256、长度、slot/block/material line 与 assignment locator。schema-v3 material contract 已证明：

```text
post-practice slots                 349
unique normalized stimulus hashes  344
cross-block exact duplicate groups   5
```

因此 committed evidence 可以完成 exact-hash grouping，但无法计算字符串编辑距离、token overlap 或语义 embedding；SHA256 不保留任何可用于 near-duplicate 判断的距离。它也不能证明 document/paragraph identity。当前根 `CODEX_NEXT_TASK.md` 要求“只用 committed evidence”同时完成这些项目，属于可恢复的任务规格冲突，而不是让 Codex 自行补数据或猜阈值的授权。

v1.8 的修复顺序是：先对 7 个已经通过 run-005 local↔OSF SHA256 的小型 material CSV 做受限 source binding，再产出 outcome-blind similarity diagnostic；阈值和最终 union-find grouping 由下一轮 ChatGPT/作者根据 diagnostic 冻结。不能在同一 Codex run 内既看 corpus score 分布又自行选择 threshold 并宣布 DONE。

### 17.3 允许的 source scope 与固定 hash

只允许从 `/home/song/projects/trust_align/zuco/...` 的已记录 ZuCo 2.0 根读取以下 7 个 text CSV；实际根路径必须从 run 005/schema-v3 已记录的 authorized dataset root 恢复，不能全盘搜索：

| 文件 | SHA256 |
|---|---|
| `task_materials/nr_1.csv` | `77291d9fe66797781efa7c093824a16198f38e92ac34067e8bf20d76d5c50386` |
| `task_materials/nr_2.csv` | `68a6885dd96d4fa386297d7f30352c2077b565577c68dcb2205b19d506042132` |
| `task_materials/nr_3.csv` | `1a1ead3a1dfa12d8ff73dbe619db94b6ce202b35a3d19358d67f01c3115553ba` |
| `task_materials/nr_4.csv` | `d7b5c9b3a0e6d55958b976b0ea2cc6c236720ead947d6851d15de798e712965f` |
| `task_materials/nr_5.csv` | `2ca84d88f3267ecc4686f357cc97f2c077a2b90534ecbc8615b2197e2f93b5bc` |
| `task_materials/nr_6.csv` | `3722ba205f8b63e801791ef3303dcdbf52bbef3c6bd157bd11a16ccd40e1861a` |
| `task_materials/nr_7.csv` | `575a938092ca1db20d883fed180cb48fa66deca53097267874fe784fdc44cf9b` |

每个文件在解析前重新计算 SHA256；任一不符即 `STIMULUS_SOURCE_HASH_MISMATCH` 并停止。允许同时读取 committed `zuco2_nr_targeted_manifest_v3.yaml`、`zuco2_nr_analysis_view_v1.{jsonl,yaml}` 与 `data_card.yaml` 做绑定。禁止读取 MAT/HDF5、EEG、event、TSR、历史结果或其他材料文本。

### 17.4 文本规范化与 identity 层

冻结两个不同用途的规范化函数，禁止混用：

1. `N_exact(s)`：UTF-8 decode（CSV 使用 `utf-8-sig`）、Unicode NFKC、首尾空白删除、所有 Unicode whitespace run 折叠成单个 ASCII space；保留大小写与标点。`stimulus_sha256=SHA256(UTF8(N_exact(s)))`，必须逐 slot 与 schema-v3 349/349 匹配。
2. `N_lex(s)`：从 `N_exact` 继续做 Unicode `casefold()`，把每个连续的非字母数字字符 run 替换为单个 space，再折叠/trim。token 是由 space 分隔的非空项。`lexical_sha256=SHA256(UTF8(N_lex(s)))`；不得提交 `N_exact`、`N_lex` 或 token 内容。

identity 层级固定为：

- `occurrence_id`：现有 task/block/material-line/slot key，不合并重复呈现；
- `exact_stimulus_id`：现有 `stimulus_sha256`，349 slots 映射到 344 unique identities；
- `document_id` / `paragraph_id`：只有 CSV 中存在明确、非文本推断的 source field 才能绑定；否则写 `null` 与 `SOURCE_METADATA_NOT_AVAILABLE`。不得把 block、邻接 line、主题相似或 URL 猜测当作 document/paragraph；
- `near_duplicate_group_id`：本 run 不生成，保持 `PENDING_GROUP_POLICY_REVIEW`。

输出不得含原文、token、n-gram、embedding vector、可逆文本片段或第三方 article body。

### 17.5 冻结 embedding diagnostic

只把 embedding 用于 input-leakage grouping diagnostic，不是 backbone A、文本生成器、evaluator 或科学结果。模型固定为官方 `sentence-transformers/all-MiniLM-L6-v2@c9745ed1d9f207416be6d2e6f8de32d1f16199bf`；model card 标为 Apache-2.0，并说明其输出 384 维 sentence/short-paragraph vector、适用于 clustering/sentence similarity。只允许安全的 `model.safetensors` 加 config/tokenizer/`1_Pooling` 文件；禁止加载 `pytorch_model.bin`、pickle、ONNX、OpenVINO、TF 或 Rust weights。

若 exact revision 不在本地 cache，允许一次受限下载该 repo/revision 的上述必要文件；不得下载整个 977 MB multi-format repository，不使用 API inference，不发送 stimulus text 到远程服务，不下载其他模型。保存 model revision、license、每个实际读取文件的 SHA256、Transformers/Torch/tokenizers versions 与 download status；weights 不进 Git。

推理固定为 CPU、eval/no-grad、batch ordering 按 `exact_stimulus_id`、官方 attention-mask mean pooling、L2 normalize、float32。tokenizer 必须在不 truncation 的探测中证明所有 344 identities `wordpieces<=256`；任何超限即 `STIMULUS_EMBEDDING_TRUNCATION_REQUIRED` 并停止 diagnostic，不能静默截断。embedding vectors 只在内存存在，不落盘。

### 17.6 全对 similarity diagnostic

对 344 unique `exact_stimulus_id` 的全部无序 pair 计算并断言：

\[
\binom{344}{2}=58{,}996.
\]

每个 pair 计算：

1. `edit_similarity = 1 - levenshtein(N_lex(a),N_lex(b))/max(len(a),len(b))`；两个空串视为 schema error，不定义为相似；
2. `token_jaccard = |T_a∩T_b|/|T_a∪T_b|`；空 union 为 schema error；
3. `embedding_cosine`：上节 384-d L2 vectors 的 dot product。

浮点在完成比较后 round-half-even 到 6 decimals；排序 key 固定为 `(id_a,id_b)`，且 `id_a<id_b`。本 run 的 broad diagnostic prefilter 不是 grouping threshold：

```text
edit_similarity >= 0.80
OR token_jaccard >= 0.70
OR embedding_cosine >= 0.70
```

输出全体三项 score 的 0.01-width histograms、min/max/预注册 quantiles、每项 top-1000 pair、broad-prefilter union ledger、candidate count 与交集 counts。candidate ledger 只含两个 exact IDs、三个 scores、触发 flags、两个长度、source slots；不得含文本。exact duplicates 单独按既有 5 groups ledger，不混入 344-identity pair 数。

Codex 不得根据 histogram、top pairs 或 candidate count 自行选择最终 threshold，不得把 `embedding_cosine` 高称为 verified paraphrase，也不得在本 run 运行 union-find near-duplicate grouping。diagnostic 的职责是把下一次阈值决策需要的信息变成 committed、可复核、outcome-blind evidence。

### 17.7 任务图、输出与停止状态

新增：

```text
SPEC_V18_REVIEW
  -> S0_STIMULUS_SOURCE_BINDING
  -> S0_STIMULUS_SIMILARITY_DIAGNOSTIC
  -> S0_STIMULUS_GROUP_POLICY_REVIEW (READY; owner=ChatGPT/author)
  -> S0_STIMULUS_ID (BLOCKED until policy review)
  -> S0_JOINT_SPLIT (still BLOCKED)
```

本 run 最小产物：

```text
scripts/build_stimulus_similarity_diagnostic.py
tests/test_build_stimulus_similarity_diagnostic.py
artifacts/stimulus_source_binding_v1.yaml
artifacts/stimulus_similarity_diagnostic_v1.yaml
artifacts/stimulus_similarity_candidates_v1.jsonl
reports/stimulus_similarity_diagnostic_v1.md
runs/2026-08-22_009_stimulus_similarity_diagnostic.md
```

source binding 与 diagnostic 验收全部 PASS 时：`SPEC_V18_REVIEW=DONE`、`S0_STIMULUS_SOURCE_BINDING=DONE`、`S0_STIMULUS_SIMILARITY_DIAGNOSTIC=DONE`、`S0_STIMULUS_GROUP_POLICY_REVIEW=READY`；`S0_STIMULUS_ID` 从原 READY 改为 BLOCKED，原因是 threshold/policy 尚未冻结；`recommended_next_task=S0_STIMULUS_GROUP_POLICY_REVIEW`，execution 保持 stage 0 READY。根 `CODEX_NEXT_TASK.md` 必须改成“等待 ChatGPT/author policy review”，不能继续做 grouping 或 split。

若 material hash/row/slot/hash binding、model safe-load、token length、pair count、determinism、文本泄漏或任何测试失败，diagnostic 不得 DONE；保留精确 blocker 并停止。旧 runs 001–008、schema-v1/v2/v3、analysis view 与 data card 不得修改。

### 17.8 v1.8 未改变的科学决定

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、subject-cluster inference、无 teacher forcing、stimulus-disjoint split、Gate A1→A→B、calibration 二选一、5,905-row analysis view、377-row exclusion union、unknown-unit policy 和全部 failure routes 保持不变。v1.8 不读取 EEG/outcome，不选择 A，不构造 split，不实现 schema/null/NC-HSG，不训练，也不运行 Gate。

本节的外部算法依据限于官方模型资料：[`all-MiniLM-L6-v2` model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) 声明 sentence/short-paragraph embedding、clustering/similarity 用途、384 维输出、mean pooling/L2 normalization 示例与 256-wordpiece truncation 边界；[固定 revision tree](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/c9745ed1d9f207416be6d2e6f8de32d1f16199bf) 列出 Apache-2.0 metadata 与 90.9 MB safe `model.safetensors`。这些资料只支持 diagnostic 实现，不提供本数据集的最佳 grouping threshold，所以 threshold 必须留待 corpus diagnostic 后冻结。

## 18. 第八次迭代状态与最终 stimulus-grouping 合同

### 18.1 对 `main@1252d0a` 与 run 009 的独立复核

- 远程 `main` 为 `1252d0a24b6d4785e7f550464586c95f54f3cfa3`，commit message 为 `chore: diagnose ZuCo NR stimulus similarity`，worktree clean，远程与本地 HEAD 一致。
- 独立环境复现 `test_build_stimulus_similarity_diagnostic.py` 12/12、`test_build_zuco2_nr_analysis_view.py` 11/11、`test_project_memory.py` 38/38、`test_audit_input_sources.py` 8/8；validator 为 `tasks=51, done=20`，status 为 stage 0 READY，唯一推荐任务是 `S0_STIMULUS_GROUP_POLICY_REVIEW`，`git diff --check` 通过。
- 独立环境缺 `h5py`，所以 `test_audit_zuco2_nr.py` 在 import 时明确报 `ModuleNotFoundError`；没有把本地未运行的 targeted tests 冒充为复现。run 009 记录服务器 21/21 PASS。
- 四个 run-009 输出 SHA256 与记录逐一相同：source binding `d1feb8e4...b941`、diagnostic `878d9ea6...a66d`、candidate ledger `6645369f...e6b`、report `93a5d2ab...200b`。
- 独立解析确认：349 slots、344 exact identities、5 个 exact duplicate occurrence groups、58,996 pairs、11 broad candidates；下节冻结规则产生 2 条 inter-identity edge、342 个最终 groups、9 个未连接 broad candidates。
- 本轮只读取治理、代码和不含原文的 committed diagnostic artifacts；没有读取 stimulus 原文、EEG、event、TSR、held-out/test outcome、历史 prediction/metric 或其他项目结果，也没有选择 A、训练或运行 Gate。

### 18.2 冻结的最终分组政策

政策 ID 固定为：

```text
NC_HSG_STIMULUS_GROUP_POLICY_V1
```

输入只能是以下三个 committed artifacts，导入后先校验完整 SHA256；任一不符即 `STIMULUS_GROUP_INPUT_HASH_MISMATCH` 并停止：

| 输入 | SHA256 |
|---|---|
| `artifacts/stimulus_source_binding_v1.yaml` | `d1feb8e46b69074693173594ccdc4f7c3e014ca113594701131fe460f205b941` |
| `artifacts/stimulus_similarity_diagnostic_v1.yaml` | `878d9ea68c9f5c42cc2f8d441da3117681b354d9869e1238011f6f8d7522a66d` |
| `artifacts/stimulus_similarity_candidates_v1.jsonl` | `6645369f6cfc173683c825de71d12689faa6ff75a4544c68ab018875e6d7be6b` |

对两个不同 `exact_stimulus_id`，使用 candidate ledger 已提交的六位小数 score；不重新读取 CSV、不重新运行 tokenizer/model，也不从 top-pair 排名重算分数。最终无向边规则为：

```text
edit_similarity >= 0.95
OR token_jaccard >= 0.90
OR embedding_cosine >= 0.90
```

三条阈值都不低于 run-009 broad prefilter，因此 11-row candidate ledger 是最终边规则的完备超集。阈值取自 run 009 预先输出的高位 component-risk grid，不从 outcome、split 或模型性能选择。选择理由如下：

1. `edit>=0.95` 与 `Jaccard>=0.90` 保守捕获大小写/标点等 exact-hash 外的词面等价风险；固定 corpus 中两者都只触发同一对。
2. `cosine>=0.90` 处于极端尾部：p99 仅为 `0.414134`；它只触发 cosine=`0.998133` 与 `0.959401` 两对，而下一高 broad candidate 只有 `0.782380`，不存在临界堆积。
3. 高 embedding 分数只表示 **split leakage risk**，不表示人工确认的 paraphrase。由于本轮不读取原文，所有输出必须写 `paraphrase_verified=false` 与 `paraphrase_status=NOT_VERIFIED_NO_TEXT_REVIEW`。
4. 对 split 而言，少量 false-positive 合并只损失少量有效组数，false-negative 则可能让高度相似刺激跨集合；在只有两个 size-2 components 且无 chaining 风险的现状下，选择高阈值风险合并更保守。

先把同一 `exact_stimulus_id` 的多个 occurrences 映射到同一 split group，但 `occurrence_id`、subject-slot row 与 exact duplicate occurrences 必须继续保留，禁止物理合并或删行。再对 344 个 exact IDs 的最终边执行确定性 union-find。当前固定输入的唯一合法结果是：

| 项目 | 冻结值 |
|---|---:|
| final inter-identity edges | 2 |
| broad candidates below final rule | 9 |
| final stimulus groups | 342 |
| multi-exact-ID groups | 2 |
| largest exact-ID component | 2 |
| one-occurrence groups | 335 |
| two-occurrence groups | 7 |
| groups larger than two occurrences | 0 |

两条 edge 的 opaque 审计事实为：

| slots | edit | Jaccard | cosine | 决策标签 |
|---|---:|---:|---:|---|
| 97 / 327 | 1.000000 | 1.000000 | 0.998133 | `GROUP_LEXICAL_EQUIVALENCE_RISK` |
| 307 / 308 | 0.693431 | 0.692308 | 0.959401 | `GROUP_EMBEDDING_NEAR_DUPLICATE_LEAKAGE_RISK` |

其余 9 个 broad candidates 全部标 `UNJOINED_BELOW_FROZEN_POLICY`。不得把 block 邻接、slot 邻接、document/paragraph 猜测或 article 主题用于补边；`document_id` 与 `paragraph_id` 继续为 `null`，status 继续为 `SOURCE_METADATA_NOT_AVAILABLE`。

### 18.3 确定性 artifact 合同

新增：

```text
scripts/build_stimulus_identity.py
tests/test_build_stimulus_identity.py
artifacts/stimulus_identity.yaml
artifacts/stimulus_groups.json
reports/stimulus_identity.md
runs/2026-08-23_010_stimulus_identity_grouping.md
```

`build_stimulus_identity.py` 的生产 CLI 不接受输入路径或 threshold 参数；它只从 repository root 读取上述三个固定 committed paths。CLI 只允许可选的 `--output-root`，并始终在该 root 下写固定相对路径 `artifacts/stimulus_identity.yaml`、`artifacts/stimulus_groups.json`、`reports/stimulus_identity.md`；默认 output root 是 repository root。这样可以在 repo 外两个临时 root 做真实确定性复建，又不能替换科学输入。未知参数、input symlink/越界、output symlink/重叠、hash/schema/count/order/allowlist 不符均 fail closed。阈值常量必须带 policy ID，并由测试精确锁定。

每个 group ID 必须按下式生成，禁止用顺序号或 Python hash：

```text
payload = b"NC_HSG_STIMULUS_GROUP_V1\0"
          + b"\n".join(value.encode("ascii")
                         for value in sorted(member_exact_stimulus_ids))
stimulus_group_id = "sg_v1_" + SHA256(payload).hexdigest()
```

`artifacts/stimulus_identity.yaml` 至少包含：schema/artifact/policy ID、三个输入 hash、精确阈值与边规则、score source/rounding contract、normalization contract 引用、metadata availability、全部 344 个 exact identity 到 group 的映射、11 个 candidate decision、5 个 exact duplicate occurrence ledger、计数、safety boundary。每个 identity 继续记录已有 `lexical_sha256`、slots、blocks、material lines 与 analysis-view row count，但不得写原文或 token。

`artifacts/stimulus_groups.json` 是一个 JSON object，不是 JSONL；至少包含 schema/artifact/policy/input hashes/counts/groups。342 个 group records 按最小 member exact ID 排序；member exact IDs 按 ASCII 升序，slots 按整数升序，edge evidence 按 `(id_a,id_b)` 升序。每组记录 `stimulus_group_id`、member IDs、member slots、group kind、edge decisions、`paraphrase_verified=false`、document/paragraph null/status。group kind 只允许：

```text
SINGLETON
EXACT_DUPLICATE_OCCURRENCES
NEAR_DUPLICATE_LEAKAGE_RISK
```

固定结果中应为 335/5/2。两个 multi-ID groups 一律使用 `NEAR_DUPLICATE_LEAKAGE_RISK`；不能写 `PARAPHRASE`。所有 349 occurrences 都必须恰好映射一次，所有 5,905 analysis-view rows 的 exact ID 必须可映射，但输出不复制 5,905-row ledger。

输出使用原子写入；YAML key/list 顺序和 JSON formatting 必须固定，JSON 使用 UTF-8、`sort_keys=True`、2-space indent、尾部一个 newline。连续两次完整构建必须逐 byte 相同。至少覆盖以下测试：固定 input hashes、schema/count/order、candidate 完备性、阈值边界、2-edge/342-group/335-5-2 counts、union-find、stable group ID、exact occurrence 保留、11-row decision ledger、metadata null、paraphrase 未验证、禁止字段、tamper/缺行/额外行/路径逃逸/symlink fail-closed、两次构建 byte-identical。

### 18.4 任务图与成功后的停止状态

新增并执行：

```text
SPEC_V19_REVIEW
  -> S0_STIMULUS_GROUP_POLICY_REVIEW (由本 SPEC 冻结，DONE)
  -> S0_STIMULUS_ID (Codex 实现与验证，DONE)
  -> S0_JOINT_SPLIT (READY；本 run 停止)
```

成功后：

- active SPEC 为 `guide/NC_HSG_Paper_Spec_v1_9_2026-08-23.md`，version `v1.9`，reviewed/baseline commit 为 `1252d0a24b6d4785e7f550464586c95f54f3cfa3`；
- `SPEC_V19_REVIEW`、`S0_STIMULUS_GROUP_POLICY_REVIEW`、`S0_STIMULUS_ID` 为 DONE，证据指向 v1.9 review、两个 artifacts、测试与 run 010；
- `last_completed_task=S0_STIMULUS_ID`，`recommended_next_task=S0_JOINT_SPLIT`，execution 保持 stage 0 READY；
- `S0_JOINT_SPLIT` 从 BLOCKED 改为 READY，why-ready 明确 342 个 groups 已冻结；但根 `CODEX_NEXT_TASK.md` 必须写等待下一轮 ChatGPT/作者给出精确 split 实现指令，不能在 run 010 继续执行；
- `S0_A_INTERFACE`、N1/N2、schema、训练与 Gates 的 blocker 不变，unknown-unit blocker 仍只阻断 unit-sensitive A。

若三个输入 hash、11-candidate 完备性、2-edge、342 groups、335/5/2 kinds、349 occurrence coverage、metadata null、no-text safety、determinism 或任一测试失败：`S0_STIMULUS_ID` 不得 DONE，`S0_JOINT_SPLIT` 不得 READY；记录精确 blocker 后停止，不得修改阈值或 expected counts 迎合实现。

### 18.5 Codex 执行与验证边界

下一 run 从 clean `main@1252d0a24b6d4785e7f550464586c95f54f3cfa3` 开始，只导入 package manifest 列出的 v1.9 SPEC、review 与根任务指令。保留旧 SPEC、reviews、runs 001–009、schema-v1/v2/v3、analysis view、data card 与 run-009 artifacts 不变。允许修改本节列出的新增文件以及 active entry/state files：`AGENTS.md`、`AI_START_HERE.md`、`PROJECT_STATE.yaml`、`TASKS.yaml`、`HANDOFF.md`、`CODEX_NEXT_TASK.md`、validator allowlist 与对应治理测试。

最低验证集：

```text
python -m unittest discover -s tests -p 'test_build_stimulus_identity.py'
python -m unittest discover -s tests -p 'test_build_stimulus_similarity_diagnostic.py'
python -m unittest discover -s tests -p 'test_build_zuco2_nr_analysis_view.py'
python -m unittest discover -s tests -p 'test_audit_zuco2_nr.py'
python -m unittest discover -s tests -p 'test_project_memory.py'
python -m unittest discover -s tests -p 'test_audit_input_sources.py'
python scripts/check_project_state.py
python scripts/project_status.py
git diff --check
```

用服务器冻结 Python 路径运行；如果环境依赖缺失，先报告而不是跳过并冒充 PASS。随后执行两次真实 repository-only build 到 repo 外不同临时目录，比较三个输出 SHA256；通过后再原子写入正式 artifacts/report。最后写 run 010、同步治理文件、重跑验证、检查 no-text/no-split 边界，commit、push，并证明 `origin/main` 等于新 HEAD 且 worktree clean。

本 run 禁止：重新读取 7 个 material CSV 或任何 MAT/HDF5/EEG/event/TSR；重新下载或运行 embedding model；改变 threshold；人工或自动猜 paraphrase；构造 split；选择 A；实现 N1/N2/schema/NC-HSG；读取 outcome；训练或运行 Gate。

### 18.6 v1.9 未改变的科学决定

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、subject-cluster inference、无 teacher forcing、stimulus-group-disjoint split、Gate A1→A→B、calibration 二选一、5,905-row analysis view、377-row exclusion union、unknown-unit policy 和全部 failure routes 保持不变。v1.9 只冻结 outcome-blind split-group identity，不把相似度 diagnostic 或 grouping 当作 EEG 结果、semantic evidence、模型 admission 或 Gate 证据。

## 19. 第九次迭代：确定性 joint split 与 subject-macro population 合同

### 19.1 对 `main@e852e7d` 与 run 010 的独立复核

- 远程 `main`、fresh clone HEAD 与 `origin/main` 均为 `e852e7de24c31410387ad46d75fb44a5cac9e850`，commit message 为 `fix: freeze ZuCo NR stimulus groups`，worktree clean。
- active entry points、v1.9 SPEC、state、tasks、handoff、run 010 与物理 artifacts 一致；validator 为 `tasks=52, done=23`，stage 0 READY，唯一 READY/recommended task 为 `S0_JOINT_SPLIT`，无 `STATE_SPEC_CONFLICT`。
- 独立复现 `test_build_stimulus_identity.py` 12/12、`test_build_stimulus_similarity_diagnostic.py` 12/12、`test_build_zuco2_nr_analysis_view.py` 11/11、`test_project_memory.py` 38/38、`test_audit_input_sources.py` 8/8；`git diff --check` 通过。
- 当前复核环境仍缺 `h5py`，所以 `test_audit_zuco2_nr.py` 在 import 时明确失败；没有把本地未运行冒充 PASS。run 010 的服务器环境记录该测试 21/21 PASS，且没有 skip。
- 两次新的 repo-external `build_stimulus_identity.py` 生产构建逐 byte 相同，并复现 identity `f6b94449...a69ea`、groups `4408e57d...fded`、report `de83ea58...a465`；独立结构审计确认 349 occurrences、344 exact IDs、342 groups、335/5/2 kinds、最大 group size 2。
- 本轮研究只读取 committed identity/grouping、5,905-row analysis-view assignment metadata 与治理文件；没有读取 stimulus text、EEG 数值、event、outcome、prediction、metric 或历史结果。

### 19.2 固定输入与 read boundary

政策 ID：

```text
NC_HSG_JOINT_SPLIT_POLICY_V1
```

生产 builder 只允许读取下列固定 committed paths，并在 parse 前校验完整 SHA256；任一不符即 `JOINT_SPLIT_INPUT_HASH_MISMATCH`：

| 输入 | SHA256 |
|---|---|
| `artifacts/stimulus_identity.yaml` | `f6b94449d58c0e26d7da972968943f0eca0fa2bfc16cf2495ce8c41da80a69ea` |
| `artifacts/stimulus_groups.json` | `4408e57defbdc7ac5bd503c35489d68941d231d56009550a2bb17d0973b1fded` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.yaml` | `5e387ef3dc9e930e3ca3e4b6ccb6a009a3cc719281f1ac183cfbf56ac7b66181` |
| `artifacts/data_card.yaml` | `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84` |

analysis-view JSONL 只允许把 `occurrence_id, subject, session, task, block, slot, stimulus_sha256` 用作 split validation/feature；`raw_samples`、`raw_shape`、`raw_channels` 与 `source_locator` 不进入排序、目标函数或输出。所有 5,905 rows 必须唯一映射到 349 occurrences 与 342 groups。冻结 subject 顺序为：

```text
YAC,YAG,YAK,YDG,YDR,YFR,YFS,YHS,YIS,YLS,YMD,YMS,YRH,YRK,YRP,YSD,YSL,YTL
```

数据只有一个 admitted session，故 Regime II 固定为 18-fold LOSO；不得虚构跨日 fold。document/paragraph metadata 仍不可用，但其泄漏边界已由冻结 stimulus groups 保守覆盖。

### 19.3 Regime I 角色、容量与用途

342 个不可拆分 groups 的顶层 `60/20/20` 采用固定整数容量：

```text
outer_train = 205 groups  (59.9415%)
cal         =  68 groups  (19.8830%)
test        =  69 groups  (20.1754%)
```

由于 342 不可被 5 整除，`205/68/69` 是冻结的最大余数实现；cal/test 的相同余数固定把额外一组给 confirmatory test，不允许 Codex搜索容量。`outer_train` 再固定为：

```text
train_fit = 164 groups
inner_val =  41 groups
```

cal 的 68 groups 预先、outcome-blind 地保留为 `cal_select_reserve=34` 与 `cal_cert_reserve=34`。reserve 标签不提前决定 V5：若未来选择两段式，只能 select 用前者、cert 用后者；若选择 simultaneous LTT，可使用完整 cal union。不得根据未来结果交换 reserve。

用途冻结：

- `train_fit`：表示/adapter/schema/candidate/null-bin 的实际拟合；
- `inner_val`：只做 train-side 超参数、early stopping 与接口诊断；
- 配置冻结后，可预注册地在 `outer_train=train_fit∪inner_val` 重拟合一次，但必须对所有比较方法相同且不能读取 cal/test；
- `cal`：只做冻结 evaluator/policy 的 calibration；不得表示学习；
- `test`：`LOCKED_UNTIL_ROUTE_LOCK`，本 run 只生成身份索引，禁止读取任何 prediction/metric/outcome；
- random-trial split 不生成，也不能替代主 split。

### 19.4 整数、确定性的平衡算法

算法不搜索 seed。每个 group 的 feature vector 固定为 26 个非 outcome 整数：按上节 subject 顺序的 18 个 admitted-row counts、block 1–7 的 7 个 occurrence counts、总 occurrence count 1 个。禁止把文本、相似度 score、EEG 长度/幅值或模型信息作为 feature。

主分配固定：

```text
role order     = train_fit, inner_val, cal, test
capacities     = 164, 41, 68, 69
N              = 342
ordering domain= b"NC_HSG_JOINT_SPLIT_V1\0PRIMARY\0"
```

初始顺序 key 为 `(SHA256(domain + ASCII(stimulus_group_id)).digest(), stimulus_group_id)`；按 role order 连续填容量。对任意 feature (d)、role (r)，令总数 (T_d)、role observed (O_{rd})、容量 (c_r)，整数偏差为：

\[
D_{rd}=|N O_{rd}-c_r T_d|.
\]

目标 tuple 按字典序最小化：

```text
(
  max(subject D), sum(subject D^2),
  max(block D),   sum(block D^2),
  max(occurrence D), sum(occurrence D^2)
)
```

local search 的每轮按 ASCII group ID 枚举所有 `a<b` 且 role 不同的 pair，评估交换；只接受严格小于当前 tuple 的全局最小 candidate。若多对得到同一最小 tuple，因枚举顺序选择第一对。执行后重新开始；没有严格改进时停止。禁止随机 restart、浮点 objective、时间停止、solver-dependent tie 或手工换组。

主分配必须恰好 25 次 swap，最终 objective：

```text
(201, 804726, 344, 651510, 201, 76266)
```

按 group ID 排序、每行 `group_id<TAB>role<LF>` 的 canonical ledger SHA256 必须为：

```text
531539ff3592cc28d89c5e3ef568d019eaab733ccdb1053c1fcf1c471e9dac1c
```

cal reserve 在最终 68 cal groups 上重复同一算法：

```text
role order      = cal_select_reserve, cal_cert_reserve
capacities      = 34, 34
N               = 68
ordering domain = b"NC_HSG_JOINT_SPLIT_V1\0CAL_RESERVE\0"
```

必须 6 次 swap，objective=`(34,30056,34,2312,34,2312)`；canonical reserve ledger SHA256：

```text
5f464d97e695ab6bc58d10ac2342351195fa936144487bd9e78f96e5e7a8442c
```

固定 summary：

| role | groups | occurrences | analysis rows | block-1..7 occurrences | per-subject row range |
|---|---:|---:|---:|---|---:|
| train_fit | 164 | 167 | 2,832 | 24,23,25,24,24,24,23 | 117–167 |
| inner_val | 41 | 42 | 709 | 7,6,6,6,6,5,6 | 29–42 |
| cal | 68 | 69 | 1,171 | 9,10,10,10,10,10,10 | 48–69 |
| test | 69 | 71 | 1,193 | 10,11,10,10,10,10,10 | 49–71 |
| cal_select_reserve | 34 | 35 | 591 | 5,5,5,5,5,5,5 | 24–35 |
| cal_cert_reserve | 34 | 34 | 580 | 4,5,5,5,5,5,5 | 24–34 |

任一 iteration count、objective、ledger hash 或 summary 不符均 fail closed；不得改期望值迎合代码。

### 19.5 Regime I artifact 合同

`artifacts/split_regimeI.json` 必须包含 policy/input hashes、角色/容量、342 个 group assignments 与 5,905 个 row assignments。group records 按 group ID；row records 按 `(subject,slot,occurrence_id)` 排序。row allowlist：

```text
occurrence_id, subject, session, task, block, slot,
exact_stimulus_id, stimulus_group_id, role, calibration_reserve
```

非 cal row 的 `calibration_reserve=null`。必须断言：

- 342 groups 与 344 exact IDs 各出现一次；349 occurrences、5,905 analysis rows 各映射一次；
- `train_fit/inner_val/cal/test` group sets pairwise disjoint，outer train 为前两者 union；
- 同一 stimulus group 的全部 exact IDs、slots、subjects 永不跨 role；
- 所有 18 subjects 在四个 roles 都有至少一行；
- exact/near-duplicate policy 未改变，document/paragraph 不被猜测；
- 输出不含 raw shape/sample/channel/source locator、文本、score、vector、prediction 或 metric。

### 19.6 Regime II：18-fold LOSO × frozen-test-stimulus

Regime II 复用 Regime I 的 group roles，不重新抽 stimulus。对每个按冻结顺序的 held-out subject 生成一个 fold：

```text
train_fit : subject != held_out AND group_role == train_fit
inner_val : subject != held_out AND group_role == inner_val
cal       : subject != held_out AND group_role == cal
test      : subject == held_out AND group_role == test
excluded_heldout_non_test : subject == held_out AND group_role != test
excluded_nonheldout_test  : subject != held_out AND group_role == test
```

每 fold 的 5,905 input rows 必须恰好进入上述六种互斥状态之一。训练、inner-val、cal 不得出现 held-out subject，也不得出现 test group；test 只含 held-out subject 与冻结 test groups。18 个 subjects 各 held out 一次。每 fold 记录每种状态 count，以及按 `(subject,slot,occurrence_id)` 生成的 canonical membership-ledger SHA256；不在 JSON 中重复 18×5,905 全量行。

`artifacts/split_regimeII.json` 至少包含 shared group-role ledger hash、18 folds、17-member train-subject list、partition predicates、counts/hashes、cal reserve counts，以及 test occurrence IDs。固定 fold ranges：train-fit 2,665–2,715 rows、inner-val 667–680、cal 1,102–1,123、test 49–71；每 fold test 必须非空。

Regime II 只用于跨被试且跨测试刺激的外部效度/经验风险与相对排序。它不声称 calibration risk guarantee，不允许把 other-subject test-group rows 混入 fold test，也不允许用 held-out subject 的非-test rows做 adaptation。

### 19.7 Gate A population 与 cluster-inference freeze

新增政策 ID：

```text
NC_HSG_GATE_A_POPULATION_V1
```

`artifacts/gate_a_population.yaml` 必须冻结：

1. Regime I confirmatory population 是上述固定 18 subjects，subject 为唯一主要统计 cluster，等权 subject macro；test rows/subject 依次为：

```text
YAC50,YAG71,YAK60,YDG71,YDR70,YFR49,YFS68,YHS71,YIS71,
YLS69,YMD69,YMS70,YRH60,YRK68,YRP69,YSD70,YSL69,YTL68
```

2. Regime II population 是 18 个 LOSO fold 的 held-out-subject summaries，仍等权但只作描述性外部效度。
3. 每个方法/seed 先在每名 subject 的固定共同 test-row set 上计算 trial-derived metric，再在 subject 内聚合 trials；随后在 subject 内平均 5 seeds；最后才对 18 subjects 等权平均。seed、trial 或 occurrence 绝不能冒充独立 cluster。
4. 方法比较必须在相同 row/subject/seed 索引上 paired；不 zero-fill、不把缺失 subject 静默删除。任一冻结 subject 完全缺少可比较输出时，confirmatory Gate 标 `NOT_EVALUABLE`，而不是改变 population。
5. 10,000 次 paired subject bootstrap 使用固定 subject 顺序。每个 replicate 抽 18 个 subject indices with replacement；生成器为 SHA256 counter rejection sampling：

```text
domain = b"NC_HSG_GATE_A_POPULATION_V1\0SUBJECT_BOOTSTRAP\0"
digest = SHA256(domain + uint32_be(replicate)
                       + uint16_be(draw)
                       + uint16_be(retry))
x = uint64_be(digest[0:8])
accept only x < floor(2^64/18)*18; index = x mod 18
```

10,000×18 indices 按 replicate/draw 顺序直接写为 180,000 个 uint8 bytes，其 SHA256 必须为：

```text
e77ca92b29c414a17c1e66edf4075edd470c007dfe2019487c36758f5f99c86d
```

CI 使用 paired subject-bootstrap distribution 的 equal-tailed 2.5%/97.5% quantiles；具体 metric/Gate 仍由后续 frozen artifacts 提供，本 run 不计算任何科学统计量。

### 19.8 实现、任务图与停止状态

新增最小实现：

```text
scripts/build_joint_split.py
tests/test_build_joint_split.py
artifacts/split_regimeI.json
artifacts/split_regimeII.json
artifacts/split_manifest.yaml
artifacts/gate_a_population.yaml
reports/joint_split_population.md
runs/2026-08-23_011_joint_split_population_freeze.md
```

生产 CLI 不接受 input path、capacity、domain、seed、objective 或 threshold 参数；只允许可选 `--output-root`，固定写上述 artifacts/report。函数级测试可注入 fixture root。路径、symlink、hash、schema、allowlist、count、order、objective、iteration、canonical ledger、coverage、no-leakage 或 determinism 任一失败都必须原子 fail closed。

任务链：

```text
SPEC_V20_REVIEW
  -> S0_JOINT_SPLIT
  -> S0_GATE_A_POPULATION_E5
  -> S0_A_POLICY_REVIEW (READY; owner=ChatGPT/author; stop)
```

成功后：active SPEC=v2.0；baseline/reviewed commit=`e852e7de24c31410387ad46d75fb44a5cac9e850`；`SPEC_V20_REVIEW`、`S0_JOINT_SPLIT`、`S0_GATE_A_POPULATION_E5` DONE；`last_completed_task=S0_GATE_A_POPULATION_E5`，`recommended_next_task=S0_A_POLICY_REVIEW`，stage 0 READY。新增 `S0_A_POLICY_REVIEW`，要求 ChatGPT/作者只基于 license、release-native amplitude compatibility、channel/interface、checkpoint locality、复现性和改造成本选择/拒绝唯一 A；Codex 不得选择。`S0_A_INTERFACE` 与 `S0_LEAKAGE_AUDIT` 继续 BLOCKED。

最低测试覆盖：固定 inputs/field allowlist；group/row/fold counts；容量；初始 hash order；整数 objective；25/6 swaps；两个 canonical ledger hashes；Regime I 全覆盖/无 overlap；Regime II 18-fold predicates/全覆盖/无 subject 或 group leakage；population/aggregation/bootstrap hash；test lock；tamper/missing/extra/unknown arg/path escape/symlink fail closed；atomic writes；两个 repo-external production builds逐 byte相同。

服务器验证集至少运行：新 split tests、identity tests、similarity tests、analysis-view tests、targeted audit、project-memory tests、input-audit tests、validator、status、`git diff --check`。写 run 011，更新所有 active entry/state/task files 与 validator allowlist/tests，确认不出现 random split、prediction/metric/model/data cache，再 commit/push；证明 `origin/main==HEAD` 且 clean。

本 run 禁止：读取 stimulus text、真实 EEG/event/TSR 或任何 outcome；改变 grouping/split capacity/objective/domain；搜索更好 seed/split；解锁 test；运行完整 leakage audit；选择/下载/实现 A；实现 N1/N2/schema/NC-HSG；训练或运行 Gate。

### 19.9 v2.0 未改变的科学决定

`alpha_0=0.10`、`K=199`、Specificity@Risk、N1/N2、selection-aware pseudo-real 统计量、无 teacher forcing、stimulus-group-disjoint split、Gate A1→A→B、calibration 二选一、5,905-row analysis view、377-row exclusion union、unknown-unit policy、`NC_HSG_STIMULUS_GROUP_POLICY_V1` 与全部 failure routes 保持不变。v2.0 只冻结身份索引、开发/校准/测试边界和统计人口，不产生模型证据、risk guarantee 或 Gate 结论。

---

## 20. 第十次迭代：RC-HSG 科学重构、A-policy 与新任务图

### 20.1 冻结依据、仓库事实与版本裁决

本节采用作者提供的 `NC-HSG → RC-HSG 科学重构决策记录`，其 SHA256 为
`b3792597de611f8aaee10ca8e363704d831a8f5ab8b47c6cd3f68c35d412c1f8`。
该记录是 author-level amendment basis，不是结果。采用时的远端事实基线为
`main@3b97fdc966b9b56d72287df619a80f6145d71189`，worktree clean，run 011 已完成：

- Regime I 固定为 164/41/68/69 个 `train_fit/inner_val/cal/test` groups；
- calibration reserve 固定为 34/34 个 `cal_select/cal_cert` groups；
- Regime I 覆盖 342 groups、344 exact IDs、349 occurrences、5,905 rows；
- Regime II 为 18 个 LOSO folds，不允许 held-out-subject adaptation；
- test identities 仍为 `LOCKED_UNTIL_ROUTE_LOCK`，未读取 test value；
- 旧名 `artifacts/gate_a_population.yaml` 是不可变的 run-011 population
  contract，名称保留作 provenance；其中 equal-weight subject macro 与 bootstrap
  合同由 Gate R、Gate H 和 Mechanism A 共同复用，不表示旧 Gate A 仍是核心门。

独立复核重新通过 joint split 13/13、identity 12/12、similarity 12/12、analysis
view 11/11、project memory 39/39、input audit 8/8，共 95 tests；validator 报告
54 tasks / 26 DONE / sole READY `S0_A_POLICY_REVIEW`。run 011 记录的服务器 targeted
audit 21/21 PASS 继续作为服务器证据。本版本没有读取 EEG value、semantic outcome、
calibration result、prediction 或 held-out/test metric，因此允许在此时进行科学重构。

由于 v2.0 已作为 run-011 active SPEC 和 split provenance 提交，不能再静默改写为另一
份 v2.0。本次作者级重构使用单调新版本 **v2.1**。v2.0 不删除、不重写；§§14–19
的数据与 split 证据继续有效，§20 supersede 旧科学解释和 downstream task graph。

### 20.2 新论文身份与唯一科学问题

正式方法名冻结为 **RC-HSG — Reference-Calibrated Hierarchical Semantic
Generation**。

推荐英文标题：

> *Reference-Calibrated Hierarchical Semantic Generation for
> Reliability-Aligned EEG-to-Text Generalization*

推荐中文标题：

> **面向可信泛化对齐的参照校准层级 EEG-to-Text 生成**

唯一核心 scientific question：

> 在 stimulus-group-disjoint EEG-to-Text 泛化中，结构匹配 reference
> distribution 提供的样本级相对信息，能否比 absolute confidence 更好地识别
> 何时可以安全输出更深语义，并使层级生成在相同 unsupported-semantic risk 下
> 达到更高 specificity？

核心因果链改为：

```text
weak single-trial EEG + strong language prior
→ fluent decoder may over-commit semantic detail on unseen stimuli
→ absolute score alone can misestimate sample-level semantic reliability
→ a structure-matched reference distribution contextualizes each frozen candidate score
→ low-capacity reliability estimators predict cumulative typed semantic error
→ a calibrated hierarchical policy stops at the deepest permitted semantic level
→ specificity is aligned with reliability under stimulus-disjoint generalization
```

旧 `W_l` 的 real-minus-null population location shift 不再被解释为主方法成立所必需的
EEG evidence increment。real-vs-reference separation 保留为 non-blocking Mechanism A。

### 20.3 核心 hypotheses 与不可升级的边界

**H1 — Reference Utility.** 在共享 A、F、candidate content、schema、split、
训练预算、calibration budget 与 evaluator 时，RC-HSG 相对 Absolute-HSG 在风险
预算内提高 `Specificity@Risk(0.10)`。

**H2 — Hierarchy Utility.** 在共享完整 reference feature、训练预算与风险预算时，
parent-consistent hierarchical fallback 相对 Flat-RC 提高 specificity，且
`M_sem` 不发生超过 0.05 的恶化。

**H3 — Generalization Reliability.** H1/H2 必须首先在 Regime I 成立。Regime II
只报告 subject × stimulus external validity 和 empirical risk，不给任意新被试、设备、
跨日或 distribution-free guarantee。

结果前禁止声称 thought reading、逐样本绝对可靠、生成细节全部可归因于 EEG、exact
knockoff、FDR control、任意新设备/被试保证，或 risk guarantee。只有 Gate C 的实际
finite-sample contract 成立且 test empirical risk 不越界时才允许 `risk-controlled`；
否则统一使用 `risk-aware` / `reliability-aligned`。

### 20.4 Reference score 与 primary feature contract

所有主方法共享每层冻结 candidate `y_l` 和 real score：

\[
s_l=s_l(E,y_l).
\]

对同一 candidate 生成 `K=199` 个 matched-reference scores
`S_l^ref={s_l(E^(k),y_l)}_{k=1}^{199}`。primary reference family priority 冻结为：

1. **N2 multivariate common-phase Fourier reference**：只要 Gate R0-N2 在所有 legal
   pre-test roles 全部 PASS，且其每个 row 都可生成 199 个 finite references，即为
   primary；test 解锁后只能运行同一冻结实现，任一 test row 失败使对应 confirmatory
   result `NOT_EVALUABLE`，不得切换 family；
2. **N1 within-block joint permutation**：作为 strict-randomization mechanism 与
   robustness family；只有 N2 不准入、N1 structural PASS、并且每个 subject 在全部
   legal pre-test roles 的 evaluable-row coverage 均不低于 0.90 时，才按本预注册
   fallback 成为 primary；test coverage 不得用于选择 family；
3. 不得按 AUROC、Specificity@Risk、Gate 或 test 表现挑 reference family；
4. 两者都不准入时，删除 RC claim，转 ordinary hierarchical selective generation。

N2 优先的理由是其 reference 对每个 trial 都由该 trial 自身的 multivariate spectrum
构造，更符合 sample-adaptive reliability context；N1 的严格随机化解释与 coverage
边界仍被保留，但不再让其 singleton/coverage 决定整篇方法生死。

对 primary family 定义：

\[
m_l=\operatorname{median}(S_l^{ref}),\qquad
\Delta_l=s_l-m_l,
\]

\[
V_l=\operatorname{median}_k|S_{lk}^{ref}-m_l|,\qquad
Z_l=\frac{\Delta_l}{\max(V_l,10^{-6})},
\]

\[
Q_l=\frac{1+\sum_{k=1}^{199}\mathbf 1[S_{lk}^{ref}\ge s_l]}{200}.
\]

primary spread **只允许 MAD**；IQR、standard deviation 和其他 spread 只可作三 seed
ablation，不得替换 primary。primary local feature vector 冻结为：

\[
\phi_l=[s_l,\Delta_l,Z_l,Q_l,V_l,c_l].
\]

`c_l` 只能包含不读取 gold 的冻结结构量：level ID、candidate 是否存在、从当前候选到
已选择父 candidate 的 deterministic projection-valid flag、ancestor-path-valid flag，
以及上一层 absolute score（L1 用固定 sentinel）。不得加入 stimulus text identity、
gold、test retrieval、subject ID、session ID、raw length、raw amplitude、未来 layer outcome
或任意 result-derived feature。连续 features 只用 train-fit 均值/尺度标准化并冻结；
calibration/test 不重新拟合。

`Q_l` 是 empirical reference-rank feature，不自动称 p-value。只有 N1 满足其完整
exchangeability/structural contract 时，单独的 N1 mechanism analysis 才可使用
randomization-p 语言。

### 20.5 Reliability model、candidate firewall 与 controller

每层累计预测 typed units 定义 unsupported count `u_i^(l)` 和总预测 count
`n_i^(l)=max(|Uhat_i^{<=l}|,1)`。primary reliability model 冻结为每层一个低容量
L2-regularized binomial-logistic GLM：

\[
u_i^{(l)}\sim\operatorname{Binomial}(n_i^{(l)},\hat r_l(\phi_{il})),
\qquad \hat r_l=\sigma(\beta_{0l}+\beta_l^T\phi_{il}).
\]

- intercept 不惩罚；不使用 deep MLP、free LLM judge、calibration representation
  learning 或 test-time fitting；
- `lambda ∈ {0.01,0.1,1,10,100}`，只在 inner-val 以 equal-weight subject-macro
  binomial deviance 选择；完全相同时选择更大 lambda；
- 固定 deterministic solver、最大 1,000 iterations、收敛 tolerance `1e-8`；不收敛
  即 fail closed，不临时换 solver/model；
- model family、feature order、standardizer、lambda grid、solver/version/hash 必须在
  cal/test 前冻结；每个 A/F seed 独立拟合一个 deterministic GLM，但 seed 不是统计样本。

candidate content selection 与 reliability routing 强制解耦：所有 B2/B3/B4/PMI/
uncertainty 主比较共享同一 candidate library、同一 frozen semantic decoder、同一
parent-consistent candidate path，并且**只按 absolute score `s_l` 选择内容**。reference
features 只决定是否允许输出到该层，不得改变 candidate ranking。reference-assisted
candidate ranking 只能作为非 primary ablation。

RC-HSG 的层级决策必须顺序满足父层：只有所有 `j<=l` 的 candidate path 合法且对应
frozen policy 通过，才允许 depth l；否则回退到最近通过层，无层通过则 L0 abstain。
L4 仍只语言化已认证 L3 slots，不新增 semantic unit，不增加 depth。

### 20.6 Gate 架构

**Gate R0 — Reference Integrity / Admissibility.** outcome-blind 审计 N1 的 block、
双射、scope、singleton/fixed-point、determinism、共同 preprocessing，以及 N2 的
real/reference 无文本判别、subject/session/length/power probes、PSD、cross-spectrum、
covariance、amplitude、endpoint、mask 和 coverage。一个 family 失败只删除该 family；
全部失败才删除 reference-calibrated 方法。R0 不读取 semantic outcome。

**Gate R — Reference Utility.** 比较 RC-HSG 与 Absolute-HSG。二者共享 candidate
content，Absolute-HSG 只使用 `[s_l,c_l]`，RC-HSG 使用完整 `phi_l`。confirmatory PASS
同时要求：`Delta D>=0.10`、paired subject-bootstrap 95% CI lower bound `>0`、
Holm-adjusted one-sided `p<0.05`、双方 test `R_sem<=0.10`，且 paired bootstrap 的
`Delta M_sem` 95% upper bound `<=0.05`。任何方法风险越界时该 primary cell invalid，
不能靠更深/更浅阈值事后修复。

**Gate C — Risk Certification.** 两阶段 `cal-select -> cal-cert` 路线在本版本冻结；
34-group select reserve 只做有限 policy/hyperparameter selection，34-group cert reserve
只认证完全冻结的有限 policy family。不能在 cal-cert 再改 feature/model/policy。只有
multiplicity-valid UCB `<=0.10` 且 test empirical risk `<=0.10` 才可写
`risk-controlled`；否则 Gate C FAIL 只删除保证措辞，不杀死 Gate R/H 的 empirical
reliability claim。

**Gate H — Hierarchy Utility.** 比较 RC-HSG 与 Flat-RC；Flat-RC 使用同一完整
reference features、candidate、模型预算和 calibration budget，但只有一个 global
accept/reject 或固定-depth decision，不使用 parent-pass 或逐层 fallback。PASS 要求
`Delta D>0`、paired 95% CI lower `>0`、Holm-adjusted one-sided `p<0.05`、双方风险
不越界，且 `Delta M_sem` 95% upper `<=0.05`。失败只删除 `Hierarchical` 标题词，
保留 flat reference-calibrated selective generation。

**Mechanism A — Real-vs-Reference Semantic Separation.** 完整报告旧 Gate A 的
L1–L3 margin/location、subject CI、Cliff delta、方向比例、depth gap 与层级趋势，但
它是 non-blocking diagnostic。失败只删除 EEG-attribution/evidence-increment 语言；
不得自动否定 Gate R、C 或 H。

### 20.7 Confirmatory family、统计与 anti-abstention

唯一 primary 仍为 subject-macro `Specificity@Risk(0.10)`；`alpha_0=0.10`、
敏感性 0.05/0.20/0.30、K=199、主表 5 seeds、ablation 3 seeds、10,000 paired
subject-bootstrap 全部继承。trial 先在 subject 内聚合，五 seeds 再在 subject 内平均，
最后 18 subjects 等权；任何 frozen subject 完全缺失时 confirmatory result
`NOT_EVALUABLE`，禁止 zero-fill 或静默删 subject。

confirmatory Holm family 固定为三项 one-sided paired comparisons：

1. RC-HSG > Absolute-HSG（Gate R）；
2. RC-HSG > Flat-RC（Gate H）；
3. RC-HSG > PMI/LM-prior-corrected hierarchical controller（matched EEG reference
   necessity claim）。

每项使用同一冻结 10,000×18 subject-bootstrap index stream。CI 为 equal-tailed
2.5/97.5%。one-sided bootstrap p-value 用 subject effects 在零均值下 centered 后，
以同一 indices 重采样；`p=(1+#null_bootstrap_mean>=observed_mean)/10001`，再做 Holm。
Gate R 额外保留冻结 MDE `Delta D>=0.10`；Gate H/PMI comparison 不加结果驱动 MDE。

anti-abstention cap 固定为 `Delta M_sem<=0.05`，并以 paired 95% CI upper bound 判定，
不是只看 point estimate。永远拒答的 `D=0, M_sem=1`；不得靠近乎普遍 abstention
制造风险 PASS。

AUROC/AUPRC、Brier/ECE、risk-specificity curve、supported-unit yield、concept/
proposition F1、BLEU/ROUGE/BERTScore 都是 secondary/diagnostic，不可替换 primary。

### 20.8 Baselines 与单变量公平性

主表至少冻结：language-only、fixed L1/L2/L3、Absolute-HSG、RC-HSG、Flat-RC、
PMI/LM-prior correction、conventional uncertainty、compute-matched ensemble、
RC-HSG without rank/spread。Absolute-HSG/RC-HSG/Flat-RC 必须共享 A、F、candidate
content、schema/projection、split、training steps、seeds、calibration rows、policy-grid
budget、evaluator 与 test indices。PMI 也共享 candidate content 与 hierarchy；它只把
reference-relative EEG features 换成 frozen LM-prior correction features。

- RC-HSG > PMI：允许声称 matched EEG reference 有独立 utility；
- RC-HSG ≈ PMI：只声称 reference/prior calibration 有用；
- RC-HSG < PMI：删除 matched EEG reference necessity，把论文收缩为一般 reliability
  calibration / prior-correction study；
- compute-matched ensemble 未排除计算收益时，不得把 improvement 归因于 reference。

### 20.9 Claim–evidence 与固定失败路由

| Claim | 必要证据 | 失败后的固定动作 |
|---|---|---|
| unseen-stimulus confidence–specificity misalignment | Absolute-HSG/fixed-depth Regime I risk–specificity | 弱化问题动机 |
| reference 可安全作为 context | Gate R0 | 删除失败 family；全部失败转 ordinary HSG |
| reference 有增量决策价值 | Gate R | 删除 reference-calibrated title claim |
| finite-sample risk certification | Gate C + test risk | 删除 risk-controlled，只写 empirical risk-aware |
| hierarchy 有独立价值 | Gate H | 删除 Hierarchical，保留 Flat-RC |
| matched EEG reference 不只是 LM prior | RC-HSG vs PMI | 收缩为一般 reliability-reference study |
| real/reference semantic separation | Mechanism A | 只删除 EEG attribution，不影响 R/C/H |
| L4 不新增语义 | constrained renderer audit | 只报告 L1–L3 structured output |
| external validity | Regime II/replication | 限定到 fixed subject-pool Regime I |

机器 stop logic：

```text
IF leakage_audit != PASS: STOP all scientific comparisons
IF no pre-registered reference family passes Gate_R0:
    route = ordinary hierarchical selective generation
    forbid reference-calibrated claim
IF Gate_R == FAIL:
    remove reference-calibrated title-level claim
IF Gate_C == FAIL:
    forbid risk-controlled; use empirical risk-aware only
IF Gate_H == FAIL:
    remove Hierarchical; route = Flat-RC
IF RC_HSG <= PMI:
    remove matched-EEG-reference necessity claim
IF Mechanism_A == FAIL:
    remove EEG-attribution/evidence-increment language only
IF risk passes only by near-universal abstention OR Delta_M upper > 0.05:
    anti-abstention FAIL
IF only random split OR one seed OR one subject:
    downgrade to observed-setting result
```

### 20.10 Backbone A owner decision

当前三个 ledger candidates 均不得原样成为 primary：

- `TRUST_ALIGN_A1_SPECTRAL` 的外部 source root 无可核 license，禁止复制/import 其代码；
- `TRUST_ALIGN_LABRAM_A3` 要求未验证的 128-channel mapping、unit scaling、filter details
  与 checkpoint sidecar；
- `OFFICIAL_NEUROLM_B_VQ` 要求 microvolt、standard-1020 mapping、约 4.28 GB 未下载
  weights 和尚未冻结的 adapter；当前 release unit 未知，不能 plug-and-play。

为避免结果驱动选择，并解除 unit/channel/checkpoint blocker，primary A policy 冻结为
**`RC_HSG_NATIVE_SPECTRAL_A1_V1`**：项目内 clean-room、新写、无外部 source code
复制、无 pretrained checkpoint、无 weight download 的低容量 controlled backbone。
LaBraM/NeuroLM 仅可在主方法/route 全部冻结后作 optional descriptive robustness，不能
替换 primary。

固定 interface：

```text
input                 105 x T finite release-native EEG, 500 Hz,
                      exact frozen channel order, common-average processed reference
unit conversion       NONE; microvolt inference forbidden
per-trial transform   channel median centering;
                      scale=max(1.4826*MAD, RMS, 1e-6); clip [-20,20]
window                500 samples, hop 250, Hann; valid-sample mask mandatory
bands Hz              [1,4),[4,8),[8,10),[10,13),[13,20),[20,30),[30,45),[55,75]
features              log relative bandpower per channel/band; fixed epsilon 1e-12
token input           840 dimensions per valid window
projection            Linear(840,256) + GELU + LayerNorm + dropout 0.10
temporal encoder      2 TransformerEncoder layers, d=256, heads=4,
                      FFN=512, dropout=0.10, sinusoidal position, masked attention
outputs               window embeddings H[L,256], mask[L], masked-mean z[256]
initialization        deterministic project-owned random init per frozen main seed
trainability          A is trainable from scratch; no PEFT/checkpoint; all methods share it
prohibited            subject/session ID feature, guessed units, channel interpolation,
                      test-fitted scale, teacher forcing, test text retrieval
```

如果有效 segment 少于 500 samples，必须 fail admission for that row；不得 silent pad
使其成为科学输入。N1/N2、real 与 all baselines 必须经过同一 frontend path。A 只提供
EEG representation；semantic decoder F、candidate schema 和 score API 由后续独立任务
冻结，不能在 A-interface run 中借 test/semantic outcome 决定。

该选择是 feasibility/control 决策，不是性能结论。若 clean-room implementation
无法通过 outer-train-only tensor/admission checks，则报告 A blocker；不得改投 NeuroLM、
LaBraM 或看结果后换 backbone。

### 20.11 Calibration 可行性警告

run 011 的 equal-weight subject macro 只有 18 个 subject clusters。对 `[0,1]` loss，
直接把 18 subjects 当作独立 calibration samples 的 95% distribution-free UCB 很可能
即使零观察损失也无法低于 `alpha_0=0.10`；把 580 rows 或 34 groups 伪装为 iid trial
来绕过这一点是禁止的。因此在实现 Gate C 前新增 outcome-blind
`S0_CALIBRATION_FEASIBILITY_REVIEW`：

1. 明确风险目标究竟是 fixed-subject future-stimulus expectation 还是 subject-population
   expectation；本论文 primary 当前只允许前者；
2. 对候选 UCB 给出 assumptions、independent unit、family size 和 zero-loss lower
   feasibility calculation；
3. 若在 frozen 18-subject contract 下无法认证 0.10，预先把论文主措辞锁为 empirical
   `risk-aware`，不得在看到 test 后改用 trial-iid bound；
4. 不得改变 alpha、delta、cal reserve 或 population 来追求可认证结果。

两阶段 `cal-select/cal-cert` 的数据隔离现在已冻结，但具体 finite-sample theorem/UCB
继续是 blocker，必须由该 review 在任何 calibration outcome 前解决。

### 20.12 新执行图与旧任务迁移

新的关键路径：

```text
S0  DONE data admission → identity/grouping → deterministic split/population
S1  freeze/admit RC_HSG_NATIVE_SPECTRAL_A1_V1 → full leakage audit
S2  freeze L1–L3 schema/evaluator/projection/L4 renderer and candidate content rule
S3  N1/N2 feasibility + implementation → Gate R0
S4  build shared candidates and absolute/reference feature tables on legal train roles
S5  fit/freeze Absolute-HSG and RC-HSG low-capacity reliability models
S6  calibration feasibility review → cal-select → freeze finite policies → cal-cert
S7  pre-test method/route lock; unlock test once
S8  Gate R + Gate C + Gate H on frozen common rows/methods
S9  Mechanism A + PMI/conventional uncertainty/compute-matched baselines
S10 five-seed main table → three-seed ablations → Regime II/replication
S11 writing freeze by the fixed claim-contraction table
```

任务迁移必须保留历史 task IDs 但不得让旧依赖重新执行：旧 `GATE_A1`、`GATE_A`、
`GATE_B`、`S0_NC_HSG_CORE`、`S0_DIRECT_C` 标记 `SKIPPED`，reason=`SUPERSEDED_BY_RC_HSG_V21`
且保留原历史字段。新增 `GATE_R0`、`S0_REFERENCE_FEATURES`、
`S0_RELIABILITY_MODELS`、`S0_CALIBRATION_FEASIBILITY_REVIEW`、`S0_ABSOLUTE_HSG`、
`S0_RC_HSG_CORE`、`S0_FLAT_RC`、`GATE_R`、`GATE_C`、`GATE_H`、`MECHANISM_A`。
现有 `S0_PMI_BASELINE` 可保留 ID，但其 prerequisites/acceptance 改为 RC-HSG 公平性合同。
`ROUTE_LOCK` 改为 pre-test method/claim route lock，必须先于任何 test-value read。

### 20.13 本轮必须落库的状态迁移

下一 Codex run 只做 scientific-governance activation 与 A-policy materialization：

```text
SPEC_V21_REVIEW
-> S0_SCIENTIFIC_REDESIGN_FREEZE
-> S0_A_POLICY_REVIEW
-> S0_A_INTERFACE READY
-> stop
```

必须新增：

```text
guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md
artifacts/spec_review/rc_hsg_v21_scientific_redesign_review.md
artifacts/backbone_a_policy.yaml
runs/2026-08-24_012_rc_hsg_scientific_redesign_freeze.md
```

更新 active entry points、PROJECT_STATE、TASKS、HANDOFF、root next task、validator/status
tests 和 implementation matrix。成功态：

```text
project.name               rc_hsg_eeg_text
project.spec_version       v2.1
route.primary              RC-HSG
SPEC_V21_REVIEW            DONE
S0_SCIENTIFIC_REDESIGN_FREEZE DONE
S0_A_POLICY_REVIEW         DONE
S0_A_INTERFACE             READY, owner=CODEX
last_completed_task        S0_A_POLICY_REVIEW
recommended_next_task      S0_A_INTERFACE
stage_0/READY
```

`artifacts/backbone_a_policy.yaml` 必须逐字段记录 §20.10 的 selection/rejections、exact
interface、外部代码不复制、无下载、未知单位处理、fail-closed 与 robustness boundary。
本 run 不实现 frontend、不读 EEG、不运行 leakage audit、不构造 reference、不训练。

### 20.14 硬停止线

本版本激活 run 禁止：读取真实 EEG value、stimulus/test outcome、calibration result、
历史 model metric；下载/import/copy trust_align、LaBraM 或 NeuroLM code/weights；实现或
训练 A/F/schema/reference/reliability model；运行 full leakage audit、Gate R0/R/C/H/
Mechanism A；改 split/grouping/bootstrap；解锁 test；把旧 Gate A 重新设为 prerequisite；
或由 Codex自行选择 feature/model/reference/calibration theorem。

任何 active entry、task graph、state、hash、baseline 或 fixed decision 冲突时报告
`STATE_SPEC_CONFLICT` 并停止。完成 v2.1 activation 后，下一轮只能按新的精确指令实现
`S0_A_INTERFACE`，不能顺带开始 semantic model 或读取 held-out outcome。

---

## 21. v2.2：A interface、短片段总体保持与 run 013 合同

### 21.1 当前仓库事实与本轮研究裁决

run 012 已在远程 `main@91997faa1de1616d1eb662cd36edc1547613206d` 完成
RC-HSG activation。仓库恢复必须得到：67 tasks、29 DONE、8 SKIPPED、29 BLOCKED、
唯一 READY/推荐任务 `S0_A_INTERFACE`，owner=`CODEX`；test 仍
`LOCKED_UNTIL_ROUTE_LOCK`。当前冻结输入如下：

| 输入 | SHA256 / 固定值 |
|---|---|
| `artifacts/backbone_a_policy.yaml` | `034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/data_card.yaml` | `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84` |
| `artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml` | `50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf` |
| `requirements-trust-align.lock.txt` | `72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910` |
| channel-order contract | `23b8d1ee22d87560fe1a6384141b2713c450ca34ef9eeff8241e7bd3bd885ef5` |

analysis-view metadata 的 `raw_samples` 在 5,905 rows 中为 24–27,010；按已冻结的
500-sample window，73 rows 太短，其中 train-fit/inner-val/cal/test 分别为
35/9/15/14。若把它们删除，会改变冻结 population、偏向性地移除较短/可能较难的 trial，
并使方法比较的共同 row set 发生变化；若 pad 到 500，则会把人工信号送入 A。两者均
不可接受。

因此 §20.10 的“fail admission for that row”只表示 **不得调用 A frontend**，不表示
从论文 population、风险分母或 paired comparison 中删除该 row。唯一允许路由为：

```text
raw_samples < 500
-> A_INTERFACE_SHORT_SEGMENT
-> no frontend call, no padding, no imputation
-> every A-dependent primary/comparison method forced to L0 abstention
-> D=0, semantic miss=1, risk=0 under the frozen metric definitions
-> row remains in the same subject/role/population and paired common-row set
```

该路由必须对 RC-HSG、Absolute-HSG、Flat-RC、PMI correction、conventional uncertainty、
compute-matched ensemble、N1、N2 与所有共享 A 的方法一致。language-only 等不依赖 A 的
diagnostic 不得借此进入 confirmatory paired set；主比较仍按同一 5,905-row population。
`raw_samples`、`window_count`、eligibility status 与 padding amount 均禁止成为 reliability
model、candidate、route policy 或 semantic model feature。

### 21.2 公共输入、metadata 与 fail-closed API

项目内新增 package `src/rc_hsg/backbones/native_spectral_a1.py`。公共输入必须是：

```text
eeg                 floating Tensor [B, 105, T]
valid_samples       integer Tensor [B], 500 <= valid_samples[b] <= T
channel_order_hash  exact frozen SHA256 string
sampling_hz         exact integer 500
unit_status         exact RELEASE_NATIVE_AMPLITUDE_UNRESOLVED
processed_reference exact common-average
```

公开符号固定为 `AInterfaceContractError`、frozen dataclass
`NativeSpectralA1Output` 与 `NativeSpectralA1(torch.nn.Module)`。constructor 精确为
`NativeSpectralA1(init_seed: int)`；forward 精确为
`forward(eeg, valid_samples, *, channel_order_hash, sampling_hz, unit_status,
processed_reference) -> NativeSpectralA1Output`。contract errors 的 message 必须以稳定 code
之一开头：`A_INPUT_RANK`、`A_INPUT_DTYPE`、`A_INPUT_CHANNELS`、`A_INPUT_DEVICE`、
`A_METADATA_MISMATCH`、`A_VALID_SAMPLES`、`A_SHORT_SEGMENT`、`A_NONFINITE`。测试只依赖
这些 code prefix，不依赖任意自然语言尾缀。

committed release schema 是 `[samples, channels]`；未来 loader 必须显式 transpose 为
`[B,105,T]`。A 自身不得猜轴、自动 transpose、截断 channel、补 channel、插值、重采样、
单位转换或 reference conversion。missing/wrong metadata、非浮点输入、rank/axis/channel
不符、`valid_samples` 越界、有效 slice 内任何非有限值都抛出稳定的 contract error。
padding tail 不参与 finite check、归一化、FFT 或 pooling；混合 batch 中出现 short row
则整个 frontend call fail，pipeline 必须先依据 §21.5 overlay 把 short rows 路由到 L0。
不得隐式搬运 CPU/GPU；input 与 model 参数必须同 device。

### 21.3 固定预处理与频谱 token

每个 trial、每个 channel 只在前 `valid_samples[b]` 内独立计算：

\[
c=x-\operatorname{median}(x),\quad
s=\max(1.4826\operatorname{median}(|c|),\sqrt{\operatorname{mean}(c^2)},10^{-6}),
\quad \tilde x=\operatorname{clip}(c/s,-20,20).
\]

禁止跨 trial/subject/split 拟合 scale；release-native amplitude status 保持未解析，禁止
声称 microvolt。只取完整窗：window=500、hop=250、start=`0,250,...` 且
`start+500<=valid_samples`；窗口数
`1+floor((valid_samples-500)/250)`，尾部不足完整窗口直接丢弃，绝不 pad。Hann 必须是
symmetric/`periodic=False`。

频谱计算固定为 float32、`rfft(n_fft=500, norm="backward")`、500 Hz，故频点间隔
1 Hz；power 为复数模平方并按频点求和。分母是 `[1,75)` Hz 的全部 bins 1–74，包含
45–54 Hz；分子依次是以下 half-open bands：

```text
[1,4), [4,8), [8,10), [10,13), [13,20), [20,30), [30,45), [55,75)
```

对应频点数必须为 `3,4,2,3,7,10,15,20`。每 channel/band 特征固定为：

\[
f_{c,k}=\log\frac{P_{c,k}+10^{-12}}{P_{c,[1,75)}+10^{-12}}.
\]

按 channel-major、channel 内 band-major 展平成 840 维；不得用均值替代 band-power sum、
不得把 45–54 Hz 加成第九 band、不得改 log/epsilon/FFT normalization。实现可在当前
device 计算，但 run-013 的 synthetic canonical self-check 在 CPU float32；不同 device
之间只要求数值容差一致，不声称 byte-identical 浮点输出。

### 21.4 固定 trainable encoder 与输出

840-d token 依次通过：

```text
Linear(840,256,bias=True)
GELU(approximate="none")
LayerNorm(256,eps=1e-5)
Dropout(0.10)
standard sinusoidal position, no learned parameters
2 x TransformerEncoderLayer(
    d_model=256, nhead=4, dim_feedforward=512,
    dropout=0.10, activation="gelu", batch_first=True, norm_first=True
)
final LayerNorm(256,eps=1e-5)
```

position (p) 使用标准 `sin/cos(p/10000^(2i/256))`。Transformer 的
`src_key_padding_mask` 必须来自 full-window mask；masked positions 在最终输出显式置零，
pooled embedding 是 valid windows 的算术均值。返回固定 dataclass：

```text
window_embeddings  float Tensor [B,Wmax,256]
window_mask        bool Tensor [B,Wmax]
pooled_embedding   float Tensor [B,256]
```

总 trainable parameter count 必须精确为 **1,270,528**：projection 215,296；projection
LayerNorm 512；每个 Transformer layer 527,104；两层 1,054,208；final LayerNorm 512。
fixed tokenizer 与 sinusoidal position 无 trainable parameter。

constructor 接受显式 integer `init_seed`，先在 CPU 构造且不得污染 caller RNG；所有
二维/matrix weights（含 MHA packed matrix）使用 Xavier-uniform gain 1，所有 bias=0，
所有 LayerNorm weight=1/bias=0。相同 seed 的 `state_dict` 和 eval output 必须一致，
不同 seed 至少有一个 trainable tensor 不同。run 013 只验证 seed contract，不替作者
选择主实验 seed 值。不得调用网络、外部 repo、pretrained API 或下载/import weight。

### 21.5 outcome-blind eligibility overlay

新增 production builder `scripts/build_a_interface_contract.py`，production CLI 只允许可选
`--output-root`，不得接受 input path、threshold、band、model、seed 或 feature 参数。它
只读 §21.1 的 committed policy/analysis-view/split/data-card/targeted-manifest/lock metadata，
不得打开任何 EEG source locator、MAT file、stimulus text、semantic outcome、prediction、
metric 或 historical model result。

生成：

```text
artifacts/backbone_a_contract.yaml
artifacts/a_interface_eligibility_v1.jsonl
reports/a_interface_contract.md
```

YAML 顶层 key 至少且仅按以下 canonical 顺序出现；各 nested field 逐项复制 §21 固定事实，
不允许加入 performance/result：

```text
schema_version, artifact, policy_id, spec_version, baseline_commit,
input_artifacts, input_contract, preprocessing_contract, spectral_contract,
encoder_contract, output_contract, initialization_contract,
eligibility_contract, acceptance_counts, implementation,
prohibited_features, prohibited_actions, evidence_scope
```

固定 header 值为 `schema_version: 1`、
`artifact: RC_HSG_NATIVE_SPECTRAL_A1_CONTRACT_V1`、policy ID、`spec_version: v2.2` 与
baseline commit；`implementation` 记录 code path/SHA256、Python/Torch/NumPy 版本、
trainable parameter count 和 `real_eeg_validated: false`。`evidence_scope` 精确为
`SYNTHETIC_INTERFACE_AND_COMMITTED_METADATA_ONLY_NO_REAL_EEG_VALUES_NO_OUTCOMES`。

JSONL 按 `(subject,slot,occurrence_id)` canonical 排序，每 row 恰含：

```text
occurrence_id, subject, slot, role, calibration_reserve,
raw_samples, window_count, a_interface_status, action
```

`role` 只能是 split 原值 `train_fit|inner_val|cal|test`；`calibration_reserve` 只能是
`null|cal_select_reserve|cal_cert_reserve`，非-cal row 必须 null。

其中 eligible row 为 `status=ELIGIBLE, action=RUN_FRONTEND`；short row 为
`status=A_INTERFACE_SHORT_SEGMENT, window_count=0,
action=FORCED_L0_NO_FRONTEND`。不得复制 source locator、stimulus hash/text、EEG 值或
outcome。builder 必须验证 5,905 rows 一对一映射、105 channels、`[samples,105]`、冻结
channel hash、sampling/reference/unit status、split role 与全部输入 hash，并 fail closed
于 symlink、path escape、schema/hash/order/count/unknown-arg mismatch；写入必须原子化。

固定 outcome-blind acceptance counts：

| role | total rows | eligible | forced L0 | full windows |
|---|---:|---:|---:|---:|
| train-fit | 2,832 | 2,797 | 35 | 29,263 |
| inner-val | 709 | 700 | 9 | 6,482 |
| calibration | 1,171 | 1,156 | 15 | 11,558 |
| locked test | 1,193 | 1,179 | 14 | 13,219 |
| total | 5,905 | 5,832 | 73 | 60,522 |

calibration reserve 细分必须是 cal-select 582 eligible/9 short，cal-cert 574 eligible/6
short。两次 repo-external production build 的三个文件必须 byte-identical。这里只冻结
metadata eligibility，不是 real-data frontend admission，也不允许根据这些 counts 改
window threshold、population 或 method。

### 21.6 synthetic tests 与证据边界

新增 `tests/test_native_spectral_a1.py` 与 `tests/test_build_a_interface_contract.py`，至少覆盖：

1. input/output shape、mask、500/749/750 samples 的 full-window count 与 trailing discard；
2. wrong axis/channel/hash/rate/unit/reference、short valid length、有效 slice 非有限值 fail；
3. padded tail 被完全忽略，no auto-transpose/pad/interpolation/unit conversion；
4. constant/finite input 稳定、正 amplitude scaling invariance、单频 sine 落入唯一正确 band；
5. exact band bins/feature order/Hann/FFT/epsilon 与 1,270,528 parameter count；
6. same-seed state/output determinism、different-seed difference、eval repeatability；
7. masked output zero、masked-mean correctness、finite forward/backward parameter gradients；
8. builder fixed input hashes、exact 5,905/5,832/73/60,522 counts、role/reserve counts、
   canonical schema/order、two-build determinism、tamper/symlink/path/unknown-arg fail closed；
9. source/import scan 证明无 external source code、network、checkpoint、weight、EEG reader。

所有 model assertions 只用程序生成的 synthetic tensors；builder 只用 committed metadata。
synthetic PASS 只能写作 interface contract implemented，不得写作 physical EEG admission、
representation quality、reference feasibility、performance 或 Gate evidence。当前本地审查
运行时没有 PyTorch；因此 run-013 必须在服务器冻结环境实际运行这些 tests，不能用静态
审查或 skip 冒充 PASS。

### 21.7 任务依赖纠正与 run-013 唯一状态迁移

v2.1 图中 `S0_LEAKAGE_AUDIT` 只依赖 `S0_A_INTERFACE` 与 split，会在 interface 完成后
与 `S0_A1_FRONTEND` 同时 READY，违背单一下一任务纪律。依赖改为：

```text
S0_A_INTERFACE
-> S0_A1_FRONTEND
-> S0_LEAKAGE_AUDIT
-> S0_A1_ADMISSION
```

`S0_LEAKAGE_AUDIT.prerequisites` 必须精确包含 `S0_A1_FRONTEND` 与 `S0_JOINT_SPLIT`；
`S0_A1_ADMISSION` 继续依赖 frontend、split、leakage audit。run 013 唯一链：

```text
SPEC_V22_REVIEW
-> S0_A_INTERFACE
-> S0_A1_FRONTEND READY
-> stop
```

新增 task `SPEC_V22_REVIEW` 并完成；`S0_A_INTERFACE` 完成。成功态恰为 68 tasks、31 DONE、
8 SKIPPED、28 BLOCKED、唯一 READY `S0_A1_FRONTEND`，owner=`CODEX`。原
`B_V7_A_INTERFACE_UNIMPLEMENTED` 迁入 superseded/closed evidence；新增 active
`B_V8_A_REAL_FRONTEND_UNVALIDATED`，其 reason 明确 synthetic interface 已实现但真实
outer-train tensor、finite-value、device/memory 与 admission 未验证；它阻塞
`S0_LEAKAGE_AUDIT`、`S0_A1_ADMISSION`、N1/N2、Gate R0 与全部 A-dependent downstream，
但不阻塞 READY 的 `S0_A1_FRONTEND`。

PROJECT_STATE 必须更新：

```text
project.spec_version       v2.2
project.spec_path          guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md
project.baseline_commit    91997faa1de1616d1eb662cd36edc1547613206d
project.reviewed_commit    91997faa1de1616d1eb662cd36edc1547613206d
project.repository_status  RC_HSG_V22_A_INTERFACE_IMPLEMENTED_REAL_FRONTEND_PENDING
last_completed_task        S0_A_INTERFACE
recommended_next_task      S0_A1_FRONTEND
last_run                   runs/2026-08-24_013_native_spectral_a_interface.md
execution.stage/status     stage_0/READY
```

同步更新 active entry points、HANDOFF、root next task、implementation matrix、validator、
status 与 project-memory tests；保留所有旧 SPEC/review/run/task/artifact 为 provenance。

### 21.8 run 013 交付、验证与硬停止线

新增：

```text
guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md
artifacts/spec_review/rc_hsg_v22_a_interface_review.md
src/rc_hsg/__init__.py
src/rc_hsg/backbones/__init__.py
src/rc_hsg/backbones/native_spectral_a1.py
scripts/build_a_interface_contract.py
tests/test_native_spectral_a1.py
tests/test_build_a_interface_contract.py
artifacts/backbone_a_contract.yaml
artifacts/a_interface_eligibility_v1.jsonl
reports/a_interface_contract.md
runs/2026-08-24_013_native_spectral_a_interface.md
```

除所有现有 tests 外，必须运行两组新 tests、validator、status、`git diff --check`；不得
skip。run 013 记录 baseline/import hashes、exact math/API、parameter count、eligibility
counts/hashes、two-build determinism、测试版本与结果，并明示 no real EEG value read、
no semantic/test/calibration outcome、no training/checkpoint/download/external code、no F/schema/
reference/reliability/GLM、no full leakage audit/Gate/test unlock。

本 run 禁止读取或 mmap 任何真实 EEG array，禁止用 real data 验证 tensor，禁止训练或
做 optimizer step，禁止冻结主 seeds/optimizer，禁止实现 F、candidate、schema、N1/N2、
reference、reliability、calibration 或 baseline，禁止运行 full leakage audit/Gate，禁止
改 grouping/split/population/bootstrap，禁止删除 short rows、改变 500/250 threshold 或
解锁 test。任何 fixed hash/count/API/task/state 冲突报告 `STATE_SPEC_CONFLICT` 并停止；
代码/环境测试失败报告 `A_INTERFACE_IMPLEMENTATION_BLOCKED`，不得静默换 backbone、频带、
window、padding、dtype 或依赖版本。

---

## 22. v2.3：bounded real A-frontend self-check 与 leakage 分层

### 22.1 run-013 验收与当前事实

远程 `main@237788090dcb20e533f304f63ae8feb2f545fe0b` clean，run 013 已完成。恢复
必须得到 68 tasks、31 DONE、8 SKIPPED、28 BLOCKED、唯一 READY/推荐
`S0_A1_FRONTEND`；validator/status PASS，test 仍 `LOCKED_UNTIL_ROUTE_LOCK`。服务器
run record 报告 full discovery 147/147、no skip；独立本地审查因没有 PyTorch/h5py 只复跑
可用的 project-memory 50、joint split 13、identity 12、similarity 12、analysis view 11、
input audit 8，全部 PASS，不能把未复跑 suite 冒充本地结果。

固定输入：

| 文件 | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md` | `a5d6d695f21a72dd2e3d8445771b6b3d772f0a42282ad5ce9feaa6e43da01911` |
| `artifacts/backbone_a_policy.yaml` | `034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425` |
| `artifacts/backbone_a_contract.yaml` | `4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac` |
| `artifacts/a_interface_eligibility_v1.jsonl` | `8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad` |
| `src/rc_hsg/backbones/native_spectral_a1.py` | `71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/data_card.yaml` | `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84` |
| `artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml` | `50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf` |
| `artifacts/admission/zuco2_osf_file_metadata.yaml` | `85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721` |
| `requirements-trust-align.lock.txt` | `72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910` |

run 013 的 implementation/contract/eligibility/report hashes 与 §21 一致。A code review 未发现
改变 channel、window、band、feature order、mask、parameter count 或 short routing 的
证据。本轮不是算法重选，也不修改 A code，除非 validator 发现 `STATE_SPEC_CONFLICT`。

### 22.2 为什么 frontend self-check 不能等同 full admission

outer-train 仅指 Regime-I `train_fit|inner_val`：总 3,541 rows，其中 3,497 eligible、
44 short，完整窗口 35,745。一次性把 3,497 rows 全部读取并称作 `S0_A1_FRONTEND` 会使
后续 `S0_A1_ADMISSION` 失去独立含义，也扩大首次真实值读取面。相反，仅用一个随意 smoke
row 无法覆盖 subject、role、length/mask 与最大内存形状。

因此任务边界冻结为：

1. `S0_A1_FRONTEND`：预先固定的 107-row real-value audit panel；验证 loader 与 A 的
   真实全链路、重复性、batch/padding/device behavior；不是 full admission。
2. `S0_LEAKAGE_AUDIT`：随后只审计 split/data/A path 和此次读取白名单。
3. `S0_A1_ADMISSION`：在早期 leakage PASS 后，才对全部 3,497 eligible outer-train
   rows 作正式 streaming admission；剩余 3,390 rows 不得在 run 014 提前读取。

cal/test EEG、semantic outcome、stimulus text、prediction、metric、历史 model result 均不
属于任何 run-014 输入。opening HDF5 container 不等于授权 dereference 其他 cell；代码必须
证明只 dereference audit-panel eligible cells。

### 22.3 outcome-blind audit-panel 冻结

只从 committed eligibility overlay 选择。eligible 先限制
`role in {train_fit,inner_val}`，window-count strata 固定为：

```text
W01_04   1 <= window_count <= 4
W05_16   5 <= window_count <= 16
W17_PLUS window_count >= 17
```

对每个非空 `(subject,role,stratum)` cell，按 `(occurrence_id,slot)` 升序取第一 row；禁止
搜索 seed、amplitude、tensor value 或 outcome。该规则在当前 metadata 恰产生 105 rows：
train-fit 54、inner-val 51；W01_04/W05_16/W17_PLUS 为 34/36/35；覆盖全部 18 subjects。

另对每个 role 选一个 memory stress row：先最大化 `(window_count,raw_samples)`，再按
`(occurrence_id,subject,slot)` 升序破平。当前两个 stress rows 不与前 105 重复，故真实
frontend panel 固定为 **107 rows**：train-fit 55、inner-val 52、总 1,452 windows，
metadata length 572–18,436，最大 72 windows。`init_seed=20260824` 只作为 audit seed，
标记 `AUDIT_ONLY_NOT_MAIN_EXPERIMENT_SEED`；不得由此冻结主实验 seeds。

所有 44 个 outer-train short rows（train-fit 35、inner-val 9）也进入 panel ledger，
selection reason=`ALL_OUTER_TRAIN_SHORT`，但 `source_dataset_read=false`、
`action=FORCED_L0_NO_FRONTEND`。因此 ledger 共 151 rows；真正 dereference/read real array
恰为 107 distinct rows，short/cal/test dereference 必须为零。

新增 `artifacts/a1_frontend_audit_panel_v1.jsonl`，canonical order
`(subject,slot,occurrence_id)`，每 row fields 精确为：

```text
subject, slot, occurrence_id, role, raw_samples, window_count,
selection_reason, a_interface_status, action,
source_file, source_field, source_dataset_read
```

eligible selection reason 只能是 `STRATIFIED_CELL|ROLE_MAX_STRESS`；若一般实现中同 row
兼具二者则 `STRATIFIED_AND_ROLE_MAX`，但本 baseline 必须复现 105+2 distinct。short reason
只允许 `ALL_OUTER_TRAIN_SHORT`。`source_field` 固定 `rawData`；不得写 stimulus hash/text、
EEG/output value、tensor hash、amplitude summary 或 device-specific embedding。

### 22.4 dataset root、HDF5 与 loader firewall

production dataset root 固定从 targeted manifest 验证为：

```text
/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0
```

production CLI 只允许可选 `--output-root`；不得接受 dataset path、role、subject、slot、
threshold、seed、device、batch、dtype 或 model 参数。函数级 tests 可注入 isolated fixture
root。拒绝 root/path component symlink、path escape、missing/unexpected summary file、size
drift、manifest/hash/schema drift 和 HDF5 external link。18 个 summary file 只复用 run-005
已验证 SHA256，production 本轮检查 exact relative path + committed size，不重新 hash 34.6 GB。

每个允许 row 只可：打开其 subject 的 `results{subject}_NR.mat` read-only；读取
`sentenceData/rawData[slot-1,0]` 的同文件 object reference；要求 target 为 numeric floating
HDF5 dataset，logical shape 精确 `[raw_samples,105]`。不得读取 `content`、`word`、
`wordbounds`、fixation/feature fields 或另一个 slot。不得自动 transpose 错误 source shape；
只在 exact `[T,105]` 后执行显式 `.T` 得到 `[1,105,T]`。

raw array 必须先在 source dtype 检查全有限，再作唯一允许的数值转换：contiguous native
float32 cast；这是 computation dtype cast，不是 physical-unit conversion。cast 后再次要求
finite，不乘 scale、不猜 microvolt、不 rereference、不 resample、不 interpolate。传入
`valid_samples=[T]` 与 §21 exact metadata。short row 的 object reference 本身也不得
dereference。

### 22.5 固定 real-tensor 自检算法

新增 `scripts/validate_a1_frontend.py`。model 固定 `NativeSpectralA1(20260824).eval()`，
CPU float32 是 canonical path，全部 forward 在 `torch.inference_mode()`；optimizer、loss、
backward、parameter update 与 cache write 禁止。model parameters 在 run 前后必须 exact
unchanged。

panel 按 `(window_count,subject,slot)` 排序，以最多 4 rows streaming batch；每批 raw arrays
只读一次、验证后释放。对每 row/batch 必须同时通过：

1. individual CPU eval 重复两次 byte/exact equal；
2. expected window count、all-valid single-row mask、finite embeddings/pool 与 masked mean；
3. batch 输入显式 pad 到 batch max T，zero-tail 与 NaN-tail 两次结果 exact equal，证明
   padding tail 未读取；
4. individual 与 batch valid outputs 在 `rtol=2e-5, atol=2e-5` 内一致；
5. parameter state 未变、grad 全为 null、无 training mode、无 output/cache/tensor hash 落盘；
6. source dtype 只能 float32/float64；actual dtype counts 可记录为 schema diagnostic，但
   不记录 amplitude/value distribution。

若 `torch.cuda.is_available()`，另取每 subject 在 107-row panel 中按
`(occurrence_id,role,slot)` 最小的一 row，再并入两个 role stress rows；当前应为 20 rows、
199 windows。用同一 CPU state 移到 CUDA、禁止 TF32，比较 CPU/CUDA valid outputs
`rtol=2e-4, atol=2e-4`；available 而失败即 blocker。CUDA 不可用记录
`NOT_AVAILABLE_NONBLOCKING`，CPU canonical PASS 仍可完成本 task；不得下载/切换 Torch。

两次 repo-external production builds 必须对三个输出 byte-identical，随后生成 canonical
outputs。artifact/report 不写 wall-clock、RSS、绝对 dataset path、tensor/output hash 或
浮点值，故 determinism 只证明 selection/contract/report，不宣称跨设备 floating output
byte-identical。

### 22.6 固定产物与 acceptance

新增：

```text
scripts/validate_a1_frontend.py
tests/test_validate_a1_frontend.py
artifacts/a1_frontend_audit_panel_v1.jsonl
artifacts/a1_frontend_freeze.yaml
reports/a1_frontend_selfcheck.md
runs/2026-08-24_014_a1_real_frontend_validation.md
```

`artifacts/a1_frontend_freeze.yaml` 顶层 canonical keys：

```text
schema_version, artifact, spec_version, baseline_commit, task, policy_id,
evidence_scope, input_artifacts, authorized_scope, panel_contract,
source_identity_contract, loader_contract, execution_contract,
acceptance_counts, check_results, implementation, prohibited,
safety, downstream_boundary
```

header 固定 `schema_version: 1`、
`artifact: RC_HSG_A1_REAL_FRONTEND_VALIDATION_V1`、`spec_version: v2.3`、baseline、task、
policy；evidence scope 精确为
`BOUNDED_OUTER_TRAIN_REAL_EEG_FRONTEND_SELF_CHECK_NO_OUTCOMES_NO_TRAINING_NOT_FULL_ADMISSION`。
`implementation` 记录 validator code hash、Python/Torch/NumPy/h5py versions、audit seed、
CPU/CUDA status；不记录时间或性能。`downstream_boundary` 必须写
`full_outer_train_admission_completed: false`、`remaining_eligible_rows_not_read: 3390`、
`next_task: S0_LEAKAGE_AUDIT`。

PASS 必须同时满足 exact committed hashes、3,541/3,497/44/35,745 outer-train metadata、
151 ledger、107 real rows、44 no-read short rows、1,452 panel windows、18 subjects、两个
roles、18 source files path/size、0 cal/test/short dereference、全部 source/loader/numeric/mask/
repeat/batch/padding/parameter checks以及 conditional CUDA rule。任何 failure 原子不写 partial
PASS，报告 `A1_FRONTEND_VALIDATION_BLOCKED`；不得改 panel/window/dtype/tolerance/model。

tests 至少覆盖 selection/count/order、HDF5 exact-slot access、cal/test/short non-dereference、
shape/dtype/nonfinite/cast、explicit transpose、individual-repeat、batch/padding isolation、
parameter immutability、CUDA conditional logic、input tamper、symlink/path/external-link、atomic
failure、unknown CLI args、two-build determinism 与 no-value/no-text/no-cache output schema。
fixture 使用程序生成 HDF5/EEG；production run 才读取上述 107 real rows。

### 22.7 leakage task 拆分

当前 `S0_LEAKAGE_AUDIT` acceptance 同时要求 A/data split firewall 与尚未实现的 schema、
candidate、reference、reliability、calibration/test-time code，若在 A admission 前执行会
必然不可完成。v2.3 不降低审计，而是拆成两个有正确依赖的 task：

1. 保留 ID `S0_LEAKAGE_AUDIT`，title 改为
   `Audit Regime-I data split and A-frontend leakage firewall`；prerequisites 精确
   `[S0_A1_FRONTEND,S0_JOINT_SPLIT]`；produces
   `artifacts/a_path_leakage_assertions.yaml`、`reports/a_path_leakage_audit.md`。它只审计
   source/role allowlist、train-fit/inner-val、short bypass、no cal/test dereference、无跨-row
   normalization/fitting、no output cache 与 fail-closed loader。
2. 新增 BLOCKED `S0_METHOD_LEAKAGE_AUDIT`，审计 schema/candidate/reference/reliability/
   calibration/baseline/test-time retrieval 与 route-lock firewall；prerequisites 精确为
   `S0_A1_ADMISSION,S0_SCHEMA_AUDIT,S0_REFERENCE_FEATURES,S0_RELIABILITY_MODELS,
   S0_CALIBRATION_CONTRACT,S0_ABSOLUTE_HSG,S0_RC_HSG_CORE,S0_FLAT_RC,S0_PMI_BASELINE`；
   produces `artifacts/method_leakage_assertions.yaml`、`reports/method_leakage_audit.md`。

`ROUTE_LOCK` 和 `MAIN_EXPERIMENT` 的 leakage prerequisite 改为
`S0_METHOD_LEAKAGE_AUDIT`；Gate R0、S0 semantic/schema 早期链仍依赖
`S0_LEAKAGE_AUDIT`。旧 task/history 不删。任何地方不得用早期 A-path PASS 声称完整方法
leakage PASS。

### 22.8 run-014 状态迁移

唯一执行链：

```text
SPEC_V23_REVIEW
-> S0_A1_FRONTEND
-> S0_LEAKAGE_AUDIT READY
-> stop
```

新增并完成 `SPEC_V23_REVIEW`；新增 `S0_METHOD_LEAKAGE_AUDIT` 为 BLOCKED；完成
`S0_A1_FRONTEND`。成功态恰为 **70 tasks、33 DONE、8 SKIPPED、28 BLOCKED、唯一 READY
`S0_LEAKAGE_AUDIT`**，owner=`CODEX`。B_V8 迁入 superseded evidence；新增 active
`B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING`，明确 bounded panel PASS 不是 full admission，
阻塞 N1/N2/Gate R0/reference/features/models，但不阻塞用来解除它的未来
`S0_A1_ADMISSION`；其 resolution 是 early leakage PASS 后全量扫描剩余 3,390 eligible
outer-train rows。

PROJECT_STATE：

```text
project.spec_version       v2.3
project.spec_path          guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md
project.baseline_commit    237788090dcb20e533f304f63ae8feb2f545fe0b
project.reviewed_commit    237788090dcb20e533f304f63ae8feb2f545fe0b
project.repository_status  RC_HSG_V23_REAL_FRONTEND_SELFCHECK_PASSED_A_LEAKAGE_PENDING
last_completed_task        S0_A1_FRONTEND
recommended_next_task      S0_LEAKAGE_AUDIT
last_run                   runs/2026-08-24_014_a1_real_frontend_validation.md
execution.stage/status     stage_0/READY
```

同步 AGENTS、AI_START_HERE、HANDOFF、root next task、implementation matrix、validator/status/
tests。旧 SPEC/review/run 和 run-013 outputs byte-immutable。test 继续 locked。

### 22.9 run-014 硬停止线

本 run 仅授权读取 107 个 frozen panel 的 `rawData` real arrays；禁止读取剩余 3,390
eligible outer-train、44 short arrays、任何 cal/test array、stimulus text、semantic/
calibration/test outcome、prediction、metric 或 historical model result。禁止训练/backward/
optimizer、保存 embeddings/tokens/waveform/output hash、修改 A、选择主 seeds、实现 full
admission/A-path leakage/method leakage/F/schema/candidates/N1/N2/reference/reliability/
calibration/baseline/Gate、改 split/population/window/short route 或解锁 test。

run record 必须明确 real values read 的 exact bounded scope、no-value-emission、panel/output
hashes、tests、task/blocker migration 与未完成边界。fixed hash/count/selection/API/state 冲突
报告 `STATE_SPEC_CONFLICT`；real source/loader/tensor/device check 失败报告
`A1_FRONTEND_VALIDATION_BLOCKED`，停止且不得以 synthetic PASS 覆盖。

---

## 23. v2.4：no-new-real-value A-path leakage audit 与 run 015 合同

### 23.1 run-014 验收、仓库事实与下一研究裁决

独立复核基线为 clean `main@dc105709563cf9eb216f1c28f82fdf754e7b0683`；
`HEAD=origin/main`、porcelain 为空。`scripts/check_project_state.py` 与
`scripts/project_status.py` PASS，恢复状态恰为 **70 tasks、33 DONE、8 SKIPPED、28
BLOCKED、唯一 READY `S0_LEAKAGE_AUDIT`**，owner=`CODEX`；test 仍为
`LOCKED_UNTIL_ROUTE_LOCK`，route 未锁。

run 014 的 bounded real-value 证据予以接受：151-row ledger 中 107 distinct real rows、
44 short no-read rows；18 subjects、train-fit/inner-val 55/52、1,452 windows；剩余 3,390
eligible outer-train arrays、全部 short/cal/test arrays 仍未读。CPU 全检查 PASS；服务器有
CUDA 时 frozen 20-row/199-window parity PASS。服务器 run record 报告 full discovery
161/161 no skip。独立 review 环境的 Python 没有 `pytest`，因此本轮只接受服务器 committed
run record 为完整 suite 执行证据，不把本地静态审查冒充 test execution。

固定的 run-014 evidence hashes：

| 文件 | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md` | `f5fdb4f9815cb519cc44a214c5c75812d3ebffdd007314304f20e544ae15ba9a` |
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/a_interface_eligibility_v1.jsonl` | `8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad` |
| `artifacts/backbone_a_policy.yaml` | `034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425` |
| `artifacts/backbone_a_contract.yaml` | `4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac` |
| `src/rc_hsg/backbones/native_spectral_a1.py` | `71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9` |
| `scripts/build_a_interface_contract.py` | `153d887b7eafb605745eafd820162f5f636ff9fef40b0e4ef14d4db5d93ef964` |
| `scripts/build_joint_split.py` | `794083d43d7c15cfb970e22699e1504738393b015198f77edcca524a85a81b5b` |
| `scripts/validate_a1_frontend.py` | `ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd` |
| `artifacts/a1_frontend_audit_panel_v1.jsonl` | `95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed` |
| `artifacts/a1_frontend_freeze.yaml` | `817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66` |
| `reports/a1_frontend_selfcheck.md` | `703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503` |

本轮研究裁决是：early audit 应当验证“被冻结的读取实现是否机械封闭”，而不是再读一次
真实数据。重复打开 107 个已验收数组不会增加 leakage 结论，只会扩大数据接触；读取剩余
3,390 行则会越权吞并 `S0_A1_ADMISSION`。因此 run 015 的 production audit **不得打开任何
`.mat`/HDF5、不得导入或执行 real validator、不得读取任何 EEG value**。

### 23.2 证据三角测量与可写结论上限

`S0_LEAKAGE_AUDIT` 采用三类互补证据：

1. **committed metadata/evidence cross-check**：split、eligibility、panel、freeze 与 report
   的 hash、schema、key、role、count 和 no-read 边界一致；
2. **function-scoped AST semantic audit**：解析 frozen source，而不是用任意 grep；检查真实
   dereference guard、同文件/同 slot/rawData 路径、valid-slice per-row preprocessing、
   inference-only 和 output allowlist；
3. **synthetic fixture + mutation evidence**：已有 frontend tests 只用 repository-external
   synthetic HDF5 验证 loader fail-closed；新增 audit tests 和内存 mutation probes 必须证明
   角色放宽、guard 删除、跨-row fit、cache/training/CLI 注入会被拒绝。

这三类证据一起才可写：

```text
EARLY_REGIME_I_SPLIT_DATA_AND_FROZEN_A_PATH_LEAKAGE_FIREWALL_PASS
```

不得写“full method leakage PASS”、不得证明未来 full-admission 新数据本身正确、不得证明
schema/candidate/reference/reliability/calibration/test-time 路径安全，也不得升级任何论文
效果 claim。后者仍由 `S0_METHOD_LEAKAGE_AUDIT` 和后续 Gates 决定。

### 23.3 production audit 的绝对 read boundary

新增 `scripts/audit_a_path_leakage.py`。production CLI **只能**接受可选
`--output-root`；不得接受 dataset root、source path、role、subject、slot、field、seed、device、
threshold、hash override 或 `--enforce=false`。函数 API 固定：

```python
audit_a_path_leakage(
    project_root: Path,
    output_root: Path,
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]
```

tests 可向 repository-external temporary project root 注入 synthetic source/metadata，并仅在
函数层使用 `enforce_frozen_expectations=False`；production CLI 不暴露该开关。审计脚本只可
使用 stdlib 与已锁定的 YAML parser，不能 import `h5py`、NumPy、Torch、A model 或
`validate_a1_frontend`。输入必须来自脚本内 exact relative-path allowlist；拒绝 symlink、
absolute path、`..`、missing、unexpected type 与 hash drift。任何 allowlisted input suffix
为 `.mat/.h5/.hdf5` 都应自我拒绝。production 期间任何 HDF5 open count 必须为零。

脚本不得 `subprocess` 执行 validator/tests，也不得访问 production dataset root。synthetic
HDF5 tests 由 test runner 独立执行；它们不属于 production audit 的数据读取。

### 23.4 exact audited components 与 machine assertions

AST audit 的 runtime components 精确为：

```text
scripts/validate_a1_frontend.py
src/rc_hsg/backbones/native_spectral_a1.py
```

metadata provenance components 精确为：

```text
scripts/build_a_interface_contract.py
scripts/build_joint_split.py
```

后两者可以合法处理 cal/test **metadata**，不能被错误解释为 cal/test value read。审计必须
按函数作用域和 source category 区分 metadata construction 与 real-array dereference。

`assertions` 至少包含以下 12 个稳定 ID；任一非 PASS 都原子失败：

| assertion ID | 必须机械验证的内容 |
|---|---|
| `SPLIT_ROLE_FIREWALL` | `split_regimeI` role 只能为 train_fit/inner_val/cal/test；真实读取 allowlist 精确为 `{train_fit,inner_val}`；cal/test 不进入 real panel |
| `ROW_KEY_FIREWALL` | analysis、eligibility、panel 的唯一 join key 精确为 `(subject,slot,occurrence_id)`；无 duplicate/missing；151-row panel 与 frozen selector/hash 一致 |
| `SHORT_BYPASS_FIREWALL` | 44 short 全部为 `A_INTERFACE_SHORT_SEGMENT`、`FORCED_L0_NO_FRONTEND`、window 0、`source_dataset_read=false`；不得进入 `_read_raw` |
| `DEREFERENCE_SCOPE_FIREWALL` | 只有 panel 中 107 个 `source_dataset_read=true` key 可组成 `allowed_keys`；guard 同时要求 membership、read flag 与 outer role；恰好一次读取并以 set equality 收口 |
| `SOURCE_IDENTITY_FIREWALL` | production root 是常量且 CLI 无 dataset override；root/file symlink、path escape、unexpected file、size drift、external/soft link 均拒绝 |
| `SOURCE_FIELD_SLOT_FIREWALL` | HDF5 只以 read-only 打开；路径精确 `sentenceData/rawData[slot-1,0]`；只接受 same-file hard-link/reference、exact selected slot、floating `[raw_samples,105]` |
| `NUMERIC_TRANSFORM_FIREWALL` | source/float32 cast 前后 finite；唯一转换为 no-scale contiguous float32 + explicit transpose；无 unit guess、scale、rereference、resample、interpolation |
| `PER_ROW_PREPROCESSING_FIREWALL` | A normalization 只在 `trial[:, :valid_length]` 内，以单 row/单 channel 的 median、MAD、RMS 完成；forward 逐 row tokenize；无跨-row/dataset statistics、fit 或 partial_fit |
| `INFERENCE_ONLY_FIREWALL` | model `.eval()` + `torch.inference_mode()`；无 optimizer、loss、backward、parameter update、`.train()` 或 checkpoint load |
| `NO_VALUE_TEXT_OUTCOME_CACHE` | runtime 不访问 content/word/labels/outcomes/predictions/results；不写 EEG/token/embedding/value/hash；无 `torch.save`、`numpy.save*`、pickle/joblib/parquet/HDF5 write 或 feature cache；仅合同 YAML/JSONL/MD 原子输出可写 |
| `FAIL_CLOSED_AND_DETERMINISTIC` | stable error prefixes、safe input/output path、temporary + fsync + replace、no partial PASS；two repo-external builds 与 canonical build byte-identical |
| `TEST_AND_DOWNSTREAM_LOCK` | route.locked 为 null，test 为 `LOCKED_UNTIL_ROUTE_LOCK`；full admission/method audit/Gates false；remaining unread=3,390；下一任务只为 `S0_A1_ADMISSION` |

AST extractor 必须检查明确的 imports、assignment literals、function definitions、calls、
attributes、subscripts、comparison guards 和 write targets。不得把 comment/docstring 当代码
证据；不得只因 source hash 匹配就跳过 semantic assertions。反之，hash drift 在 production
先报 input mismatch，不得用 AST PASS 接受未审版本。

### 23.5 frozen in-memory mutation probes

production audit 自身必须在内存中对 source text 作以下定点 mutation；每次 replacement 必须
恰好命中预期次数，且 mutated AST 必须被对应 assertion 拒绝。不得把 mutated file 写入仓库
或运行它。`mutation_tests` 至少记录以下稳定 ID 与 `status: PASS_REJECTED`：

| mutation ID | 注入的违规 |
|---|---|
| `M01_ROLE_BROADEN_CAL` | 把 real `OUTER_ROLES` 加入 `cal` |
| `M02_REMOVE_READ_FLAG_GUARD` | 从 `_read_raw` 删除 `source_dataset_read` guard |
| `M03_REMOVE_ALLOWED_KEY_GUARD` | 删除 selected-key membership guard |
| `M04_HDF5_WRITE_MODE` | 把 HDF5 mode 从 `r` 改为 `r+` |
| `M05_FORBIDDEN_SOURCE_FIELD` | 把 `rawData` 换成 `content` |
| `M06_WRONG_SLOT` | 把 `[slot-1,0]` 改为固定/其他 slot |
| `M07_REMOVE_VALID_SLICE` | 把 `trial[:, :valid_length]` 改为整段 trial |
| `M08_CROSS_ROW_FIT` | 注入 batch/dataset mean、`fit` 或 `partial_fit` |
| `M09_TRAINING_OR_BACKWARD` | 注入 `.train()`、optimizer 或 `.backward()` |
| `M10_OUTPUT_CACHE_WRITE` | 注入 `torch.save`/`numpy.save`/pickle/joblib/cache write |
| `M11_DATASET_CLI_OVERRIDE` | 注入 `--dataset-root` production CLI 参数 |
| `M12_SHORT_DEREFERENCE` | 把 short ledger 的 `source_dataset_read` 改为 true |

新增 tests 还必须覆盖：AST 不读取 comment/docstring 假阳性、malformed Python、missing
function、duplicate key、role/count/hash drift、panel tamper、test unlock、symlink/path escape、
unknown CLI arg、atomic failure、two-build determinism、no `.mat` open/import/subprocess 与全部
12 个 mutation probes。测试 fixture 使用临时 synthetic metadata/source；现有
`tests/test_validate_a1_frontend.py` 继续负责 synthetic HDF5 的 exact-slot/no-read/fail-closed
证据。不得在 tests 中调用 production dataset root。

### 23.6 implementation、错误与产物合同

新增：

```text
scripts/audit_a_path_leakage.py
tests/test_audit_a_path_leakage.py
artifacts/a_path_leakage_assertions.yaml
reports/a_path_leakage_audit.md
runs/2026-08-24_015_a_path_leakage_audit.md
```

异常类固定为 `APathLeakageAuditError(RuntimeError)`；稳定错误前缀至少为：

```text
A_PATH_AUDIT_INPUT_MISMATCH
A_PATH_AUDIT_ASSERTION_FAILED
A_PATH_AUDIT_MUTATION_NOT_REJECTED
A_PATH_AUDIT_OUTPUT_FAILURE
```

任何错误不得覆盖已有 canonical PASS outputs；若 output root 内已有目标，必须在全部输入、
assertion、mutation 与 serialization 完成后再原子替换。production outputs 不含时间、绝对
路径、host/device、EEG/value/tensor/embedding/hash、outcome/prediction/metric 或性能。

`artifacts/a_path_leakage_assertions.yaml` 顶层 canonical key order 精确为：

```text
schema_version, artifact, spec_version, baseline_commit, task,
evidence_scope, input_artifacts, audited_components, frozen_scope,
assertions, mutation_tests, prohibited, safety, downstream_boundary
```

header 精确为：

```text
schema_version: 1
artifact: RC_HSG_A_PATH_LEAKAGE_ASSERTIONS_V1
spec_version: v2.4
baseline_commit: dc105709563cf9eb216f1c28f82fdf754e7b0683
task: S0_LEAKAGE_AUDIT
evidence_scope: STATIC_CODE_COMMITTED_METADATA_AND_SYNTHETIC_FIXTURE_A_PATH_LEAKAGE_AUDIT_NO_NEW_REAL_EEG_VALUES_NO_OUTCOMES
```

`input_artifacts` 对 §23.1 全部 fixed inputs 记录 path/hash，并记录 active v2.4 spec 与 audit
code 的实际 hash。`audited_components` 区分 `runtime_value_path` 与
`metadata_provenance_path`。`frozen_scope` 明写 roles、151/107/44、18 subjects、1,452
panel windows、3,390 remaining unread、source field、key、test lock 和 no-HDF5-open。
`assertions` 依 §23.4 的固定顺序，每项只有 `id,status,evidence`，status 必须全为 PASS；
`mutation_tests` 依 §23.5 固定顺序。`safety` 至少写：

```text
production_hdf5_opened: false
new_real_eeg_values_read: false
real_frontend_validator_executed: false
text_or_outcome_read: false
training_or_parameter_update: false
test_status: LOCKED_UNTIL_ROUTE_LOCK
```

`downstream_boundary` 精确声明：

```text
full_outer_train_admission_completed: false
remaining_eligible_rows_not_read: 3390
method_leakage_audit_completed: false
full_method_leakage_pass_claimed: false
next_task: S0_A1_ADMISSION
```

report 必须逐 assertion 给出人可读 evidence 和 epistemic limits；不得仅把 YAML 复制成
PASS 清单。两次 repository-external production builds 必须 byte-identical，再生成 canonical
outputs；三者 hashes 一致。

### 23.7 acceptance 与验证矩阵

run 015 只有同时满足以下条件才可完成：

1. baseline/status/count/test-lock 与 §23.1 一致，package manifest 全通过；
2. production audit 没有 import/execute validator/model、没有 HDF5 open、没有新真实值读取；
3. exact fixed hashes/counts/keys/roles/panel/freezes 一致；
4. 12 assertions 全 PASS，12 mutations 全 `PASS_REJECTED`；
5. new audit tests、frontend synthetic HDF5、native A、A-interface builder、joint split 与全仓
   test discovery 全 PASS/no skip；
6. validator、status、task counts、only-ready、test lock、three-build determinism、
   `git diff --check` 与 clean post-commit/push verification PASS；
7. run record 区分服务器实际结果、committed prior evidence 与任何未执行检查。

fixed hash/state mismatch 报 `STATE_SPEC_CONFLICT`；audit source/metadata/assertion/mutation/output
失败报 `A_PATH_LEAKAGE_AUDIT_BLOCKED`。不得通过修改 expected hash、放宽 role、删 mutation、
读取真实数据或把后期要求移入 early PASS 来修复。

### 23.8 task graph 与 run-015 状态迁移

唯一执行链：

```text
SPEC_V24_REVIEW
-> S0_LEAKAGE_AUDIT
-> S0_A1_ADMISSION READY
-> stop
```

新增并完成 `SPEC_V24_REVIEW`；其 prerequisites 精确 `[SPEC_V23_REVIEW]`，产物为 active
v2.4 SPEC 与 `artifacts/spec_review/rc_hsg_v24_a_path_leakage_review.md`。完成
`S0_LEAKAGE_AUDIT`，evidence scope 使用 §23.6 精确字符串；acceptance evidence 包含 script、
tests、YAML、report 与 run 015。`S0_A1_ADMISSION` 在三个 prerequisites 全 DONE 后从 BLOCKED
迁为唯一 READY，owner=`CODEX`，`why_ready` 明确 early firewall PASS 后才允许 separate full
streaming admission。不得在 run 015 实现或执行 admission。

成功态恰为 **71 tasks、35 DONE、8 SKIPPED、27 BLOCKED、唯一 READY
`S0_A1_ADMISSION`**。B_V9 保持 active：它不阻塞其 resolver `S0_A1_ADMISSION`，但继续阻塞
N1/N2/Gate R0/reference/features/models。其他 blocker、route、Gate 与 test lock 不变。

PROJECT_STATE：

```text
project.spec_version       v2.4
project.spec_path          guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md
project.baseline_commit    dc105709563cf9eb216f1c28f82fdf754e7b0683
project.reviewed_commit    dc105709563cf9eb216f1c28f82fdf754e7b0683
project.repository_status  RC_HSG_V24_A_PATH_LEAKAGE_PASSED_FULL_ADMISSION_PENDING
last_completed_task        S0_LEAKAGE_AUDIT
recommended_next_task      S0_A1_ADMISSION
last_run                   runs/2026-08-24_015_a_path_leakage_audit.md
execution.stage/status     stage_0/READY
```

同步 AGENTS、AI_START_HERE、HANDOFF、root `CODEX_NEXT_TASK.md`、implementation matrix、
validator/status/tests。旧 SPEC/review/run、run-014 source 与 outputs byte-immutable。root next
task 必须改成 post-run stop state，明确下一轮仍需 ChatGPT 冻结 full-admission exact contract，
不能把当前 v2.4 package 内的执行指令重复当作 admission 授权。

### 23.9 对论文前进方向的更新

论文主线继续是 RC-HSG 的“reference-calibrated reliability alignment”，不回退到旧 NC-HSG
evidence-increment 叙事。当前最近关键路径为：

```text
A-path leakage firewall
-> full outer-train A1 admission
-> N1 block feasibility + N2 common-phase implementation
-> Gate R0 reference admissibility
-> typed semantic schema / shared candidates / reference features
-> reliability models + calibration contract
-> RC-HSG/Flat-RC/absolute/PMI controls
-> method leakage audit + pre-test route lock
-> confirmatory Gates and main experiment
```

run 015 的科学价值不是产生结果，而是建立第一道可审计防火墙：以后的 full admission 与
null/reference work 只能调用已证明 role/key/source/valid-slice/inference/cache 封闭的 A path。
下一次 ChatGPT 研究必须先冻结 `S0_A1_ADMISSION` 的 streaming 顺序、全量 counts、memory/
CUDA sampling、failure ledger、确定性产物与 B_V9 closure，Codex 不得自行设计。

### 23.10 run-015 硬停止线

禁止打开 production `.mat`/HDF5、重跑 real validator、读取 107 panel 或剩余 3,390 rows、
short/cal/test EEG、stimulus text、semantic/calibration/test outcome、prediction、metric 或历史
model result。禁止训练/backward/optimizer、写 checkpoint/embedding/token/value cache、修改 A、
split、eligibility、panel、run-014 outputs、短片段路由、unit/channel/window/tolerance；禁止执行
full admission、method leakage、N1/N2/F/schema/candidates/reference/reliability/calibration/
baseline/Gate 或解锁 test。

Codex 只实现 §23 已冻结的 audit harness、machine evidence、tests、状态迁移与 run record；
成功后在唯一 READY `S0_A1_ADMISSION` 处停止并 push。任何必须改变研究方案、输入边界、
assertion 定义、mutation 集或下一任务的情况，停止回传 ChatGPT/author，不得自主裁决。

---

## 24. v2.5：single-pass full outer-train A1 admission 与 run 016 合同

### 24.1 run-015 验收、当前仓库事实与固定输入

独立复核基线为 clean `main@07c37b3bb77c3cf396116078b64687dcebb9ee03`，其中
`6c8b21f77cdf9aafa602eafd5e4fa666eb595341` 完成 run 015，随后 `07c37b3...` 只恢复
`scripts/audit_a_path_leakage.py` 与 `scripts/check_project_state.py` 的 executable mode，未改
内容。`HEAD=origin/main`、porcelain 为空。validator/status PASS，恢复状态恰为 **71 tasks、
35 DONE、8 SKIPPED、27 BLOCKED、唯一 READY `S0_A1_ADMISSION`**，owner=`CODEX`；route
未锁，test 仍为 `LOCKED_UNTIL_ROUTE_LOCK`。

run 015 的两项 canonical outputs 在独立 repository-external rebuild 中 byte-identical；本地
可用的 audit tests 20/20、project-memory tests 52/52 PASS。服务器 run record 报告 full
discovery 182/182 no skip。独立 review 环境无 `pytest`/完整 PyTorch-h5py server stack，故
不把未复跑的 frontend suite 冒充本地结果。

run-016 fixed inputs：

| 文件 | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md` | `5878fa84db5abb380c71e6257a4a7c30e0587ab8d505ba0d9446c110d47426b5` |
| `artifacts/backbone_a_policy.yaml` | `034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425` |
| `artifacts/backbone_a_contract.yaml` | `4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac` |
| `artifacts/a_interface_eligibility_v1.jsonl` | `8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad` |
| `src/rc_hsg/backbones/native_spectral_a1.py` | `71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/data_card.yaml` | `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84` |
| `artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml` | `50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf` |
| `artifacts/admission/zuco2_osf_file_metadata.yaml` | `85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721` |
| `requirements-trust-align.lock.txt` | `72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910` |
| `scripts/validate_a1_frontend.py` | `ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd` |
| `artifacts/a1_frontend_audit_panel_v1.jsonl` | `95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed` |
| `artifacts/a1_frontend_freeze.yaml` | `817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66` |
| `reports/a1_frontend_selfcheck.md` | `703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503` |
| `scripts/audit_a_path_leakage.py` | `797618af0113a2f8f357ea8c91f53de7b9375afcbb3860baf437ebc1bfbe5e24` |
| `artifacts/a_path_leakage_assertions.yaml` | `eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70` |
| `reports/a_path_leakage_audit.md` | `491986e4caed53623069b26918b9be232aff74416c8e4ef973955a6810b7fd27` |
| `runs/2026-08-24_015_a_path_leakage_audit.md` | `52ff87aad5c260d6bb3ef34367839cbb6f1251ff6f4f1282075db9d4af1b22f6` |

active v2.5 SPEC 与新 admission code 的实际 hash 也必须写入 output。任何 fixed hash drift
先报 `STATE_SPEC_CONFLICT`；不得修改 expected hash 迎合仓库。

### 24.2 full admission 的科学边界与 evidence reuse

Regime-I outer-train 仍精确指 `role in {train_fit,inner_val}`。它含 3,541 rows：3,497
eligible、44 short，累计 35,745 full windows。run 014 已对 107 个 frozen panel eligible
rows 做完整 loader/CPU/batch/padding/CUDA frontend 检查；重复读取它们不会增加总体覆盖，
只增加真实值接触。因此 run 016 必须：

1. 复用 run-014 panel 的 107-row/1,452-window PASS，不 dereference 它们；
2. 单次流式读取 `eligible_outer_train_keys - run014_panel_keys` 的 **3,390 distinct rows**；
3. 对这 3,390 rows 全部执行 frozen A1 frontend inference，而不只是 loader shape scan；
4. 保留全部 44 short rows 为 forced L0，source dereference 与 frontend 均为零；
5. 形成全部 3,541 outer-train rows 的 canonical admission ledger。

确切分解：

| scope | rows | full windows |
|---|---:|---:|
| train-fit eligible cumulative | 2,797 | 29,263 |
| inner-val eligible cumulative | 700 | 6,482 |
| run-014 panel reused | 107 | 1,452 |
| run-016 remaining read | 3,390 | 34,293 |
| run-016 train-fit read | 2,742 | 28,411 |
| run-016 inner-val read | 648 | 5,882 |
| short no-read | 44 | 0 |
| full outer-train ledger | 3,541 | 35,745 |

最短 eligible 为 513 samples，最大为 18,436；maximum windows=72；18 subjects 和 18
summary files 必须全覆盖。source dtype distribution 是本轮允许记录的 schema diagnostic，
但不预猜其值；只允许 float32/float64。

可写结论上限仅为：

```text
FULL_REGIME_I_OUTER_TRAIN_A1_FRONTEND_ADMISSION_PASS
```

这不是训练、表示质量、reference/null feasibility、semantic outcome、calibration、Gate、
test 或 full-method leakage 证据。release-native physical unit 仍是 unresolved；PASS 只表示
unit-insensitive frozen A contract 接受该输入，不得写成 microvolt/unit 已识别。

### 24.3 implementation 与 audited-loader reuse

新增 `scripts/admit_a1_outer_train.py`。它不得实现第二套 HDF5 loader，不得直接 import
`h5py`，也不得修改 `scripts/validate_a1_frontend.py` 或 A code。必须先验证 §24.1 hashes，
随后 lazy-import exact audited validator module，并只复用：

```text
_dataset_files
_read_raw
_strict_execution_kernels
select_audit_panel
_row_key
METADATA
AUDIT_SEED
PRODUCTION_DATASET_ROOT
NativeSpectralA1
```

不得调用 `validate_a1_frontend()`，不得重建/覆盖 run-014 artifacts。新 script 的 AST/self-test
必须证明：没有 direct HDF5 open、没有 alternate source reader、真实数组只经 exact-hash
`_read_raw` 返回，且 `_read_raw` 的 `allowed_keys` 精确等于 remaining 3,390 keys。

production CLI 只允许：

```text
--output-root
--verification-root-a
--verification-root-b
```

三个参数都是 output roots；production 时 verification A/B 必须提供且 repository-external。
不得接受 dataset root、role、subject、slot、seed、device、batch、dtype、threshold、source、
resume 或 expectation override。tests 可在函数层注入 isolated synthetic dataset root 并用
`enforce_frozen_expectations=False`；production CLI 不暴露这些能力。

函数 API 固定为：

```python
admit_a1_outer_train(
    project_root: Path,
    dataset_root: Path,
    canonical_output_root: Path,
    verification_output_roots: tuple[Path, Path],
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]
```

### 24.4 单次 scan、streaming order 与 memory/device contract

在首次真实 dereference 前，必须只用 metadata 完成：fixed hash、3,541/3,497/44/35,745、
panel 107/1,452、remaining 3,390/34,293、key uniqueness/disjoint/union、role/source-file scope、
output roots 与 device preflight。任何冲突在零新增真实读取时停止。

remaining rows 的 scan order 精确按：

```text
(window_count, raw_samples, subject, slot, occurrence_id)
```

以最大 4 rows 组 deterministic batches；相邻长度排序减少 padding。每个 source array 只经
`_read_raw` dereference 一次，加入 `dereferenced_keys`，batch 验证后立即释放。禁止 preload
全体、保存 raw/tensor/token/embedding 或 resume cache。

model 固定 `NativeSpectralA1(20260824).eval()`，在首次读取前只移动一次到 selected device。
device 也只选一次：CUDA available 则全部 3,390 rows 使用 `cuda:0`，否则全部使用 CPU；
不得 mid-run fallback 或混用 device。
CUDA unavailable 是 nonblocking CPU fallback；CUDA available 但初始化/inference 失败则
blocker，不得转 CPU 掩盖。run-014 的 20-row/199-window CPU/CUDA parity 直接复用，不在本轮
重读 panel 或另做 parity sample。TF32、native JIT、MHA fastpath、Flash/memory-efficient SDP
继续按 audited `_strict_execution_kernels` 关闭。

每 batch：CPU tensor zero-pad 到 batch max T，转 selected device；`valid_samples` 精确为
metadata T；在 `torch.inference_mode()` 执行一次。每 row 必须验证 expected window count、
mask true-prefix/false-tail、finite window embeddings、finite pooled embedding、pooled exact
masked mean。model 全程 eval、grad null、parameters before/after exact unchanged。无需重复
run-014 的 individual-repeat、NaN-tail 或 batch-vs-individual tests；那些是已复用的 bounded
behavior evidence，本轮目标是 complete population traversal。

planned production scan 恰为一次。任何 source/value/tensor/frontend failure 原子不写 PASS
outputs，不自动重读、改 batch/device/tolerance 或跳过 row；回传稳定 row key 与错误 code。

### 24.5 canonical 3,541-row ledger

新增 `artifacts/a1_outer_train_admission_v1.jsonl`，canonical order 精确
`(subject,slot,occurrence_id)`；每 row fields/order 精确为：

```text
subject, slot, occurrence_id, role, raw_samples, window_count,
a_interface_status, action, evidence_source, source_file, source_field,
source_dataset_read_run016, source_dataset_read_cumulative,
source_dtype, source_shape_status, input_finite_status,
frontend_status, observed_window_count, window_mask_status,
output_finite_status
```

三类 row 的字段合同：

1. 107 panel：`evidence_source=RUN014_BOUNDED_PANEL_REUSED`；本 run read=false、cumulative=true；
   dtype=`float64` 与全部 status=PASS 来自 exact run-014 hashes；不得重算。
2. 3,390 remaining：`evidence_source=RUN016_STREAMING_FRONTEND_PASS`；本 run/cumulative read
   均 true；dtype 记录 actual float32/float64；shape/input/frontend/mask/output status 均 PASS，
   observed windows 等于 metadata。
3. 44 short：`evidence_source=SHORT_FORCED_L0_NO_READ`；两个 read flag 均 false；
   `source_dtype=NOT_READ`、shape/input/mask/output=`NOT_APPLICABLE`、frontend=
   `NOT_APPLICABLE_FORCED_L0`、observed windows=0。

source file 只写 committed relative path，source field 只写 `rawData`。ledger 禁止绝对路径、
EEG/value/tensor/embedding/waveform hash、amplitude/power/frequency statistic、text、outcome、
prediction、metric、timing、memory 或 device name。

### 24.6 freeze artifact、report 与 evidence scope

新增：

```text
scripts/admit_a1_outer_train.py
tests/test_admit_a1_outer_train.py
artifacts/a1_outer_train_admission_v1.jsonl
artifacts/a1_outer_train_admission_freeze.yaml
reports/a1_admission.md
runs/2026-08-24_016_a1_full_outer_train_admission.md
```

freeze artifact 顶层 canonical key order 精确为：

```text
schema_version, artifact, spec_version, baseline_commit, task, policy_id,
evidence_scope, input_artifacts, population_contract, reuse_contract,
loader_contract, execution_contract, acceptance_counts, check_results,
implementation, prohibited, safety, blocker_resolution, downstream_boundary
```

header 精确：

```text
schema_version: 1
artifact: RC_HSG_A1_FULL_OUTER_TRAIN_ADMISSION_V1
spec_version: v2.5
baseline_commit: 07c37b3bb77c3cf396116078b64687dcebb9ee03
task: S0_A1_ADMISSION
policy_id: RC_HSG_NATIVE_SPECTRAL_A1_V1
evidence_scope: FULL_REGIME_I_OUTER_TRAIN_A1_FRONTEND_ADMISSION_REUSING_RUN014_PANEL_NO_OUTCOMES_NO_TRAINING
```

`input_artifacts` 记录 §24.1 fixed paths/hashes、active v2.5 spec 与 admission code actual hash。
`population_contract` 写 exact role/key/count/window/source scope；`reuse_contract` 写 panel
path/hash、107/1,452、`panel_reread=false`；`loader_contract` 写 exact audited validator hash、
same-file rawData/slot/shape/dtype/cast/transpose 与 no alternate loader；`execution_contract` 写
single-pass、order、batch≤4、device policy、eval/inference/no-cache 与 reused parity evidence。

`acceptance_counts` 至少包含 §24.2 全部 counts、18 subjects/files、actual run016 dtype counts；
`check_results` 至少包含 input/hash/key/scope/source/finite/frontend/mask/output/parameter/
triple-render 全 PASS。`safety` 必须明确：

```text
production_scan_attempts: 1
run014_panel_arrays_reread: 0
run016_remaining_distinct_arrays_read: 3390
short_arrays_read: 0
calibration_arrays_read: 0
test_arrays_read: 0
text_or_outcome_read: false
training_or_parameter_update: false
representation_or_value_cache_written: false
test_status: LOCKED_UNTIL_ROUTE_LOCK
```

`blocker_resolution` 写 B_V9 closed by this task，但保留“不含 cal/test、无 unit inference、无
performance evidence”的 limitation。`downstream_boundary` 精确声明 full outer-train admission
完成、N1/N2 未实现、method audit 未完成、route unlocked、next task
`S0_N1_BLOCK_FEASIBILITY`。

report 逐项解释 cumulative vs run016 read、all-row frontend evidence、unit limitation、未完成
边界；不得把 PASS 写成 representation quality 或 downstream method evidence。

### 24.7 one-scan / three-render determinism 与 fail-closed

真实 EEG 只扫描一次。scan 完成后，完整 ledger/summary/report 必须先全部在内存构造与
serialize；同一 bytes 分别原子写入 verification root A、verification root B、canonical root，
三份逐文件 byte-identical。不得为了 determinism 再执行第二/第三次 real scan。

每个 root 都拒绝 symlink、path escape、目标冲突；same-directory temp、flush、fsync、replace。
先完成两份 repository-external writes/check，再替换 canonical。任何失败不留下 partial
canonical PASS。稳定异常类 `A1AdmissionError(RuntimeError)`；错误前缀至少：

```text
A1_ADMISSION_INPUT_MISMATCH
A1_ADMISSION_SCOPE_MISMATCH
A1_ADMISSION_SOURCE_BLOCKED
A1_ADMISSION_TENSOR_BLOCKED
A1_ADMISSION_FRONTEND_BLOCKED
A1_ADMISSION_OUTPUT_FAILURE
```

run-level failure 报 `A1_FULL_ADMISSION_BLOCKED`。错误 detail 只允许 stable row key/check/dtype/
shape code，不含 raw value、绝对 dataset path 或 tensor dump。

### 24.8 tests 与 acceptance matrix

新增 tests 必须只用 repository-external synthetic HDF5，至少覆盖：fixed input/hash、full
population split、panel reuse/no-reread、remaining exact-once、short/cal/test no-read、key
duplicate/missing/overlap、scan order、batch≤4、dtype/shape/nonfinite/cast/transpose、full
frontend windows/mask/finite/pool、parameter immutability、CUDA-if-available/CPU fallback、no
mid-run fallback、audited-loader-only AST、no direct h5py/alternate reader、no value/text/cache
emission、single-scan triple-render byte identity、atomic failure、symlink/path escape、unknown CLI
arg 与 tamper。

run 016 acceptance 必须同时满足：

1. baseline/package/fixed hashes/current state 全精确；
2. metadata preflight 在 zero new reads 下复现 §24.2 exact counts；
3. planned scan attempt=1，恰读 remaining 3,390 distinct，panel/short/cal/test 本 run read=0；
4. cumulative 3,497 eligible frontend PASS，44 short retained forced L0，3,541-row ledger 完整；
5. source identity/dtype/shape/finite、windows/masks/output/pooled/parameters 全 PASS；
6. three-render byte identity、canonical hashes、no value/outcome/cache emission PASS；
7. new suite、frontend/native/A-interface/audit/joint-split/project-memory 与 full server discovery
   全 PASS/no skip；
8. validator/status/task counts/only-ready/test lock/`git diff --check`/post-push clean remote PASS。

记录实际测试数量，不得预填或沿用 182。fixed conflict 用 `STATE_SPEC_CONFLICT`；source/value/
frontend/determinism failure 用 `A1_FULL_ADMISSION_BLOCKED`。禁止改 A、input、expected counts、
batch/device policy、skip row 或 guessed conversion 使其通过。

### 24.9 task/blocker/state migration

唯一执行链：

```text
SPEC_V25_REVIEW
-> S0_A1_ADMISSION
-> S0_N1_BLOCK_FEASIBILITY READY (owner=CHATGPT_OR_AUTHOR)
-> stop
```

新增并完成 `SPEC_V25_REVIEW`，prerequisites 精确 `[SPEC_V24_REVIEW]`，produces active v2.5
SPEC 与 `artifacts/spec_review/rc_hsg_v25_a1_admission_review.md`。`S0_A1_ADMISSION.produces`
更新为 §24.6 三个 canonical evidence outputs；成功后 DONE，acceptance evidence 含 script、
tests、ledger、freeze、report、run 016，evidence scope 使用 §24.6 精确字符串。

B_V9 从 active 移入 superseded blockers，closed_by=`S0_A1_ADMISSION`；retained limitation 明确
仅 outer-train、short forced-L0、physical unit unresolved、cal/test 未读、无 performance。
B_V4 保持 active，但从其 `blocks` 移除 resolver `S0_N1_BLOCK_FEASIBILITY`；N1/N2/Gate R0
仍未完成。`S0_N1_BLOCK_FEASIBILITY` 从 BLOCKED 迁为唯一 READY，owner=
`CHATGPT_OR_AUTHOR`，移除 blocked_reason，why_ready 明确 full admission 已通过但 length/power
bin、permutation feasibility/tolerance 仍须下一版 author-frozen contract；不得在 run 016
计算 power bins 或执行 task。

成功态恰为 **72 tasks、37 DONE、8 SKIPPED、26 BLOCKED、唯一 READY
`S0_N1_BLOCK_FEASIBILITY`**。其他 blockers/tasks/Gates 不变，test 继续 locked。

PROJECT_STATE：

```text
project.spec_version       v2.5
project.spec_path          guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md
project.baseline_commit    07c37b3bb77c3cf396116078b64687dcebb9ee03
project.reviewed_commit    07c37b3bb77c3cf396116078b64687dcebb9ee03
project.repository_status  RC_HSG_V25_A1_FULL_OUTER_TRAIN_ADMITTED_N1_FEASIBILITY_PENDING
last_completed_task        S0_A1_ADMISSION
recommended_next_task      S0_N1_BLOCK_FEASIBILITY
last_run                   runs/2026-08-24_016_a1_full_outer_train_admission.md
execution.stage/status     stage_0/READY
```

同步 AGENTS、AI_START_HERE、HANDOFF、root `CODEX_NEXT_TASK.md`、implementation matrix、
repository/environment snapshots、validator/status/tests。旧 SPEC/review/run、A code、validator、
run-014/run-015 source 与 outputs byte-immutable。root next task 必须是 post-run STOP，等待
ChatGPT/author 冻结 N1 feasibility contract。

### 24.10 对论文前进方向的更新

若 run 016 PASS，数据/A path 的 stage-0 基础链条完成：analysis view → split → clean-room A
interface → bounded real behavior → early leakage firewall → full outer-train admission。此时论文
仍没有效果结果，但可以合法进入 reference validity 的第一步：**先做 outcome-blind N1 block
feasibility，再实现 N1/N2，最后 Gate R0**。不能跳过 N1 feasibility 直接生成 permutations，
也不能提前做 semantic/reliability/calibration 结果。

下一轮 ChatGPT 研究必须冻结：只用 outer-train EEG-observable length 与 train-frozen power
信息的 block definition、bin edges、singleton/coverage/fixed-point/unique-permutation 指标、
K=199 feasibility threshold、no adjacent borrowing 和失败路由。Codex 不得自行选择 bins 或
tolerance。

### 24.11 run-016 硬停止线

授权只限剩余 3,390 eligible outer-train `rawData` arrays 的 planned single pass。禁止重读
run-014 panel、dereference 44 short、任何 cal/test array、读取 stimulus text、semantic/
calibration/test outcome、prediction、metric 或 historical result；禁止 amplitude/power/
frequency summary、N1 binning、训练/backward/optimizer、checkpoint/embedding/token/value
cache、unit inference、rereference/resample/interpolation、修改 A/validator/audit/split/panel/
short route、执行 N1/N2/F/schema/candidates/reference/reliability/calibration/baseline/Gate 或
解锁 test。

Codex 只实现 §24 admission wrapper/evidence/tests/state/run record，成功后在 owner=
`CHATGPT_OR_AUTHOR` 的唯一 READY `S0_N1_BLOCK_FEASIBILITY` 处停止并 push。任何必须改变
scan/device/batch/reuse/ledger/state policy 的情况，停止回传 ChatGPT/author，不得自主裁决。
