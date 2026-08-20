# 操作手册（workflow.md）

> superskill 的标准执行流程。SKILL.md 只给了概览与索引，本文件是逐步操作细节，仅在正式执行归并时读取。

## 阶段 0 — 前置
- 确认用户意图是「整理全部 SKILL」还是「只归并某一类」。前者走全流程，后者可直接跳到阶段 3（指定类目）。
- 记录扫描根目录（默认 `~/.workbuddy/skills`，可追加项目级目录）。

## 阶段 1 — 扫描盘点
```bash
PY=~/.workbuddy/binaries/python/versions/3.13.12/python.exe
SK=~/.workbuddy/skills/superskill
"$PY" "$SK/scripts/scan_skills.py" --dir ~/.workbuddy/skills \
  --json "$SK/references/manifest.json" \
  --md  "$SK/references/catalog.md"
```
- 输出：`catalog.md`（人读清单）+ `manifest.json`（结构化：name/description/trigger/bundled）。
- 核对要点：每个 SKILL 的**名称、用途、核心能力（snippet）、触发条件（trigger）**齐全；缺触发条件的补读该 SKILL.md。

## 阶段 2 — 归类 & 确认
- 对照 `references/classification-guide.md` 的分组方案与 manifest 逐条核对。
- 用 AskUserQuestion 向用户提交分组方案，**明确征求**：
  1. 类目划分是否合理；
  2. 哪些 SKILL 要保留独立（不归并）；
  3. 是否排除系统内置 SKILL。
- 用户确认/修改后，形成最终「类目 → 成员」映射表，再进入阶段 3。
- **把确认后的最终方案落盘**为 `references/plan-<YYYY-MM-DD>.md`（含类目/成员/独立保留项/执行命令模板），后续执行直接以该文件为凭据，避免反复确认。

## 阶段 3 — 逐类创建聚合大 SKILL
对每一类，运行（`--category` 为大 SKILL 名，`--members` 为该类成员）：
```bash
"$PY" "$SK/scripts/aggregate_skill.py" \
  --category 类目名 \
  --members 成员1 成员2 ... \
  --description "一句话：本类统一调度入口" \
  --root ~/.workbuddy/skills
```
脚本会自动：
- 建 `<root>/<类目>/`（SKILL.md + references/catalog.md + manifest.json）；
- 把原小 SKILL 目录**整体移入** `<类目>/references/members/<原名>/`；
- **把成员的 `SKILL.md` 改名为 `member.md`**——WorkBuddy 会递归扫描 `~/.workbuddy/skills` 下所有 `SKILL.md` 识别技能，保留原名会让成员被误识别为独立技能、重复出现在已安装列表（2026-08-20 实测确认）。改名后成员仅能经大 SKILL 的 `references/members/<名>/member.md` 按需加载；
- 在大 SKILL.md 内写入每个成员的**触发条件**与**优先级**索引（指令路径指向 member.md）。

> 建议**先 `--dry-run`** 逐个预览，确认无误再正式移动。
> 若要保留原 SKILL 顶层可达性，用 `--no-move`（此时大 SKILL 只做路由，不物理收编）。

## 阶段 4 — 校验
1. 每个新建大 SKILL：`references/members/` 下成员数 == 计划成员数。
2. 每个成员 `member.md` 可被大 SKILL 按 `references/members/<名>/member.md` 找到。
3. 抽查大 SKILL.md 的触发路由是否与实际描述一致。
4. **根目录 `find <root> -name SKILL.md` 应只剩大 SKILL + 独立 SKILL + superskill 自身**（无成员残留），否则成员仍会出现在 WorkBuddy 已安装列表。
5. 汇总一份迁移清单给用户（manifest.json 汇总），确认无误。

## 阶段 5 — 收尾
- 输出：迁移清单 + 各聚合 SKILL 路径。
- 提醒用户：原小 SKILL 已被物理移入大 SKILL；需要回滚时按 manifest.json 反移。
