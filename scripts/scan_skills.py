#!/usr/bin/env python3
"""
scan_skills.py — 扫描并盘点一个或多个 Skill 根目录下的全部 SKILL，
生成目录清单（Markdown 表格 + JSON），供 superskill 做归类。

用法:
  python scan_skills.py --dir <根目录> [--dir <根目录>...] \
      [--json <out.json>] [--md <out.md>]

- --dir  可重复传入；默认 ~/.workbuddy/skills
- --json 输出结构化清单（含 frontmatter + body 摘要 + 内置资源）
- --md   输出人读 Markdown 清单表
- 均未给时打印 JSON 到 stdout
"""
import json, re, sys, datetime
from pathlib import Path

DEFAULT_DIRS = [Path.home() / ".workbuddy" / "skills"]


def parse_frontmatter(text: str) -> dict:
    """解析 YAML 头，容错（description 可能多行/带引号）。"""
    fm: dict = {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        try:
            k, _, v = line.partition(":")
        except Exception:
            continue
        k = k.strip()
        if not k or k.startswith("-"):
            continue
        v = v.strip().strip('"').strip("'")
        fm[k] = v
    return fm


def body_snippet(text: str, n: int = 200) -> str:
    """去掉 YAML 头与代码块，取正文前 n 字作为能力摘要。"""
    text = re.sub(r"^---\s*\n.*?\n---", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    lines = [l.strip() for l in text.splitlines()
             if l.strip() and not l.lstrip().startswith(("#", "---"))]
    return " ".join(lines)[:n]


def scan_skill(skill_dir: Path) -> dict:
    name = skill_dir.name
    info = {"name": name, "path": str(skill_dir), "description": "", "trigger": "", "bundled": []}
    smd = skill_dir / "SKILL.md"
    if smd.exists():
        text = smd.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        info["description"] = fm.get("description") or fm.get("summary") or ""
        # 触发条件优先取正文中 "触发/适用场景/何时" 所在单行
        trig = re.search(r"(?:触发|适用场景|何时当|when to)[^\n]{0,120}", text, re.I)
        info["trigger"] = re.sub(r"\s+", " ", trig.group(0)).strip() if trig else ""
        info["snippet"] = body_snippet(text)
    info["bundled"] = [d.name for d in skill_dir.iterdir() if d.is_dir()]
    return info


def main() -> None:
    args = sys.argv[1:]
    dirs = list(DEFAULT_DIRS)
    out_json, out_md = None, None
    i = 0
    while i < len(args):
        if args[i] == "--dir" and i + 1 < len(args):
            dirs.append(Path(args[i + 1])); i += 2
        elif args[i] == "--json" and i + 1 < len(args):
            out_json = args[i + 1]; i += 2
        elif args[i] == "--md" and i + 1 < len(args):
            out_md = args[i + 1]; i += 2
        else:
            i += 1

    skills: list[dict] = []
    for d in dirs:
        if not d.exists():
            continue
        for child in sorted(d.iterdir()):
            if child.is_dir() and (child / "SKILL.md").exists():
                skills.append(scan_skill(child))

    # 去重（同名取第一）
    seen: dict = {}
    for s in skills:
        seen.setdefault(s["name"], s)
    skills = sorted(seen.values(), key=lambda x: x["name"])

    # 排除 superskill 自身（它是整理者，不是被整理对象）
    skills = [s for s in skills if s["name"] != "superskill"]

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if out_md:
        Path(out_md).parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# SKILL 目录清单（superskill 自动生成）", "", f"_扫描时间: {ts} · 共 {len(skills)} 个_", "",
                 "| 名称 | 用途/描述 | 触发片段 | 内置资源 |", "|---|---|---|---|"]
        for s in skills:
            desc = re.sub(r"\s+", " ", s.get("description") or "")[:140].replace("|", "\\|")
            trig = re.sub(r"\s+", " ", s.get("trigger") or "")[:90].replace("|", "\\|")
            lines.append(f"| {s['name']} | {desc} | {trig} | {', '.join(s['bundled']) or '-'} |")
        Path(out_md).write_text("\n".join(lines), encoding="utf-8")
        print(f"[OK] Markdown 清单已写: {out_md}  ({len(skills)} skills)")

    if out_json:
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(out_json).write_text(json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] JSON 清单已写: {out_json}")

    if not out_md and not out_json:
        print(json.dumps(skills, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
