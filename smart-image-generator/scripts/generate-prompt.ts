/**
 * 根据场景和风格生成提示词
 */

import fs from "node:fs/promises";
import path from "node:path";

interface GeneratePromptOptions {
  scene: string;
  style: string;
  content: string;
  output: string;
  metadata?: Record<string, any>;
}

async function generatePrompt(options: GeneratePromptOptions): Promise<string> {
  console.log("📝 生成提示词...");
  console.log(`   场景: ${options.scene}`);
  console.log(`   风格: ${options.style}`);

  // 1. 读取场景模板
  const sceneTemplatePath = path.join(
    __dirname,
    "../references/scene-types",
    `${options.scene}.md`,
  );

  let sceneTemplate = "";
  try {
    sceneTemplate = await fs.readFile(sceneTemplatePath, "utf-8");
  } catch (err) {
    throw new Error(`场景模板不存在: ${options.scene}`);
  }

  // 2. 读取风格定义
  const styleDefinitionPath = path.join(
    __dirname,
    "../references/styles",
    `${options.style}.md`,
  );

  let styleDefinition = "";
  try {
    styleDefinition = await fs.readFile(styleDefinitionPath, "utf-8");
  } catch (err) {
    throw new Error(`风格定义不存在: ${options.style}`);
  }

  // 3. 提取关键信息
  const title = options.metadata?.title || extractTitle(options.content);
  const summary = extractSummary(options.content);
  const keywords = extractKeywords(options.content);

  // 4. 生成提示词
  const prompt = buildPrompt({
    scene: options.scene,
    style: options.style,
    title,
    summary,
    keywords,
    content: options.content,
  });

  // 5. 保存提示词
  const outputDir = path.dirname(options.output);
  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(options.output, prompt, "utf-8");

  console.log(`✅ 提示词已生成: ${options.output}`);
  return options.output;
}

/**
 * 提取标题
 */
function extractTitle(content: string): string {
  // 尝试提取第一个 H1 标题
  const h1Match = content.match(/^#\s+(.+)$/m);
  if (h1Match) return h1Match[1];

  // 或取第一行
  const firstLine = content.split("\n")[0];
  return firstLine.slice(0, 50);
}

/**
 * 提取摘要
 */
function extractSummary(content: string): string {
  // 简单取前 200 字符
  return content.slice(0, 200).replace(/\s+/g, " ").trim();
}

/**
 * 提取关键词
 */
function extractKeywords(content: string): string[] {
  // 简单的关键词提取（实际可以使用更复杂的算法）
  const words = content
    .toLowerCase()
    .replace(/[^\w\s\u4e00-\u9fa5]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2);

  // 统计词频
  const freq = new Map<string, number>();
  for (const w of words) {
    freq.set(w, (freq.get(w) || 0) + 1);
  }

  // 返回前 10 个高频词
  return Array.from(freq.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([w]) => w);
}

/**
 * 构建提示词
 * ⚠️ 关键修复：Visual 部分必须全部用英文，描述具体视觉元素
 * 中文只能出现在 Title 和引用的具体内容中
 */
function buildPrompt(params: {
  scene: string;
  style: string;
  title: string;
  summary: string;
  keywords: string[];
  content: string;
}): string {
  // 精准检测内容语言
  const hasChinese = /[\u4e00-\u9fa5]/.test(params.title + params.summary);

  // 风格映射（保持英文，这是风格名称）
  const styleMap: Record<string, string> = {
    notion: "notion-style",
    obsidian: "obsidian-style",
    blueprint: "blueprint-style",
    warm: "warm-style",
  };
  const styleEn = styleMap[params.style] || params.style;

  // 场景映射（保持英文，这是场景类型）
  const sceneMap: Record<string, string> = {
    cover: "article cover",
    poster: "poster",
    flowchart: "flowchart",
    mindmap: "mindmap",
    note: "visual note",
  };
  const sceneEn = sceneMap[params.scene] || params.scene;

  // 生成关键词描述（保持原始语言）
  const keywordsDesc = params.keywords.slice(0, 5).join(", ");

  // 结构化的提示词格式
  // - 独立的 Language 章节
  // - 明确的 Text Requirements
  // - 多处强调语言要求
  const language = hasChinese ? "Chinese" : "English";
  const punctuationNote = hasChinese
    ? '(Chinese punctuation: ""，。！？)'
    : "(English punctuation)";

  return `Create a ${styleEn} ${sceneEn} following these guidelines:

## Image Specifications

- **Type**: ${sceneEn}
- **Aspect Ratio**: 16:9
- **Style**: ${styleEn}
- **Language**: ${language}

## Language Requirements (CRITICAL)

- **All text must be in ${language}**
- Match punctuation style ${punctuationNote}
- Ensure text is properly rendered and readable
- Use appropriate fonts for ${language} characters

## Text Style

- Main title should be prominent and eye-catching
- Key text should be bold and enlarged
- Use visual hierarchy to guide attention
- Ensure all text is clearly legible

## Visual Composition

- Main composition: clean and modern layout
- Key elements: ${keywordsDesc}
- Layout: balanced design with clear hierarchy
- Typography: title prominence with supporting visuals
- Style notes: ${getStyleNotes(params.style)}

## Content to Visualize

**Title** (large, in ${language}):
${params.title}

**Context**:
${params.summary}

**Key elements**: ${keywordsDesc}

---

Please use nano banana pro to generate this ${sceneEn} ensuring all text is in ${language} with proper character rendering.

Generated: ${new Date().toISOString()}
`;
}

/**
 * 获取风格要点
 * ⚠️ 全部使用英文，避免中文在 Visual/Style 描述中导致乱码
 */
function getStyleNotes(style: string): string {
  const notesEN: Record<string, string> = {
    notion:
      "minimal clean lines, soft pastel colors (blue/purple/pink), card-based layout, modern sans-serif",
    obsidian:
      "hand-drawn aesthetic, purple/pink accents, sketch elements, warm approachable",
    blueprint:
      "technical precision, grid background, engineering annotations, blue scheme",
    warm: "warm gradients (orange to pink), friendly inviting, soft shadows, comfortable feel",
  };
  return (
    notesEN[style] ||
    "clean modern aesthetic, balanced composition, professional"
  );
}

/**
 * 获取默认输出路径
 * 三级优先级：
 * 1. 用户指定路径（--output）：最高优先级
 * 2. 输入文件目录（--file）：在输入文件所在目录创建 smart-image-generator-output/
 * 3. 项目根目录：fallback，在项目根目录创建 smart-image-generator-output/
 */
async function getDefaultOutputPath(
  scene: string,
  style: string,
  inputFile?: string,
): Promise<string> {
  let baseDir: string;

  // 优先级 2：如果提供了输入文件，使用输入文件所在目录
  if (inputFile) {
    // 获取输入文件的目录（绝对路径）
    const inputFileAbs = path.isAbsolute(inputFile)
      ? inputFile
      : path.resolve(process.cwd(), inputFile);
    baseDir = path.dirname(inputFileAbs);
    console.log(`📂 使用输入文件目录: ${baseDir}`);
  } else {
    // 优先级 3：查找项目根目录
    let currentDir = process.cwd();
    let rootDir = currentDir;

    // 尝试向上查找项目根目录（package.json）
    while (currentDir !== path.dirname(currentDir)) {
      const packageJsonPath = path.join(currentDir, "package.json");
      try {
        await fs.access(packageJsonPath);
        rootDir = currentDir;
        break;
      } catch {
        // 继续向上查找
      }
      currentDir = path.dirname(currentDir);
    }
    baseDir = rootDir;
    console.log(`📂 使用项目根目录: ${baseDir}`);
  }

  // 在 baseDir 下创建 smart-image-generator-output/prompts/
  const outputDir = path.join(
    baseDir,
    "smart-image-generator-output",
    "prompts",
  );

  // 生成文件名：scene-style-timestamp.md
  const timestamp = new Date()
    .toISOString()
    .replace(/[:.]/g, "-")
    .split("T")[0];
  const filename = `${scene}-${style}-${timestamp}.md`;

  return path.join(outputDir, filename);
}

// CLI 使用
if (import.meta.main) {
  const args = process.argv.slice(2);

  const options: Partial<GeneratePromptOptions> = {
    style: "obsidian", // 默认风格
  };

  // 临时变量：输入文件路径（用于确定默认输出目录）
  let inputFile: string | undefined;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === "--scene" || arg === "-s") {
      options.scene = args[++i];
    } else if (arg === "--style") {
      options.style = args[++i];
    } else if (arg === "--content" || arg === "-c") {
      options.content = args[++i];
    } else if (arg === "--output" || arg === "-o") {
      options.output = args[++i];
    } else if (arg === "--file" || arg === "-f") {
      // 新增：输入文件路径（用于确定输出目录）
      inputFile = args[++i];
    }
  }

  if (!options.scene || !options.content) {
    console.error(`
用法: bun generate-prompt.ts [选项]

选项:
  -s, --scene <type>    场景类型 (必需): cover/flowchart/poster/mindmap/note
  --style <name>        视觉风格 (默认: obsidian): obsidian/notion/blueprint/warm
  -c, --content <text>  内容文本 (必需)
  -f, --file <path>     输入文件路径 (可选，用于确定输出目录)
  -o, --output <file>   输出路径 (可选)

📂 输出目录三级优先级:
  1️⃣  用户指定 (--output): 使用指定路径
  2️⃣  输入文件同目录 (--file): 在输入文件目录创建 smart-image-generator-output/
  3️⃣  项目根目录: 在项目根目录创建 smart-image-generator-output/

示例:
  # 优先级 2：使用输入文件目录
  bun generate-prompt.ts \\
    --scene cover \\
    --file docs/article.md \\
    --content "文章内容..."
  → 输出: docs/smart-image-generator-output/prompts/cover-notion-2026-01-29.md

  # 优先级 1：指定输出路径
  bun generate-prompt.ts \\
    --scene cover \\
    --content "文章内容..." \\
    --output /custom/path/prompt.md
  → 输出: /custom/path/prompt.md

  # 优先级 3：使用项目根目录
  bun generate-prompt.ts \\
    --scene cover \\
    --content "文章内容..."
  → 输出: 项目根目录/smart-image-generator-output/prompts/cover-notion-2026-01-29.md
`);
    process.exit(1);
  }

  // 如果没有指定输出路径，使用默认路径（三级优先级）
  if (!options.output) {
    options.output = await getDefaultOutputPath(
      options.scene!,
      options.style!,
      inputFile, // 传入输入文件路径（可选）
    );
    console.log(`📂 使用默认输出路径: ${options.output}`);
  }

  try {
    await generatePrompt(options as GeneratePromptOptions);
  } catch (err) {
    console.error("❌ 错误:", err);
    process.exit(1);
  }
}

export { generatePrompt, type GeneratePromptOptions };
