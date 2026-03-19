/**
 * 识别输入类型：本地文件 / URL / 直接内容 / 提示词文件
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { load } from 'cheerio';

interface InputResult {
  type: 'local-file' | 'url' | 'direct-content' | 'prompt-file';
  content: string;
  metadata: Record<string, any>;
  path?: string;
}

async function detectInput(input: string): Promise<InputResult> {
  // 1. 检查是否为 URL
  if (input.startsWith('http://') || input.startsWith('https://')) {
    console.log('📡 检测到 URL，正在抓取内容...');
    return await fetchWebContent(input);
  }

  // 2. 检查是否为本地文件
  try {
    const stats = await fs.stat(input);
    if (stats.isFile()) {
      const content = await fs.readFile(input, 'utf-8');
      
      // 检查是否为提示词文件
      if (input.endsWith('-prompt.md')) {
        console.log('📝 检测到提示词文件');
        return {
          type: 'prompt-file',
          content,
          path: input,
          metadata: { promptFile: true },
        };
      }
      
      // 普通文件
      console.log('📄 检测到本地文件');
      return {
        type: 'local-file',
        content,
        path: input,
        metadata: extractFileMetadata(content, input),
      };
    }
  } catch (err) {
    // 不是文件，继续检查
  }

  // 3. 直接内容
  console.log('💬 检测到直接输入内容');
  return {
    type: 'direct-content',
    content: input,
    metadata: {},
  };
}

/**
 * 抓取网页内容
 */
async function fetchWebContent(url: string): Promise<InputResult> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const html = await response.text();
    const $ = load(html);
    
    // 提取元数据
    const title = $('title').text() || $('h1').first().text();
    const description = $('meta[name="description"]').attr('content') || '';
    
    // 提取主要内容（移除脚本和样式）
    $('script, style, nav, footer, header').remove();
    const bodyText = $('body').text().replace(/\s+/g, ' ').trim();
    
    return {
      type: 'url',
      content: bodyText.slice(0, 10000), // 限制长度
      path: url,
      metadata: { title, description, url },
    };
  } catch (err) {
    throw new Error(`无法抓取网页: ${err}`);
  }
}

/**
 * 提取文件元数据
 */
function extractFileMetadata(content: string, filepath: string): Record<string, any> {
  const metadata: Record<string, any> = {
    filename: path.basename(filepath),
    extension: path.extname(filepath),
  };
  
  // 尝试提取 YAML frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (frontmatterMatch) {
    const yamlStr = frontmatterMatch[1];
    // 简单解析（实际应使用 yaml 库）
    for (const line of yamlStr.split('\n')) {
      const [key, ...valueParts] = line.split(':');
      if (key && valueParts.length > 0) {
        metadata[key.trim()] = valueParts.join(':').trim();
      }
    }
  }
  
  // 提取第一个标题作为 title
  const titleMatch = content.match(/^#\s+(.+)$/m);
  if (titleMatch && !metadata.title) {
    metadata.title = titleMatch[1];
  }
  
  return metadata;
}

// CLI 使用
if (import.meta.main) {
  const input = process.argv[2];
  
  if (!input) {
    console.error('用法: bun detect-input.ts <文件路径|URL|内容>');
    process.exit(1);
  }
  
  try {
    const result = await detectInput(input);
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('错误:', err);
    process.exit(1);
  }
}

export { detectInput, type InputResult };
