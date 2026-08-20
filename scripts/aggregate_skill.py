#!/usr/bin/env python3
"""
aggregate_skill.py — 按类别创建聚合大 SKILL，并把原小 SKILL 移入其 references/members 保存。

流程:
  1) 在 <root>/<category>/ 下建大 SKILL 目录
  2) 把 --members 所列小 SKILL 目录整体移入
     <category>/references/members/<原名>/ 妥善保存
  3) 依据各成员 frontmatter/正文自动生成大 SKILL.md（含每个成员的
     适用场景、触发触发、优先级）与 references/catalog.md
  4) 写 manifest.json 记录移动映射，便于回滚

关键行为:
  - 成员原 SKILL.md 在移入后自动改名为 member.md —— WorkBuddy 会递归扫描
    ~/.workbuddy/skills 下所有 SKILL.md 识别技能，保留原名会导致成员被误
    识别为独立技能（重复出现在已安装列表）。改名后成员仅能经大 SKILL 加载。

用法:
  python aggregate_skill.py --category 视频制作 \
      --members agent-video-forensics ai-lyric-mv-pipeline ... \
      --description "视频/媒体制作类统一入口" \
      [--root ~/.workbuddy/skills] [--no-move]

安全:
  - 默认执行"移动"；加 --no-move 仅生成大 SKILL 不挪动原目录
  - 移动前记录 manifest.json，可用 --dry-run 预览
  - 目标目录已存在同名成员时中止（防止覆盖）
"""
import argparse, json, re, shutil, sys, datetime
from pathlib import Path


def parse_fm(text: str) -> dict:
    fm = {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        if k:
            fm[k] = v.strip().strip('"').strip("'")
    return fm


def member_trigger(text: str) -> str:
    # 只抓「触发」标记所在的单行，避免跨行把 frontmatter/正文尾部杂质带进来
    m = re.search(r"(?:触发|适用场景|何时当|when to)[^\n]{0,150}", text, re.I)
    return re.sub(r"\s+", " ", m.group(0)).strip() if m else ""


def render_big_skill_md(category, description, members, members_ref_rel) -> str:
    L = []
    L.append("---")
    L.append(f"name: {category}")
    L.append(f"description: \"{description}。内部聚合以下小 SKILL：{', '.join(m['name'] for m in members)}。\"")
    L.append("agent_created: true")
    L.append("---")
    L.append("")
    L.append(f"# {category}（聚合大 SKILL）")
    L.append("")
    L.append(f"> 由 superskill 生成 · {datetime.datetime.now():%Y-%m-%d}")
    L.append("")
    L.append(f"本 SKILL 是「{category}」领域所有小 SKILL 的**统一调度入口**。按需从 references/members/ 加载具体小 SKILL 的完整指令。")
    L.append("")
    L.append("## 成员路由（触发条件 & 优先级）")
    L.append("")
    for i, m in enumerate(members, 1):
        L.append(f"### {i}. {m['name']}")
        L.append(f"- 触发: {m.get('trigger') or m.get('description') or '-'}")
        L.append(f"- 完整指令: `{members_ref_rel}/{m['name']}/member.md`")
        L.append("")
    L.append("## 调用关系与优先级")
    L.append("- 成员之间一般**互斥**（按触发条件命中其一）；命中多个时按排列顺序，先到先得。")
    L.append("- 若成员存在严格的先后依赖（如 A 产中间产物交给 B），已在各自 SKILL.md 内标明；本入口不代跑中间步骤，只负责路由到正确的成员。")
    L.append("- 需要调度决策（同一输入命中多个成员）时，按以下优先级: 更专业的成员 > 更通用成员；本类无法裁决时上报用户。")
    L.append("")
    L.append("## 管理")
    L.append("- 成员目录: `references/members/`（原小 SKILL 整体移入，勿拆散）")
    L.append("- 分类介绍与触发索引: `references/catalog.md`")
    L.append("- 迁移映射/回滚依据: `manifest.json`")
    return "\n".join(L)


def render_catalog_md(category, members) -> str:
    L = [f"# {category} · 成员明细", "", f"共 {len(members)} 个成员。", ""]
    for i, m in enumerate(members, 1):
        L.append(f"## {i}. {m['name']}")
        L.append(f"- 路径: `references/members/{m['name']}/`")
        L.append(f"- 用途: {m.get('description') or '-'}")
        L.append(f"- 触发: {m.get('trigger') or '-'}")
        L.append("")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True, help="大 SKILL 名称（目录名）")
    ap.add_argument("--members", nargs="+", required=True, help="要归并的小 SKILL 名")
    ap.add_argument("--description", default="统一调度入口")
    ap.add_argument("--root", default=str(Path.home() / ".workbuddy" / "skills"))
    ap.add_argument("--no-move", action="store_true", help="只建大 SKILL，不移动原目录")
    ap.add_argument("--dry-run", action="store_true", help="只预览不落盘")
    args = ap.parse_args()

    root = Path(args.root)
    cat_dir = root / args.category
    members_ref_dir = cat_dir / "references" / "members"
    members_ref_rel = "references/members"

    if cat_dir.exists():
        sys.exit(f"[错误] 目标大 SKILL 目录已存在: {cat_dir}")

    # 收集成员元数据
    members = []
    missing = []
    for name in args.members:
        src = root / name
        if not (src / "SKILL.md").exists():
            missing.append(name)
            continue
        text = (src / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        members.append({"name": name, "description": fm.get("description") or fm.get("summary") or "",
                        "trigger": member_trigger(text)})
    if missing:
        sys.exit(f"[错误] 以下小 SKILL 不存在: {missing}")

    big_md = render_big_skill_md(args.category, args.description, members, members_ref_rel)
    cat_md = render_catalog_md(args.category, members)

    # 迁移映射
    manifest = {
        "category": args.category,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "moves": [{"from": str(root / m["name"]), "to": str(members_ref_dir / m["name"]), "name": m["name"]}
                  for m in members],
    }

    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print("\n--- 生成的大 SKILL.md 预览 ---\n")
        print(big_md)
        return

    # 落盘
    members_ref_dir.mkdir(parents=True, exist_ok=True)
    (cat_dir / "SKILL.md").write_text(big_md, encoding="utf-8")
    (cat_dir / "references" / "catalog.md").write_text(cat_md, encoding="utf-8")
    (cat_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 大 SKILL 骨架已建: {cat_dir}")

    # 移动成员
    if args.no_move:
        print("[提示] --no-move，未移动原 SKILL。")
        return
    for m in manifest["moves"]:
        src = Path(m["from"]); dst = Path(m["to"])
        if dst.exists():
            sys.exit(f"[错误] 目标成员目录已存在，中止以防覆盖: {dst}")
        shutil.move(str(src), str(dst))
        # 关键：成员指令文件改名为 member.md —— WorkBuddy 递归扫描目录下所有
        # SKILL.md，若保留原名，成员会被误识别为独立技能重新出现在已安装列表。
        old_md = dst / "SKILL.md"
        new_md = dst / "member.md"
        if old_md.exists():
            old_md.rename(new_md)
            print(f"[改名] {src.name}/SKILL.md -> member.md（防 WorkBuddy 递归误识别）")
        print(f"[移动] {src.name} -> {dst}")
    print("[OK] 完成。原小 SKILL 已统一移入大 SKILL 的 references/members/，指令文件为 member.md。")


if __name__ == "__main__":
    main()
