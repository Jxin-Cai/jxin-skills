---
name: resume-craft
description: 技术人员简历优化与PDF生成工具。具备两大能力：(1) 将MD格式简历重构为专业的"候选人画像优先"结构，突出核心技能、量化成就和一句话定位，让面试官7秒内抓住重点；(2) 将MD简历转换为具有AI时代科技感的精美PDF。当用户需要优化简历内容、重构简历结构、美化简历排版、或将Markdown简历转PDF时使用。
---

# Resume Craft

技术人员简历优化与PDF生成技能。基于"面试官7秒初筛"原则，将普通简历重构为"候选人画像优先"的专业格式，并支持生成具有AI时代科技感的PDF。

## 两大核心能力

1. **简历内容重构（Restructure）**：将MD简历重新组织为专业结构
2. **简历PDF生成（PDF Export）**：将MD简历转换为精美PDF

## 能力一：简历内容重构

将用户的MD格式简历重构为"候选人画像优先"的专业结构。

### 工作流程

1. **阅读原始简历**：完整阅读用户提供的MD简历，提取所有信息
2. **阅读重构指南**：读取 `references/resume-structure.md` 了解整体结构规范
3. **阅读画像指南**：读取 `references/profile-snapshot.md` 了解候选人画像设计
4. **阅读模板示例**：读取 `assets/resume-template.md` 了解输出格式
5. **执行重构**：按指南重组简历内容，输出优化后的MD文件

### 重构核心原则

**"7秒定生死"**：面试官平均只花7.4秒做初筛决策。简历必须在顶部区域传递最大价值。

**输出结构（自上而下）**：

```
1. 候选人画像（Profile Snapshot）← 最关键，7秒内必须看到
   - 基础信息：姓名 | 年龄 | 毕业院校 | 工作年限 | 当前职位
   - 擅长行业 & 公司履历时间线
   - 核心技能标签（6-8个）
   - ★ 一句话定位（候选人的独特价值主张）

2. 核心优势（Key Strengths）← 3-5条量化成就

3. 技能矩阵（Skills Matrix）← 分类展示完整技能集

4. 工作经历（Work Experience）← 反向时间序列，成就驱动

5. 代表项目（Key Projects）← STAR法则，量化结果

6. 技术影响力（Technical Influence）← 博客/开源/演讲

7. 教育背景（Education）
```

### 关键要点

- **一句话定位**是简历的灵魂，格式：`「{年限}{核心角色}，{最突出成就}，{差异化优势}」`
- **技能标签**只选最强的6-8个，不是技能列表
- **工作经历**用成就而非职责描述，必须量化
- **代表项目**选2-3个最能证明能力的项目，用STAR法则
- 详细指南见 `references/resume-structure.md` 和 `references/profile-snapshot.md`

## 能力二：简历PDF生成

将MD格式简历转换为具有AI时代科技感的精美PDF。

### 工作流程

1. **确认简历文件路径**：获取用户的MD简历文件路径
2. **阅读样式指南**：读取 `references/pdf-styling.md` 了解样式设计
3. **运行转换脚本**：执行 `scripts/convert_resume_to_pdf.py` 生成PDF
4. **自动后处理**：写入元数据（标题、作者等）；可选加密和验证
5. **验证输出**：检查PDF文件生成成功，可用 `--verify` 生成预览图

### 使用方法

```bash
# 默认（琥珀深邃 — 深色画像区 + 橙色点缀）
python3 scripts/convert_resume_to_pdf.py /path/to/resume.md

# 指定输出路径
python3 scripts/convert_resume_to_pdf.py /path/to/resume.md --output /path/to/output.pdf

# 经典暖橙（浅色画像区 + 橙色侧边）
python3 scripts/convert_resume_to_pdf.py /path/to/resume.md --theme classic

# 生成后验证（将首页转为预览图）
python3 scripts/convert_resume_to_pdf.py /path/to/resume.md --verify

# 为PDF设置密码保护
python3 scripts/convert_resume_to_pdf.py /path/to/resume.md --encrypt mypassword

# 不写入元数据
python3 scripts/convert_resume_to_pdf.py /path/to/resume.md --no-metadata
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `input` | 输入的 Markdown 简历文件路径 |
| `--output`, `-o` | 输出的 PDF 文件路径（默认与输入同目录） |
| `--theme`, `-t` | 主题: `dark`(琥珀深邃) 或 `classic`(经典暖橙)，默认 dark |
| `--html-only` | 仅生成 HTML，不生成 PDF（用于调试样式） |
| `--encrypt PASSWORD` | 为 PDF 设置密码保护 |
| `--verify` | 生成后将 PDF 首页转为图片验证渲染效果 |
| `--no-metadata` | 不写入 PDF 元数据（默认自动写入标题、作者等） |

### 依赖安装

```bash
# 必要依赖
pip install markdown playwright pypdf
playwright install chromium

# 可选依赖
pip install weasyprint     # Playwright 不可用时的降级方案
pip install pypdfium2      # PDF 验证预览（纯 Python，推荐）
pip install pdf2image      # PDF 验证预览（需要系统安装 poppler）
```

### PDF 生成三级降级

脚本会按以下顺序尝试生成 PDF，自动降级：
1. **Playwright**（推荐）：渲染效果最佳，完整支持 CSS 和 Mermaid
2. **weasyprint**（降级）：纯 Python 方案，CSS 支持略有限制
3. **手动打印提示**：提示用户在浏览器中打开 HTML 手动打印

### 视觉设计理念

- **高端名片式开场**：打开 PDF 第一眼就是候选人画像，深炭底 + 琥珀橙点缀
- **Hermès 橙色调**：沉稳大气的橙色体系，体现专家级职业人的品味与热忱
- **信息层级清晰**：画像区总览全局 → 后续章节逐层展开证明
- **图表支持**：Mermaid 图表自动渲染，本地图片自动内联
- **打印友好**：A4尺寸，`print-color-adjust: exact` 确保打印还原

详细样式说明见 `references/pdf-styling.md`

## 参考资料索引

| 文件 | 内容 | 何时阅读 |
|------|------|----------|
| `references/resume-structure.md` | 简历整体结构与各章节设计指南 | 执行简历重构时 |
| `references/profile-snapshot.md` | 候选人画像详细设计指南与示例 | 设计简历顶部画像区域时 |
| `references/pdf-styling.md` | PDF视觉样式与CSS设计说明 | 需要调整PDF样式时 |
| `assets/resume-template.md` | 完整的简历模板示例 | 需要参考输出格式时 |
| `scripts/convert_resume_to_pdf.py` | MD转PDF转换脚本（含元数据、加密、验证、降级） | 生成PDF时执行 |
