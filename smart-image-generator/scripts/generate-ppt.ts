#!/usr/bin/env bun
/**
 * PPT生成脚本
 *
 * 功能：
 * 1. 理解用户提供的内容
 * 2. 制定PPT分页计划
 * 3. 生成每页提示词（内容页+引导页）
 * 4. 基于提示词生成PPT图片
 *
 * 目录结构：
 * ppt/
 *   {ppt-name}/
 *     prompts/
 *       style-config.md     # 共用样式配置
 *       page-01.md          # 第1页提示词
 *       page-02.md          # 第2页提示词
 *       ...
 *     images/
 *       page-01.png         # 第1页图片
 *       page-02.png         # 第2页图片
 *       ...
 *     plan.json            # 分页计划
 */

import fs from "node:fs/promises";
import path from "node:path";
import { GeminiClient } from "./lib/gemini-client";
import { generateImage } from "./generate-image";

interface PPTConfig {
  contentFile: string; // 用户内容文件
  outputDir?: string; // 输出目录（默认：ppt/）
  pptName?: string; // PPT名称（默认：自动提取）
  enableChinese?: boolean; // 是否启用中文生成
  stylePreset?: string; // 样式预设（默认：thoughtworks）
}

interface PPTPage {
  pageNumber: number;
  pageType: "cover" | "section" | "content" | "end"; // 封面、引导页、内容页、结束页
  title: string;
  content: string; // 页面主要内容
  notes?: string; // 备注说明
}

interface PPTPlan {
  pptName: string;
  totalPages: number;
  pages: PPTPage[];
  styleConfig: {
    enableChinese: boolean;
    stylePreset: string;
    colorScheme?: string;
    fontFamily?: string;
  };
}

/**
 * 分析用户内容并制定分页计划
 */
async function analyzePPTContent(
  content: string,
  config: PPTConfig
): Promise<PPTPlan> {
  console.log("📖 正在分析内容并制定分页计划...\n");

  // TODO: 这里应该调用AI来分析内容并制定计划
  // 暂时使用简单的规则来演示流程

  const lines = content.split("\n").filter((line) => line.trim());
  const pptName =
    config.pptName || extractPPTName(content) || `ppt-${Date.now()}`;

  // 简单的分页逻辑：根据标题分页
  const pages: PPTPage[] = [];
  let currentSection: PPTPage | null = null;
  let pageNumber = 1;

  // 封面页
  pages.push({
    pageNumber: pageNumber++,
    pageType: "cover",
    title: lines[0] || "演示文稿",
    content: lines[0] || "演示文稿",
    notes: "封面页",
  });

  // 解析内容页
  for (const line of lines.slice(1)) {
    if (line.startsWith("#")) {
      // 章节标题（引导页）
      if (currentSection) {
        pages.push(currentSection);
      }
      const title = line.replace(/^#+\s*/, "");
      currentSection = {
        pageNumber: pageNumber++,
        pageType: "section",
        title,
        content: title,
        notes: "章节引导页",
      };
    } else if (currentSection && line.trim()) {
      // 内容
      currentSection.content += "\n" + line;
    }
  }

  if (currentSection) {
    pages.push(currentSection);
  }

  // 结束页
  pages.push({
    pageNumber: pageNumber++,
    pageType: "end",
    title: "谢谢观看",
    content: "Thank You",
    notes: "结束页",
  });

  const plan: PPTPlan = {
    pptName,
    totalPages: pages.length,
    pages,
    styleConfig: {
      enableChinese: config.enableChinese ?? true,
      stylePreset: config.stylePreset || "thoughtworks",
      colorScheme: "thoughtworks-teal-pink",
      fontFamily: "sans-serif",
    },
  };

  console.log(`✓ 分页计划完成：共 ${plan.totalPages} 页\n`);
  return plan;
}

/**
 * 从内容中提取PPT名称
 */
function extractPPTName(content: string): string | null {
  const firstLine = content.split("\n")[0]?.trim();
  if (firstLine) {
    // 去除特殊字符，保留中英文和数字
    const name = firstLine
      .replace(/^#+\s*/, "")
      .replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .substring(0, 50);
    return name || null;
  }
  return null;
}

/**
 * 生成样式配置文件
 */
async function generateStyleConfig(
  plan: PPTPlan,
  outputDir: string
): Promise<void> {
  const { enableChinese, stylePreset, colorScheme, fontFamily } =
    plan.styleConfig;

  // 根据样式预设生成不同的配置
  let styleConfig = "";

  if (stylePreset === "thoughtworks") {
    styleConfig = `# PPT样式配置 - ThoughtWorks风格

## 🎨 品牌视觉系统

### 核心配色
- **主色 - 深青色**：#003B4D（专业、稳重、品牌主色）
- **强调色 - 粉红色**：#FF6B9D（活力、创新、强调）

### 辅助色
- 青色：#65B4C4
- 橙色：#D9A441
- 绿色：#6FA287
- 紫色：#8B7BA8

### 背景和文字
- 白色背景：#FFFFFF（内容页）
- 深青背景：#003B4D（封面/章节页）
- 浅灰背景：#F0F0F0（卡片）
- 黑色文字：#000000（白底）
- 白色文字：#FFFFFF（深色底）

## 📐 设计规范

### 页面设置
- **比例**：16:9（1920x1080px）
- **边距**：上下左右各80-100px
- **网格**：12列网格系统

### 字体规范（官方标准）
- **标题字体**：Bitter Bold（粗体）- ⚠️ 只能使用Bold
- **副标题字体**：Inter SemiBold（半粗体）- ⚠️ 只能使用SemiBold
- **正文字体**：Inter Regular（常规体）- ⚠️ 只能使用Regular
- **强调字体**：Inter Bold（粗体）
${
  enableChinese
    ? "- **中文字体**：Bitter/Inter对应的中文字体（思源黑体/微软雅黑）\n"
    : ""
}
- **字号**：主标题48-72pt / 副标题24-36pt / 正文14-18pt
- ⚠️ **禁止使用**：细体、超细体、轻量体、中等体、超粗体、黑体

### 文本规范（ThoughtWorks写作指南）
- **大小写**：句首大写格式（Sentence case）
  - 句子首字母大写，内部仅专有名词大写
  - ✅ "We have fantastic products"
  - ❌ "We Have Fantastic Products"
- **公司名称**：Thoughtworks（T大写，w小写）
- **标题末尾**：无句号
- **数字**：个位数拼写（two, five），两位数及以上用数字（10, 34）
- **日期**：June 20, 2025（月份 日期, 年份）
- **语言**：美式英语

### 图形规范
- **风格**：扁平化、几何化
- **形状**：菱形、圆形、六边形
- **阴影**：柔和投影（0 4px 12px rgba(0,0,0,0.1)）
- **线条**：粗线条，简洁

### 页面元素
- **Logo**：左下角，ThoughtWorks标识（白色+粉色）
- **页码**：右下角，小字（第 X/${plan.totalPages} 页）

## 🎯 设计原则

1. **简洁至上**：去除非必要元素，突出核心信息
2. **对比鲜明**：深浅色对比、字号对比明显
3. **留白充分**：不拥挤，让内容呼吸
4. **图形化表达**：用图形、图表代替文字
5. **品牌一致**：严格遵循ThoughtWorks配色和字体

## 📄 页面类型规范

### 封面页/章节页（深色背景）
- 背景：深青色 #003B4D 全屏
- 标题：白色，超大字号，居中或左对齐
- 副标题：粉色 #FF6B9D
- Logo：左下角

### 内容页（白色背景）
- 背景：白色
- 标题：黑色，顶部左对齐
- 布局：左文右图（40/60）或卡片式
- 可选底部色带：橙/深青/浅青/粉

### 图表页（白色背景）
- 背景：白色（或左白右浅灰）
- 标题：黑色
- 布局：左文（30-40%）右图（60-70%）
- 图表：使用品牌色，扁平化

## 特殊说明

**重要**：此配置将应用于所有PPT页面，确保整体风格统一。

**语言设置**：${enableChinese ? "✅ 支持中文文本显示" : "English only"}

---
生成时间: ${new Date().toISOString()}
样式版本: ThoughtWorks v1.0
`;
  } else {
    // 其他样式预设的配置（保留原有逻辑）
    styleConfig = `# PPT样式配置

## 基础设置

- **语言**: ${enableChinese ? "中文（支持中文文本）" : "英文"}
- **样式预设**: ${stylePreset}
- **配色方案**: ${colorScheme}
- **字体**: ${fontFamily}

## 样式要求

### 布局
- 16:9 比例，专业PPT设计
- 清晰的层次结构
- 合理的留白

### 视觉风格
- 现代、简洁
- 配色统一，符合${colorScheme}方案
- 图文并茂

### 文字规范
${enableChinese ? "- 支持中文文本显示\n- 中文字体清晰易读" : "- 英文文本为主"}
- 标题醒目，正文清晰
- 字号层次分明

### 页面元素
- 页码标注（${plan.totalPages}页）
- Logo位置（右上角/左下角）
- 装饰元素简洁

## 特殊说明

**重要**：此配置将应用于所有PPT页面，确保整体风格统一。

---
生成时间: ${new Date().toISOString()}
`;
  }

  const configPath = path.join(outputDir, "prompts", "style-config.md");
  await fs.writeFile(configPath, styleConfig, "utf-8");
  console.log(`✓ 样式配置已保存: ${configPath}\n`);
}

/**
 * 生成单页提示词
 */
async function generatePagePrompt(
  page: PPTPage,
  plan: PPTPlan,
  outputDir: string
): Promise<string> {
  const { enableChinese, stylePreset } = plan.styleConfig;

  // 根据样式预设和页面类型生成不同的提示词
  let prompt = "";

  if (stylePreset === "thoughtworks") {
    // ThoughtWorks 样式的详细提示词
    switch (page.pageType) {
      case "cover":
        prompt = `Create a Thoughtworks-branded PPT cover page

**Title**: ${page.title}

**Thoughtworks Brand Style**:
- Background: Teal #003B4D full screen
- Main title: White, 60-72pt, **Bitter Bold**, center or left aligned, vertically centered
  - Text: "${page.title}" (sentence case)
- Subtitle: Pink #FF6B9D, 24-36pt, **Inter SemiBold** (if any)
- Logo: Bottom left, Thoughtworks logo (white + pink accent)
- Copyright: Bottom, white, 10pt, **Inter Regular**
- Overall: Minimalist, generous whitespace, professional

**Typography Rules** (CRITICAL):
- Title font: **Bitter Bold ONLY** (no other weights)
- Subtitle font: **Inter SemiBold ONLY** (no other weights)
- Use sentence case: First letter capitalized, rest lowercase except proper nouns
- Company name: "Thoughtworks" (capital T, lowercase w)
- No period at end of title
${enableChinese ? "- Support Chinese text with proper font\n" : ""}

**Layout**:
- Ratio: 16:9 (1920x1080px)
- Margins: 80-100px all sides
- Clean, spacious design

**Style**: Flat design, modern, professional, brand-consistent
`;
        break;

      case "section":
        prompt = `Create a Thoughtworks-branded PPT section page

**Section Title**: ${page.title}

**Thoughtworks Brand Style**:
- Background: Teal #003B4D full screen
- Section title: White, 72pt, **Bitter Bold**, left aligned
  - Text: "${page.title}" (sentence case)
- Section number/subtitle: Pink #FF6B9D, 36pt, **Inter SemiBold** (if any)
- Logo: Bottom left
- Page number: Bottom right, white, 10pt, "Page ${page.pageNumber} of ${
          plan.totalPages
        }"

**Typography Rules** (CRITICAL):
- Title font: **Bitter Bold ONLY**
- Subtitle font: **Inter SemiBold ONLY**
- Sentence case: "Section title example" not "Section Title Example"
- Numbers: Spell single digits (two, five), use numerals for 10+ (15, 34)
- No period at end of title
${enableChinese ? "- Support Chinese text\n" : ""}

**Layout**:
- 16:9 ratio
- Clean transition design
- Strong visual impact

**Style**: Flat, minimalist, strong brand presence
`;
        break;

      case "content":
        prompt = `Create a Thoughtworks-branded PPT content page

**Title**: ${page.title}

**Content**:
${page.content}

**Thoughtworks Brand Style**:
- Background: White #FFFFFF
- Title: Black, 48pt, **Bitter Bold**, top left aligned
  - Text: "${page.title}" (sentence case, no period)
- Subtitle: Black, 24pt, **Inter SemiBold** (if any)
- Body text: Black, 16-18pt, **Inter Regular**, left aligned
- Emphasis: Black, 16-18pt, **Inter Bold**
- Layout: Left text (40%) + Right image/chart (60%)
  OR: Card layout (2-3 columns)
- Card background: Light gray #F0F0F0
- Card titles: Colored background, white text, **Inter SemiBold**, 14-16pt
- Bottom color band (optional): Orange #D9A441 / Teal #003B4D / Cyan #65B4C4 / Pink #FF6B9D (25% each, 20-30px height)
- Logo: Bottom left, colored version
- Page number: Bottom right, black, 10pt, "Page ${page.pageNumber} of ${
          plan.totalPages
        }"

**Typography Rules** (CRITICAL):
- Title: **Bitter Bold ONLY**
- Subtitle: **Inter SemiBold ONLY**
- Body: **Inter Regular ONLY**
- Emphasis: **Inter Bold ONLY**
- Sentence case for all text (titles, subtitles, body, captions)
- List items: Sentence case, no periods
- Numbers: Spell single digits (two, five), numerals for 10+ (15, 34)
${enableChinese ? "- Support Chinese text with proper fonts\n" : ""}

**Diagram Requirements** (if needed):
- Flat geometric shapes (diamond/circle/hexagon)
- Brand colors: Teal #003B4D / Pink #FF6B9D / Cyan #65B4C4 / Orange #D9A441 / Green #6FA287
- Text inside shapes: White, **Inter SemiBold**, 14-16pt
- Text outside shapes: Black, **Inter Regular**, 12-14pt
- Soft shadow: 0 4px 12px rgba(0,0,0,0.1)

**Layout**: 16:9 ratio, clear hierarchy, generous spacing
**Style**: Modern, professional, visual-driven
`;
        break;

      case "end":
        prompt = `Create a Thoughtworks-branded PPT ending page

**Text**: ${page.content}

**Thoughtworks Brand Style**:
- Background: Teal #003B4D full screen
- Main text: "Thank you" or "${
          page.content
        }", white, 60pt, **Bitter Bold**, center aligned
- Contact info (optional): White, 18-24pt, **Inter Regular**, centered
- Logo: Bottom left
- Page number: Bottom right, white, 10pt, "Page ${page.pageNumber} of ${
          plan.totalPages
        }"

**Typography Rules** (CRITICAL):
- Main text: **Bitter Bold ONLY**
- Contact: **Inter Regular ONLY**
- Sentence case (e.g., "Thank you" not "Thank You")
${enableChinese ? "- Support Chinese text\n" : ""}

**Layout**:
- 16:9 ratio
- Clean, minimalist
- Centered alignment

**Style**: Simple, professional, polite
`;
        break;
    }
  } else {
    // 其他样式预设（保留原有逻辑）
    switch (page.pageType) {
      case "cover":
        prompt = `创建一个专业的PPT封面页

**标题**: ${page.title}

**设计要求**:
- 大标题居中，醒目
- 副标题或作者信息（如有）
- 简洁的装饰元素
- 符合${stylePreset}风格

${enableChinese ? "**语言**: 支持中文显示" : ""}

**比例**: 16:9
`;
        break;

      case "section":
        prompt = `创建一个PPT章节引导页

**章节标题**: ${page.title}

**设计要求**:
- 章节标题突出显示
- 简洁的过渡设计
- 与整体风格一致

${enableChinese ? "**语言**: 支持中文显示" : ""}

**页码**: 第 ${page.pageNumber}/${plan.totalPages} 页
**比例**: 16:9
`;
        break;

      case "content":
        prompt = `创建一个PPT内容页

**标题**: ${page.title}

**内容**:
${page.content}

**设计要求**:
- 标题清晰
- 内容分点列出
- 图文结合（如适用）
- 布局简洁

${enableChinese ? "**语言**: 支持中文显示" : ""}

**页码**: 第 ${page.pageNumber}/${plan.totalPages} 页
**比例**: 16:9
`;
        break;

      case "end":
        prompt = `创建一个PPT结束页

**文字**: ${page.content}

**设计要求**:
- 感谢文字居中
- 联系方式（可选）
- 简洁收尾

${enableChinese ? "**语言**: 支持中文显示" : ""}

**页码**: 第 ${page.pageNumber}/${plan.totalPages} 页
**比例**: 16:9
`;
        break;
    }
  }

  // 保存提示词
  const promptPath = path.join(
    outputDir,
    "prompts",
    `page-${String(page.pageNumber).padStart(2, "0")}.md`
  );
  await fs.writeFile(promptPath, prompt, "utf-8");

  return promptPath;
}

/**
 * 组合样式配置和页面提示词
 */
async function combinePrompts(
  pagePromptPath: string,
  styleConfigPath: string
): Promise<string> {
  const styleConfig = await fs.readFile(styleConfigPath, "utf-8");
  const pagePrompt = await fs.readFile(pagePromptPath, "utf-8");

  // 提取样式配置的关键要求
  const styleRequirements = `
--- 样式配置 ---
${styleConfig.split("## 样式要求")[1] || ""}

--- 页面内容 ---
${pagePrompt}
`;

  return styleRequirements;
}

/**
 * 生成PPT
 */
async function generatePPT(config: PPTConfig): Promise<void> {
  console.log(`
╔═══════════════════════════════════════════════════════╗
║   PPT生成器                                           ║
╚═══════════════════════════════════════════════════════╝
`);

  // 1. 读取用户内容
  console.log(`📖 读取内容文件: ${config.contentFile}`);
  const content = await fs.readFile(config.contentFile, "utf-8");

  if (!content || content.trim().length === 0) {
    throw new Error("内容文件为空");
  }

  // 2. 分析内容并制定分页计划
  const plan = await analyzePPTContent(content, config);

  // 3. 创建输出目录
  const baseDir = config.outputDir || "ppt";
  const pptDir = path.join(baseDir, plan.pptName);
  const promptsDir = path.join(pptDir, "prompts");
  const imagesDir = path.join(pptDir, "images");

  await fs.mkdir(promptsDir, { recursive: true });
  await fs.mkdir(imagesDir, { recursive: true });

  console.log(`📂 PPT目录: ${pptDir}\n`);

  // 4. 保存分页计划
  const planPath = path.join(pptDir, "plan.json");
  await fs.writeFile(planPath, JSON.stringify(plan, null, 2), "utf-8");
  console.log(`✓ 分页计划已保存: ${planPath}\n`);

  // 5. 生成样式配置
  await generateStyleConfig(plan, pptDir);
  const styleConfigPath = path.join(promptsDir, "style-config.md");

  // 6. 生成每一页
  console.log(`🎨 开始生成PPT页面...\n`);

  for (const page of plan.pages) {
    console.log(
      `\n--- 生成第 ${page.pageNumber}/${plan.totalPages} 页 (${page.pageType}) ---`
    );
    console.log(`标题: ${page.title}\n`);

    // 6.1 生成页面提示词
    const pagePromptPath = await generatePagePrompt(page, plan, pptDir);
    console.log(`✓ 提示词已生成: ${pagePromptPath}`);

    // 6.2 组合样式配置和页面提示词
    const combinedPrompt = await combinePrompts(
      pagePromptPath,
      styleConfigPath
    );

    // 6.3 临时保存组合后的提示词
    const tempPromptPath = path.join(
      promptsDir,
      `page-${String(page.pageNumber).padStart(2, "0")}-combined.md`
    );
    await fs.writeFile(tempPromptPath, combinedPrompt, "utf-8");

    // 6.4 生成图片
    const imagePath = await generateImage({
      promptFile: tempPromptPath,
      output: path.join(
        imagesDir,
        `page-${String(page.pageNumber).padStart(2, "0")}.png`
      ),
    });

    console.log(`✅ 第 ${page.pageNumber} 页已生成: ${imagePath}\n`);

    // 清理临时文件
    await fs.unlink(tempPromptPath);
  }

  console.log(`
╔═══════════════════════════════════════════════════════╗
║   ✅ PPT生成完成！                                    ║
╚═══════════════════════════════════════════════════════╝

📁 PPT目录: ${pptDir}
📄 共生成 ${plan.totalPages} 页
📂 提示词: ${promptsDir}
🖼️  图片:   ${imagesDir}
`);
}

// CLI 使用
if (import.meta.main) {
  const args = process.argv.slice(2);

  const config: Partial<PPTConfig> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === "--content" || arg === "-c") {
      config.contentFile = args[++i];
    } else if (arg === "--output" || arg === "-o") {
      config.outputDir = args[++i];
    } else if (arg === "--name" || arg === "-n") {
      config.pptName = args[++i];
    } else if (arg === "--chinese") {
      config.enableChinese = true;
    } else if (arg === "--english") {
      config.enableChinese = false;
    } else if (arg === "--style" || arg === "-s") {
      config.stylePreset = args[++i];
    } else if (arg === "--help" || arg === "-h") {
      console.log(`
用法: bun generate-ppt.ts [选项]

选项:
  -c, --content <file>      内容文件路径 (必需)
  -o, --output <dir>        输出目录 (默认: ppt/)
  -n, --name <name>         PPT名称 (默认: 自动提取)
  --chinese                 启用中文生成 (默认)
  --english                 使用英文生成
  -s, --style <preset>      样式预设 (默认: thoughtworks)

样式预设:
  thoughtworks    ThoughtWorks 企业风格（默认）
  professional    专业商务风格
  modern          现代简约风格
  minimal         极简主义风格

示例:
  # 基础用法（使用ThoughtWorks默认样式）
  bun generate-ppt.ts -c content.md
  
  # 指定PPT名称和样式
  bun generate-ppt.ts -c content.md -n "产品发布会" --style modern
  
  # 英文PPT
  bun generate-ppt.ts -c content.md --english
`);
      process.exit(0);
    }
  }

  if (!config.contentFile) {
    console.error(`
❌ 错误: 缺少必需参数

用法: bun generate-ppt.ts -c <内容文件>

使用 --help 查看详细帮助
`);
    process.exit(1);
  }

  try {
    await generatePPT(config as PPTConfig);
  } catch (err) {
    console.error("❌ 错误:", err);
    process.exit(1);
  }
}

export { generatePPT, type PPTConfig, type PPTPlan, type PPTPage };
