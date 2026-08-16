# Codex Task — Bootstrap NC-HSG Project Memory and Audit `wip2`

目标：在 `https://github.com/cb6e310/wip2` 的**实际当前仓库**中，一次完成 `S0_GOVERNANCE_BOOTSTRAP` 与随后解锁的 `S0_REPOSITORY_AUDIT`。建立可验证的项目记忆系统，并从物理文件恢复保守状态。不要实现任何科学算法。

本指令已经替你完成研究决策。不要自行选择数据集、backbone、schema、null、校准器、阈值、Gate 或论文路线；缺事实就建 blocker。

## 0. 硬边界

允许：读取仓库源码、文档、依赖清单、测试、配置和 artifact 元数据；创建/更新治理文件、validator/status 工具、治理测试、只读 inventory、handoff 和 run record；运行不训练、不下载数据的单元/静态测试。

禁止：

- 不得把示例 ZIP 中的 EQ-ANMA 状态、提交号、hash、ZuCo 数字、DONE 或 blocker 导入本项目。
- 不得实现或修改 N1/N2、NC-HSG、EB-HSG、direct-C、PMI、schema/model/data pipeline。
- 不得训练、微调、下载数据或 checkpoint、生成 surrogate、跑 Gate、跑 main experiment。
- 不得打开或汇总 held-out/test metric 内容；若发现结果文件，只登记路径、大小、mtime 和 hash，并标记 `UNREAD_HELDOUT_ARTIFACT`。
- 不得猜单位、通道、采样率、license、split、checkpoint 或配置。
- 不得改 v1.2 的科学阈值、公式、Gate 或 failure route。

## 1. 仓库与导入前检查

1. 在现有 checkout 工作；若没有 checkout，clone `wip2` 后进入仓库根目录。
2. 先读取仓库内所有适用的 `AGENTS.md`，再执行：

   ```bash
   pwd
   git rev-parse --show-toplevel
   git branch --show-current
   git rev-parse HEAD
   git status --short
   git log -1 --oneline
   ```

3. 记录 branch、HEAD、dirty paths。不得清理、reset、checkout 或覆盖用户修改。若 dirty path 与本包要写的路径重叠，停止并报告 `BOOTSTRAP_PATH_CONFLICT`；不重叠则保留并继续。
4. 安全检查交付 ZIP：列出 entries；拒绝绝对路径、`..`、symlink、重复路径、大小写冲突、设备文件和 manifest 外文件。验证 `PACKAGE_MANIFEST.sha256` 中每个内部文件的 SHA256。
5. 只导入 manifest 列出的文件。active SPEC 必须落为 `guide/NC_HSG_Paper_Spec_v1_2_2026-08-16.md`。不要删除仓库原有文件；旧 SPEC 保留，但不得继续标 active。
6. 读取 `guide/CODEX_BUILD_PROJECT_MEMORY_SYSTEM.md`、active SPEC 的 §0.4、§2.2–2.5、§3.2、§4.2–4.3、§5、§7.3、§8、§12，以及根目录 `AI_START_HERE.md`。
7. 打印 `PROJECT SNAPSHOT`。此时预期只有 `SPEC_V12_REVIEW=DONE`、`S0_GOVERNANCE_BOOTSTRAP=READY`；若不同，先报 `STATE_SPEC_CONFLICT`。

## 2. 实现 persistent project context

创建或补齐：

```text
AI_START_HERE.md
PROJECT_STATE.yaml
TASKS.yaml
HANDOFF.md
runs/
artifacts/
scripts/check_project_state.py
scripts/project_status.py
```

复用仓库现有 Python/测试布局。YAML 解析优先使用仓库已有依赖；若没有 YAML 库，在现有依赖管理文件中加入 `PyYAML>=6,<7` 并按仓库既有方式更新 lockfile。不要自写不完整 YAML parser，不要新建数据库、Web 服务或 agent framework。

### 2.1 `check_project_state.py` 必须实现

输入默认为仓库根的 `PROJECT_STATE.yaml` 与 `TASKS.yaml`；成功 exit 0，任一错误 exit 非零并逐项打印稳定错误码。至少检查：

1. 状态只能是 `TODO READY IN_PROGRESS DONE BLOCKED FAILED SKIPPED TERMINATED`。
2. 每个 task 必须有 `title stage status prerequisites produces acceptance`；所有 prerequisite ID 存在；依赖图无环。
3. `READY` 的全部 prerequisite 为 `DONE`，且 active blocker 的 `blocks` 不含该 task。
4. `DONE` 的全部 prerequisite 为 `DONE`；每个 `produces` 路径真实存在；有非空 `completed_by_run`；对应 run record 存在。代码存在但未验证不能通过 DONE。
5. `BLOCKED` 有非空 `blocked_reason`，并至少满足“prerequisite 未 DONE”或“active blocker 明确 blocks 它”之一。
6. `recommended_next_task` 必须存在、状态为 `READY`、prerequisite 全 DONE、未被 blocker 阻断。
7. `project.spec_path`、`management_contract_path` 与 `last_run` 存在；active spec version/path 一致。
8. Gate/顺序硬约束：
   - `GATE_A1=DONE` 前 `S0_LEAKAGE_AUDIT/S0_N1_SAMPLER/S0_N2_SAMPLER` 全 DONE；
   - `S0_SEMANTIC_ITEM` 与任何 semantic probe 不得在 `GATE_A1=DONE` 前 DONE；
   - `GATE_A=DONE` 前 Stage 1、sham/schema/population 前置全 DONE；
   - `GATE_B=DONE` 前 NC-HSG、direct-C、PMI、unit-cost 前置全 DONE，且 Gate A DONE；
   - `ROUTE_LOCK=DONE` 前 Gate A/B 与 calibration contract 全 DONE；
   - `MAIN_EXPERIMENT=DONE` 前 route lock/leakage/unit-cost 全 DONE；
   - route locked 时只能有一个 route，不能同时锁 full/topic/flat/negative。
9. 如果 `gates.*.outcome` 非空，只允许 SPEC 定义的 `PASS FAIL DEGRADED TOPIC_ONLY`；Gate 任务 DONE 时 outcome 不得为空。
10. 禁止 active state 引用示例项目的 `EQ-ANMA`、`CSPE`、`711340d` 或 `STRUCTURAL_NO_GO_N50`；命中时报 `FOREIGN_PROJECT_STATE`。

### 2.2 `project_status.py` 必须实现

输出恰好包含：

```text
PROJECT SNAPSHOT

Spec:
Current stage:
Current route:
Last completed:
Active blockers:

Ready tasks:
1. ...

Recommended next task:
Why:

Blocked downstream:
Do not do yet:
```

候选 next task 只能来自 `READY + prerequisites DONE + no active blocker`。排序固定为 `critical_path=true` 优先、再按 numeric `priority`、再按 task ID；不得因为代码容易写而越过 critical path。若 state 中 recommendation 不是排序第一项，exit 非零并报 `RECOMMENDATION_MISMATCH`。

### 2.3 治理测试

按仓库现有测试框架新增 focused tests，至少覆盖：

- 当前 bootstrap state PASS；
- 非法 status FAIL；
- prerequisite 不存在与 cycle FAIL；
- DONE artifact 缺失、run 缺失、前置未 DONE 均 FAIL；
- READY 被 blocker 阻断 FAIL；
- BLOCKED 无理由 FAIL；
- recommendation 指向非 READY 或不是排序第一项 FAIL；
- Gate A1/A/B、route lock、main experiment 越序均 FAIL；
- 双 route lock FAIL；
- foreign example-project state FAIL；
- status 输出字段完整且排序确定。

测试用临时 fixture，不依赖 EEG、网络、GPU 或大 artifact。

## 3. 在同一 run 完成实际仓库只读审计

治理 focused tests 通过后，把 `S0_GOVERNANCE_BOOTSTRAP` 标为 DONE，补真实 `completed_by_run` 与 run path；这会解锁 `S0_REPOSITORY_AUDIT`。继续完成后者，不开始任何科学实现。

### 3.1 审计范围

使用 `rg --files` 和 Git 元数据盘点，排除 `.git`、虚拟环境、cache、下载目录和大型数据内容。读取 README、配置、依赖、源码入口、测试入口、现有治理/规格文件；对可能包含 held-out/test 结果的文件只看文件名与元数据，不打开内容。

生成：

1. `artifacts/governance/repository_inventory.yaml`
   - repository root、remote、branch、HEAD、dirty paths；
   - 顶层目录与各类文件计数；
   - dependency/test/build entry points；
   - data/checkpoint/result 路径只登记 presence、size、mtime、sha256 或 `HASH_SKIPPED_TOO_LARGE`；
   - 不记录 secret、token、credential 或环境变量值。
2. `artifacts/governance/environment_snapshot.yaml`
   - OS/Python/CUDA/GPU（若可查询）、关键包版本、可用测试命令；
   - 只记录变量名级别的配置需求，绝不转储环境值。
3. `artifacts/governance/spec_implementation_matrix.yaml`
   - 至少逐项覆盖 data loader/data card、stimulus identity、split、leakage、A/frontend、semantic schema/evaluator、candidate firewall、N1、N2、calibration、NC-HSG、EB-HSG、direct-C、PMI、tests、artifacts；
   - 每项 status 只能是 `ABSENT IMPLEMENTED_UNVALIDATED VALIDATED BLOCKED NOT_APPLICABLE`；
   - 记录 evidence paths、tests rerun、acceptance gaps、target task、blocker；
   - README 声称、文件名相似或函数存在不能单独得到 `VALIDATED`。

### 3.2 可执行验证

1. 先运行治理 focused tests。
2. 从仓库已有配置确定最小、无网络、无训练的现有 unit/smoke test 命令；运行能在当前环境安全执行的集合并记录精确 pass/fail/skip。不得为了让测试通过而改科学代码。
3. 若依赖缺失，只记录 blocker；除治理所需 PyYAML 外不要安装大型包或下载模型。
4. 运行：

   ```bash
   python scripts/check_project_state.py
   python scripts/project_status.py
   git diff --check
   ```

## 4. 保守更新状态

完成 inventory 后：

1. `S0_GOVERNANCE_BOOTSTRAP=DONE`，证据为两个脚本、focused tests 和本 run。
2. `S0_REPOSITORY_AUDIT=DONE`，证据为三份治理 artifact 与审计命令。
3. 移除 `B_REPOSITORY_NOT_AUDITED`，但只按物理证据更新 V1–V6 blocker。
4. 科学任务状态规则：
   - artifact 存在、全部 acceptance 可核、相关测试本轮通过，才可 `DONE`；
   - 代码存在但 acceptance/真实数据/test 未验证，设 `IN_PROGRESS`；
   - 没实现且 prerequisite 未满足，保持 `BLOCKED`；
   - 没实现但 prerequisite 全满足且无 blocker，设 `READY`；
   - 不能确认就 `TODO/BLOCKED`，绝不猜。
5. `recommended_next_task` 设为 validator 算出的唯一 critical-path 第一项。通常会是 `S0_DATA_CARD`，但若仓库证据改变前置状态，以 validator 和真实 blocker 为准，不得为了符合“通常”而伪造。
6. 覆盖 `HANDOFF.md`，新增唯一 `runs/YYYY-MM-DD_<id>.md`。run 必须记录 commit baseline、files changed、tests、artifacts、state transitions、new blockers、recommended task、held-out files未读声明。
7. 将 `S0_GOVERNANCE_BOOTSTRAP.produces` 中占位的 `runs/BOOTSTRAP_RUN_RECORD.md` 替换为实际 run path。

## 5. 最终验证、提交和报告

1. 再跑治理 focused tests、所有本轮安全运行的现有 tests、state validator、status、`git diff --check`。
2. 检查 diff：不得出现科学算法、数据、模型、Gate 结果或 held-out metric 内容变化。
3. commit message：`chore: bootstrap nc-hsg project context`。
4. push 当前分支；若认证/权限失败，保留本地 commit 并如实报告，不改写历史、不强推。

最终只报告：

```text
Baseline commit:
Final commit:
Branch / push status:
Current stage:
Tasks confirmed DONE:
Tasks IN_PROGRESS:
Active blockers:
Ready tasks:
Recommended next task:
Why:
Files changed:
Artifacts produced:
Tests run and exact results:
Validation result:
Held-out content read: NO
Scientific implementation changed: NO
```
