/**
 * 调用 Gemini 生成图片
 */

import fs from "node:fs/promises";
import path from "node:path";
import { GeminiClient } from "./lib/gemini-client";

interface GenerateOptions {
  promptFile: string;
  output: string;
  scene?: string;
}

async function generateImage(options: GenerateOptions): Promise<string> {
  console.log(`
╔═══════════════════════════════════════════════════════╗
║   智能图片生成器                                      ║
╚═══════════════════════════════════════════════════════╝
`);

  // 1. 读取提示词
  console.log(`📖 读取提示词: ${options.promptFile}`);
  const prompt = await fs.readFile(options.promptFile, "utf-8");

  if (!prompt || prompt.trim().length === 0) {
    throw new Error("提示词文件为空");
  }

  console.log(`✓ 提示词长度: ${prompt.length} 字符\n`);

  // 2. 解析输出路径，确保使用 images 文件夹
  let outputPath = options.output;

  // 如果输出路径不包含 images 文件夹，自动调整
  if (!outputPath.includes("/images/") && !outputPath.includes("\\images\\")) {
    const dir = path.dirname(outputPath);
    const filename = path.basename(outputPath);

    // 如果在 prompts 文件夹，切换到 images
    if (dir.endsWith("/prompts") || dir.endsWith("\\prompts")) {
      outputPath = path.join(path.dirname(dir), "images", filename);
    } else {
      // 否则在同级创建 images 文件夹
      outputPath = path.join(dir, "images", filename);
    }
  }

  const outputDir = path.dirname(outputPath);
  const filename = path.basename(outputPath);

  console.log(`📂 图片输出目录: ${outputDir}`);
  console.log(`📄 图片文件名: ${filename}\n`);

  // 3. 初始化 Gemini 客户端（自动处理登录）
  const client = new GeminiClient();

  try {
    // 自动检测登录状态，如果需要会打开浏览器
    // 只尝试1次，避免重复打开多个浏览器窗口
    // 单次登录最多等待300秒（5分钟）
    await client.init(1);

    // 4. 生成图片
    console.log("⏳ 正在生成图片，请稍候...\n");
    const output = await client.generateImage(prompt);

    if (!output.images || output.images.length === 0) {
      throw new Error("未生成图片");
    }

    // 5. 保存图片（传入 cookies）
    const image = output.images[0];
    const cookies = client.getCookies();

    console.log(`💾 保存图片到: ${outputPath}`);
    const savedPath = await image.save(outputDir, filename, cookies);

    console.log(`
╔═══════════════════════════════════════════════════════╗
║   ✅ 图片生成成功！                                   ║
╚═══════════════════════════════════════════════════════╝

📁 提示词: ${options.promptFile}
📁 图片:   ${savedPath}
`);

    return savedPath;
  } finally {
    await client.close();
  }
}

/**
 * 获取默认图片输出路径
 * 智能推断：根据提示词文件位置，自动确定图片保存位置
 *
 * 逻辑：
 * - 提示词：.../smart-image-generator-output/prompts/xxx.md
 * - 图片：  .../smart-image-generator-output/images/xxx.png
 */
async function getDefaultImageOutputPath(promptFile: string): Promise<string> {
  // 获取提示词文件的绝对路径
  const promptFileAbs = path.isAbsolute(promptFile)
    ? promptFile
    : path.resolve(process.cwd(), promptFile);

  const promptDir = path.dirname(promptFileAbs);

  // 检查提示词文件是否在 smart-image-generator-output/prompts/ 目录下
  if (
    promptDir.endsWith(path.join("smart-image-generator-output", "prompts"))
  ) {
    // 提示词在标准目录下，图片应该在同级的 images/ 目录
    const baseDir = path.dirname(promptDir); // .../smart-image-generator-output
    const imageDir = path.join(baseDir, "images");

    const promptBasename = path.basename(promptFile, path.extname(promptFile));
    const imageFilename = `${promptBasename}.png`;

    console.log(`📂 使用提示词同目录结构: ${imageDir}`);
    return path.join(imageDir, imageFilename);
  }

  // 提示词不在标准目录下，fallback：在提示词同目录创建 images/
  const imageDir = path.join(
    promptDir,
    "..",
    "smart-image-generator-output",
    "images",
  );
  const promptBasename = path.basename(promptFile, path.extname(promptFile));
  const imageFilename = `${promptBasename}.png`;

  console.log(
    `📂 Fallback：在提示词同级创建 smart-image-generator-output/images/`,
  );
  return path.join(imageDir, imageFilename);
}

// CLI 使用
if (import.meta.main) {
  const args = process.argv.slice(2);

  const options: Partial<GenerateOptions> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === "--prompt-file" || arg === "-p" || arg === "--prompt") {
      options.promptFile = args[++i];
    } else if (arg === "--output" || arg === "-o") {
      options.output = args[++i];
    } else if (arg === "--scene" || arg === "-s") {
      options.scene = args[++i];
    }
  }

  if (!options.promptFile) {
    console.error(`
用法: bun generate-image.ts [选项]

选项:
  -p, --prompt-file <file>  提示词文件路径 (必需)
  -o, --output <file>       输出图片路径 (可选，默认: 项目根目录/smart-image-generator-output/images/)
  -s, --scene <type>        场景类型 (可选)

示例:
  # 使用默认输出路径
  bun generate-image.ts -p prompts/cover-prompt.md
  
  # 指定输出路径
  bun generate-image.ts -p prompts/cover-prompt.md -o images/cover.png
  
  # 默认输出结构：
  # 项目根目录/
  #   smart-image-generator-output/
  #     prompts/    # 提示词文件
  #     images/     # 生成的图片
`);
    process.exit(1);
  }

  // 如果没有指定输出路径，使用默认路径
  if (!options.output) {
    options.output = await getDefaultImageOutputPath(options.promptFile);
    console.log(`📂 使用默认输出路径: ${options.output}`);
  }

  try {
    await generateImage(options as GenerateOptions);
  } catch (err) {
    console.error("❌ 错误:", err);
    process.exit(1);
  }
}

export { generateImage, type GenerateOptions };
