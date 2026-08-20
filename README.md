# superskill —— 渐进式披露的 SKILL 组织器

> 把 WorkBuddy 里零散的小 SKILL，自动归并成"按领域划分的聚合大 SKILL"，每个大 SKILL 成为该领域的统一调度入口。全程遵循**渐进式披露（Progressive Disclosure）**：概览常驻，细节按需加载。

## 解决的问题

SKILL 一多就会乱：几十个零散技能堆在 `~/.workbuddy/skills/`，职责重叠、命名随意、触发条件互相打架。手动整理要逐篇读、逐目录搬，还容易搬错。

superskill 把"整理 SKILL"这件事本身做成了一个**可重复执行的确定性流程**：

```
扫描盘点 → 归类方案 → 用户确认 → 逐类聚合 → 校验收尾
```

## 核心能力

| 能力 | 说明 |
|---|---|
| 全量扫描盘点 | `scan_skills.py` 提取每个 SKILL 的名称、用途、触发条件、内置资源，生成人读清单 + 结构化 JSON |
| 智能归类 | 按能力领域/技术栈/职责生命周期分组，内置优先级裁定规则（更专业优先、纯工具降为子工具） |
| 用户确认闸门 | 任何移动/删除动作必须发生在用户确认之后；`--dry-run` 可先行预览迁移映射 |
| 一键聚合 | `aggregate_skill.py` 自动创建大 SKILL 骨架、移入成员、写清触发条件与调用优先级 |
| 可回滚 | 每次聚合生成 `manifest.json` 记录全部迁移映射，随时按它反移还原 |

## 设计原则

### 1. 渐进式披露（Progressive Disclosure）

三级加载，上下文只装该装的：

- **元数据**（name + description）—— 始终在上下文，约 100 词
- **SKILL.md 正文** —— 触发时才加载，只保留概览与索引（superskill 自身仅 180 词）
- **references/scripts** —— 按需加载，无限容量

### 2. 确定性流程固化进脚本

"必须靠 AI 判断"的部分（归类、优先级裁定）由 AI 做；"可以固化成代码"的部分（扫描、移动、生成文档、写 manifest）全部由 Python 脚本完成。AI 只当触发器与确认人，不手写搬运逻辑。

### 3. 安全优先

- 移动/删除前必须用户确认
- `--dry-run` 预览、`--no-move` 只建入口不物理收编
- 目标目录已存在同名成员时中止，防覆盖
- 每次操作留 manifest 可回滚

### 4. 与平台机制对齐（实测踩坑修正）

WorkBuddy 会**递归扫描** `~/.workbuddy/skills` 下所有 `SKILL.md` 识别技能。成员移入大 SKILL 后若仍叫 `SKILL.md`，会被误识别为独立技能、重复显示在已安装列表。聚合器因此会把成员指令文件改名为 `member.md`——成员只经大 SKILL 按需加载，不再独立出现。

## 使用流程

```bash
# 1. 扫描盘点（生成 catalog.md + manifest.json）
python scripts/scan_skills.py --dir ~/.workbuddy/skills \
  --json references/manifest.json --md references/catalog.md

# 2. 预览某类聚合方案（不落盘、不移动）
python scripts/aggregate_skill.py --category 视频制作 \
  --members a-skill b-skill c-skill \
  --description "视频/媒体制作类统一入口" --root ~/.workbuddy/skills --dry-run

# 3. 确认后正式聚合（创建大 SKILL + 移入成员 + 写路由）
python scripts/aggregate_skill.py --category 视频制作 \
  --members a-skill b-skill c-skill \
  --description "视频/媒体制作类统一入口" --root ~/.workbuddy/skills
```

## 目录结构

```
superskill/
├── SKILL.md                    # 概览 + 索引（常驻上下文，约 200 词）
├── README.md                   # 本文件：介绍与优势
├── references/                 # 按需加载的详细资料
│   ├── catalog.md              # 当前环境 SKILL 清单（扫描自动刷新）
│   ├── classification-guide.md # 分类准则、优先级裁定规则、推荐分组
│   └── workflow.md             # 阶段 0-5 完整执行手册
└── scripts/                    # 确定性脚本（不进上下文，直接执行）
    ├── scan_skills.py          # 扫描器：SKILL → 清单（MD/JSON）
    └── aggregate_skill.py      # 聚合器：创建大 SKILL + 移入成员 + 写路由
```

## 适用场景

- 你的 `~/.workbuddy/skills/` 已经攒了几十个零散技能，想分门别类
- 多个技能职责重叠（如多个视频/浏览器/文档类技能），想合并成统一入口
- 想让模型按"领域入口 → 成员路由"的方式加载技能，而不是几十个技能同时抢触发

## 与"手动整理"相比的优势

| 维度 | 手动整理 | superskill |
|---|---|---|
| 盘点 | 逐个目录打开读 | 一条命令全量提取，输出清单 |
| 归类 | 凭记忆和感觉 | 依据明确准则 + 内置优先级规则 |
| 迁移 | 手工拖拽，易错 | 脚本移动 + 自动改名 + 写 manifest |
| 触发路由 | 靠人写 | 自动从成员正文提取触发条件写入大 SKILL |
| 回滚 | 基本不可逆 | manifest.json 一键反移 |
| 重复性 | 每次重来 | 流程固化，可反复执行 |

## 许可

MIT License
