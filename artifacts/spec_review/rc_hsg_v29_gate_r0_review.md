# RC-HSG v2.9 / Gate R0 研究审查与 prime 目标评估

日期：2026-08-24  
remote baseline：`main@4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`  
裁决：**接受 run-019 N2 sampler；下一 run 只执行 outcome-blind Gate R0；性能与机制结论仍未产生。**

## 1. 远程仓库验收

- run-019 implementation commit 为 `f8dce4168ac123c51b5cb1db474734f83bd60799`，其后 `4fa6fadc...` 只纠正 run record 的 repository-status 字符串。
- 当前 75 tasks / 43 DONE / 8 SKIPPED / 23 BLOCKED / 1 READY；sole READY=`GATE_R0`。
- 本地 validator/status/diff/clean remote PASS；服务器 run 记录 full discovery 268/268、0 skip。
- N2 synthetic 最大 PSD/covariance/mean/cross-spectrum relative error 约 `3.63e-9/2.54e-9/5.52e-9/4.46e-9`，显著低于 `1e-6`；199 replicates deterministic、unique、finite。
- run-019 没有真实 EEG/text/outcome/test read，因此 sampler 正确性接受，但 N2 尚未 real-admitted。
- 两个非科学 blocker：run file 被第二 commit 直接修订；builder source 有一个相同值的重复 dict key。v2.9 用 append-only correction artifact 记录前者；后者保持历史 hash 不改，禁止复制到新脚本。

## 2. Gate R0 研究裁决

Gate 只使用 outer-train：2,797 train-fit eligible rows 拟合审计模型，700 inner-val eligible rows做独立判定；44 short、所有 calibration/test、文本和 semantic outcome 零读。每个 3,497 eligible source array 只读取一次，同时生成 replicates 1/2/199。

审计分四层：

1. 全部 rows 的 finite/shape/mask/coverage 和 replicate replay；
2. replicate 1 全 population、replicates 2/199 的 216-cell stratified panel 数值保持；
3. 同一 A1 spectral-tokenizer 路径的 balanced real/N2 classifier；
4. subject/length/power nuisance transfer，以及 amplitude/endpoint artifact bounds。

classifier 只在 train-fit 拟合，inner-val subject-macro AUC 与 bootstrap upper 都必须 `<=0.65`。这比只看 synthetic PSD 更关键：full-trial Fourier spectrum 可以完全保持，但 A1 的 500-sample window tokens、幅值分布和端点仍可能暴露 surrogate。

N1 不重读 EEG：结构/机制状态 PASS，但因既定 coverage 仍永久不能成为 primary。N2 Gate PASS 才保留 RC-HSG；N2 FAIL/INCONCLUSIVE 时转 ordinary hierarchical selective generation。无论分支，下一任务都是 author-owned `S0_SEMANTIC_ITEM`，Codex 不得顺带建 schema。

## 3. prime 目标成功率判断

以下是基于当前 evidence、样本规模和冻结门槛的研究规划区间，不是可校准的统计概率：

| 目标 | 当前主观规划区间 | 判断 |
|---|---:|---|
| Gate R0 使 N2 real-admitted | 45%–65% | synthetic 很强，但 A1 window/amplitude/endpoint artifact 未知 |
| 严格 split 下 Gate R 性能提升 | 25%–45%（以 N2 PASS 为条件） | selective reliability 可能改善，但 18 subjects、低 SNR、无 pretrained A、门槛严格 |
| 发现可复现的算法机制（reference/hierarchy utility） | 20%–40% | 可通过 Gate R/H、PMI 与消融定位，但可能只是一般置信度校准 |
| Mechanism A 的 EEG semantic separation | 10%–25% | 非阻断；小样本、强语言先验与 confound 使 attribution 更难 |
| “性能提升 + 算法机制”同时成立 | 10%–25% | 不属于高成功率目标 |
| “性能提升 + 生物/神经机制”同时成立 | 5%–15% | 当前设计最多支持有限 attribution，不能支持因果神经机制 |
| 形成一篇边界清楚的正/负结果论文 | 60%–80% | 预注册失败路线和审计资产明显提高可发表完整性 |

为什么 strongest prime 不高：ZuCo 2.0 NR 只有 18 participants、349 sentences；本项目又采用 stimulus-group-disjoint、no teacher forcing、test lock、subject-macro 以及较强的 risk/anti-abstention threshold。近年来 EEG-to-text 工作也明确承认 low-SNR、small-scale 和语言模型 hallucination 问题；较新的严格 split 研究提供“可恢复粗粒度语义”的积极信号，但通常仍依赖 pretrained language representations，而本项目 primary A 是无预训练、从零训练的 controlled frontend。

因此论文 prime 应保持为：**在相同 unsupported-semantic risk 下，reference-calibrated hierarchy 是否提高 specificity**。算法机制由 Gate R/H/PMI/ablation 解释；Mechanism A 保持 secondary/non-blocking。不要把“生物机制发现”升级为必须共同成功的标题级目标，否则项目总体成功率会被最弱的一环主导。

## 4. 下一步边界

run-020 只决定 reference admissibility。即使 PASS，也仍不能声称性能提升或机制发现；接下来必须先冻结 typed semantic schema/evaluator/projection、candidate firewall，再做 reference features、reliability、calibration、route lock，最后才有 Gate R/H/Mechanism A 的结果。

科学依据包括 multivariate common-phase surrogate 的 cross-spectrum 保持（Prichard & Theiler）、Fourier endpoint artifact 风险（Schreiber & Schmitz）、ZuCo 2.0 的 18-participant/739-sentence resource（Hollenstein et al.），以及近期严格无同句 split 的 EEG-to-text 研究对 small-scale/hallucination 的直接讨论（GLIM）。
