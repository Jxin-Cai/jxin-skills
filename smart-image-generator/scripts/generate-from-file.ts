#!/usr/bin/env bun
/**
 * 从文件生成提示词的辅助脚本
 */

import { readFile } from "node:fs/promises";
import { generatePrompt, type GeneratePromptOptions } from "./generate-prompt";

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 4) {
    console.error(`
用法: bun generate-from-file.ts <input-file> <scene> <style> <output-file>

示例:
  bun generate-from-file.ts temp-bmad-flow.md flowchart obsidian output/prompts/bmad-prompt.md
`);
    process.exit(1);
  }

  const [inputFile, scene, style, outputFile] = args;

  try {
    // 读取输入文件
    const content = await readFile(inputFile, "utf-8");

    // 提取 frontmatter 中的 metadata
    let metadata: Record<string, any> = {};
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (frontmatterMatch) {
      const yaml = frontmatterMatch[1];
      yaml.split("\n").forEach((line) => {
        const match = line.match(/^(\w+):\s*(.+)$/);
        if (match) {
          metadata[match[1]] = match[2].trim();
        }
      });
    }

    // 生成提示词
    const options: GeneratePromptOptions = {
      scene,
      style,
      content,
      output: outputFile,
      metadata,
    };

    await generatePrompt(options);
    console.log("✅ 成功!");
  } catch (error) {
    console.error("❌ 错误:", error);
    process.exit(1);
  }
}

if (import.meta.main) {
  main();
}
