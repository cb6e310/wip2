# RC-HSG v2.8 / N2 common-phase sampler 研究审查

日期：2026-08-24  
审查基线：`main@06e3e5f9b5c720bbb29074ca1cae1109add5b1b9`  
裁决：**接受 run-018；冻结 synthetic-only N2 sampler；下一 run 不得执行 Gate R0。**

## 1. 当前仓库事实

- remote `HEAD=origin/main`，worktree clean；提交为 `Implement RC-HSG v2.7 N1 mechanism sampler`。
- `PROJECT STATE VALID`；74 tasks / 41 DONE / 8 SKIPPED / 24 BLOCKED / 1 READY。
- sole READY 为 `S0_N2_SAMPLER`，owner=`CHATGPT_OR_AUTHOR`；route 未锁，test 仍锁。
- validator、status、`git diff --check` PASS。
- 本地独立复现 N1 两个新 suite 合计 18/18、project-memory 61/61；服务器 run-018 记录 full discovery 239/239、0 skip。本地 full discovery 因当前审查环境缺 `torch/h5py` 出现 6 个 import errors，不把它冒充服务器 full-suite 复现。

## 2. run-018 接受结论

N1 module 从冻结 assignment 动态重建 199 个 replicate；不使用 RNG、Python `hash()`、frontend 或 dataset reader。manifest 恰 199 rows，未泄露 block、recipient 或 donor relation。N1 仍因 run-017 的 `DEGRADED_COVERAGE` 只能作为 mechanism/robustness reference，不能回升为 primary。

run-018 文本中 package-source `CODEX_NEXT_TASK.md` 的 SHA256 有一字符序列抄写错误：recorded 值为 `667b36d04a5e91fd314bf44b1e7ce0a145ed0e9a45286c36c56c8eb8c9d2b0e7`，而其绑定 ZIP `934d7bb625b6a5183d251ae0d7b5255053adaebef17a0883394a371f3f5b5c24` 内文件及 manifest 的实际值为 `667b8bc2af414673e09d9d2011446db502fbca305fb26e6c558bd0a762d51ef6`。这是 provenance typo，不影响 code、tests、outputs 或 state；run-019 只新增 correction artifact，不修改历史 run。

## 3. N2 科学裁决

primary N2 冻结为 multivariate common-phase Fourier surrogate：每个正频率对全部 105 channels 广播同一相位增量，DC 与偶数长度 Nyquist 固定。这样保持每通道 periodogram 以及通道间相位差/交叉谱；但其精确保持对象是 circular second-order structure，不能据此声称真实 EEG exchangeability、exact p-value 或 distribution-free guarantee。

端点不连续、amplitude distribution 和 real/reference 可分性仍可能产生伪迹。因此 run-019 只实现 sampler 和 deterministic synthetic contract；真实 outcome-blind admissibility 延后给下一版 `GATE_R0` 合同。AAFT/IAAFT 仅可在未来作为 sensitivity，逐通道独立相位禁止作为 primary。

依据：Prichard & Theiler, *Generating surrogate data for time series with several simultaneously measured variables*；Schreiber & Schmitz, *Surrogate time series*；Theiler et al., *Testing for nonlinearity in time series*。

## 4. run-019 冻结范围

- 输入：仅代码、SPEC、既有 metadata/governance artifacts 和解析生成的 synthetic fixtures。
- 真实数据读取：0；不得打开 outer-train/cal/test EEG，不得读取 text/outcome/test identity。
- 不加载 A1/frontend，不生成 embedding、reference score、p-value，不训练，不执行任何 Gate。
- 数值实现：CPU contiguous float32 input，NumPy float64 FFT internal，float32 output；只变换 valid unpadded prefix；padding tail 输出 exact zero。
- synthetic acceptance：PSD、covariance、mean、cross-spectrum 的稳定 global relative norm 均 `<=1e-6`；同时验证 even/odd、199 seeds、deterministic replay、batch/unpadded parity、mask/zero-tail 和禁止性 mutation。
- amplitude KS/quantile、endpoint jump/slip 与 waveform correlation 只记录 schema，不设 synthetic Gate cutoff。

## 5. 成功后的唯一状态

仅在全部测试与安全审计 PASS 后：新增 `SPEC_V28_REVIEW=DONE`，置 `S0_N2_SAMPLER=DONE`，把 `GATE_R0` 设为 sole READY；任务计数应为 75 / 43 DONE / 8 SKIPPED / 23 BLOCKED / 1 READY。B_V4 保持 active，route 仍未锁，test 仍锁，所有 Gate outcome 仍为 null。commit/push/复核 clean 后硬停止。

下一轮由 ChatGPT/author 冻结真实 outcome-blind Gate R0：合法读取范围、replicate budget、real/reference classifier、nuisance probes、PSD/cross-spectrum/covariance、amplitude/endpoint/mask/coverage thresholds 及失败路由。Gate R0 PASS 前，不得把 N2 写成已准入 primary。
