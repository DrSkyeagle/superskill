---
name: superskill
description: 渐进式披露的 SKILL 组织器。扫描并盘点当前环境全部 SKILL（名称/用途/核心能力/触发条件）→ 按能力领域归并同类小 SKILL → 经用户确认后为每类创建聚合大 SKILL（统一调度入口）：把原小 SKILL 移入其 references/members 保存，并在大 SKILL.md 内写清各成员的适用场景、触发条件与调用优先级。触发：整理/分类/归并 SKILL、把多个小 SKILL 合成一个、SKILL 太多想分门别类、创建聚合大 SKILL、superskill。默认排除系统内置（插件托管）SKILL，仅在用户要求时才纳入。
agent_created: true
---

# superskill —— 渐进式披露的 SKILL 组织器

## 用途
把当前环境中零散的小 SKILL 按能力领域归并成若干个「聚合大 SKILL」。每个大 SKILL 是该领域**统一调度入口**，原小 SKILL 移入其 `references/members/` 妥善保存（指令文件自动改名为 `member.md`），按需加载。本 SKILL 自身严格遵循渐进式披露：SKILL.md 仅保留概览与索引，全部执行细节在后置 references/scripts 里，用到才加载。

## 关键机制（避免踩坑）
- WorkBuddy **递归扫描** `~/.workbuddy/skills` 下所有 `SKILL.md` 识别技能——成员移入子目录后若仍叫 `SKILL.md`，会被误识别为独立技能重复显示在已安装列表。因此聚合器会把成员指令文件改名为 `member.md`，成员仅能经大 SKILL 按需加载（2026-08-20 实测确认）。

## 何时触发
- 用户要整理 / 分类 / 归并 SKILL
- SKILL 太多、重复或职责重叠，想合并成统一入口
- 明确点名「superskill」「聚合 SKILL」

## 执行总览（5 步）
1. **扫描盘点** — 跑 `scripts/scan_skills.py` 生成目录清单（catalog.md）。
2. **归类** — 依 `references/classification-guide.md` 分组，列出方案。
3. **确认** — 向用户提交分组，等确认（可增删改/保留独立项）。
4. **聚合** — 逐类跑 `scripts/aggregate_skill.py` 建大 SKILL 并移入原 SKILL。
5. **校验** — 核对成员完整、路由可触发，输出迁移清单。

> 任何会**移动/删除**原 SKILL 的动作，必须出现在用户确认之后；`--dry-run` 可先行预览。

## 分类索引 / 路由（用哪个文件）
| 你想做 | 读取 |
|---|---|
| 只盘点、看当前清单 | `scripts/scan_skills.py` + `references/catalog.md` |
| 看怎么分类、优先级规则 | `references/classification-guide.md` |
| 完整跑一次归并（逐步操作） | `references/workflow.md` |
| 已确认的分类方案（历史） | `references/plan-*.md`（执行时以最新一份为凭） |
| 批量建大 SKILL / 移入成员 | `scripts/aggregate_skill.py` |

## 目录结构
```
superskill/
├── SKILL.md                    # 本文件：概览 + 索引（常驻）
├── references/
│   ├── catalog.md              # 当前 SKILL 清单（扫描自动刷新）
│   ├── classification-guide.md # 分类准则与推荐分组
│   └── workflow.md             # 完整执行手册（按需加载）
└── scripts/
    ├── scan_skills.py          # 确定性扫描器
    └── aggregate_skill.py      # 确定性聚合器（创建大 SKILL + 移入成员）
```
