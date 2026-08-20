# 分类准则（classification-guide.md）

> 供 superskill 执行「归类」时读取。本文给出分类维度、优先级裁定规则，
> 以及基于当前环境的**推荐分组方案**（随扫描自动刷新，见 catalog.md）。

## 一、分类维度
按以下顺序综合判定归属类别（前项优先）：
1. **能力领域** —— 输出物/核心动作类型（如生成视频 / 作图表 / 文档转换 / 浏览器自动化）。
2. **技术栈或产物格式** —— 同为视频、同为 PPT、同为 APK、同为浏览器。
3. **职责生命周期** —— 同一业务链的上游/中游/下游（如 口播稿→视频）。
4. **使用频次与耦合度** —— 常一起出现、互相引用的放一组。

若某 SKILL 跨多领域，按「主要输出物」归属；跨类依赖写在成员 SKILL.md 的调用关系里，不强行拆散。

## 二、归并判定规则
- **合并**：功能相似 / 同一领域 / 上下游耦合 / 高频一起用。
- **不合并**：领域差异大；系统内置（插件托管）SKILL；用户明确要保留独立的。
- **边界**：当两个小 SKILL 80% 场景重合才真正合并；仅主题相似但执行方式完全不同（如「OCR 图片」vs「生图」）不合并，只归同一**类目**但保留各自独立性。

## 三、优先级 / 调用关系裁定
同一类内，`aggregate_skill.py` 默认按给定顺序先到先得。需要人工裁定优先级时用以下规则：
1. **更专业/更贴合输入** 的成员优先于通用成员。
2. 有安全/隐私要求的（如本机数据、不上云）标记高优先级或加提示。
3. 纯工具类（被其它成员调用，非用户直接触发）降为"子工具"，只在大 SKILL 内路由，不单独对用户开放入口。
4. 存在先后依赖时明确标注（A→B），大 SKILL 只路由不代跑中间步骤。

## 四、推荐分组方案（以最近一次扫描为准）
> 运行 `scripts/scan_skills.py --dir ~/.workbuddy/skills --md <superskill>/references/catalog.md` 刷新清单后再落定分组。

| 类目 | 归类线索（供筛选） |
|---|---|
| 视频/媒体制作 | agent-video-forensics, ai-lyric-mv-pipeline, article-to-xhs-video, whiteboard-animation, whiteboard-video-workflow, jacky-motion, wechat-video-fetcher, hls-video-download |
| 医学内容生产 | med-script-generator, med-video-workflow, med-error-tracker, qa-socratic-coach, tumor-trend-chart, patient-record-md-archiver, consult-qa-organizer |
| 浏览器自动化 | browser-use, playwright-browser-automation, local-browser-devtools-mcp |
| Android/APK | android-template-overlay-apk, apk-build, github-actions-apk-fetch |
| 图像/语音感知 | ocr-images, gemini-image-gen, recording-transcribe |
| 文档/PPT/阅读 | html-to-ppt, qc-ppt-to-meeting-record, zhihu-to-epub-apkg, awesome-design-md, weread-skills |
| 数据/周报/分析 | lifelog-summary, dual-secretary-report, yibao-analysis |
| AI 基建/模型 | workbuddy-add-custom-model, deepseek-harness, qwen05-micro-classifier, sdg-content-factory, karpathy-guidelines |
| 桌面/系统自动化 | rpa-script-customizer, win-taskbar-tray-sync, portable-python-packager, win-* |
| 沉淀/错误库 | agent-error-log |

> 上表为**建议**，必须经用户确认后方可执行 `aggregate_skill.py`。
