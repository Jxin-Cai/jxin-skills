#!/usr/bin/env bun
/**
 * 清除登录状态脚本
 *
 * 功能：
 * - 删除保存的cookies文件
 * - 清除Chrome profile数据
 * - 下次使用时会自动弹出浏览器重新登录
 *
 * 使用方法：
 *   bun scripts/logout.ts
 *   或
 *   bun scripts/logout.ts --verbose
 */

import fs from "node:fs/promises";
import fss from "node:fs";
import path from "node:path";
import { homedir } from "node:os";

// 配置路径（与 gemini-client.ts 保持一致）
const CONFIG_DIR = path.join(homedir(), ".local/share/smart-image-generator");
const COOKIE_PATH = path.join(CONFIG_DIR, "cookies.txt");
const PROFILE_DIR = path.join(CONFIG_DIR, "chrome-profile");

interface LogoutOptions {
  verbose?: boolean;
}

/**
 * 清除登录状态
 */
async function logout(options: LogoutOptions = {}): Promise<void> {
  const { verbose = false } = options;

  console.log("🔐 正在清除登录状态...\n");

  let clearedCount = 0;
  const results: { item: string; status: string }[] = [];

  // 1. 删除 cookies 文件
  try {
    const cookieExists = fss.existsSync(COOKIE_PATH);
    if (cookieExists) {
      await fs.unlink(COOKIE_PATH);
      results.push({ item: "Cookies文件", status: "✅ 已删除" });
      clearedCount++;
      if (verbose) {
        console.log(`✅ 已删除 Cookies: ${COOKIE_PATH}`);
      }
    } else {
      results.push({ item: "Cookies文件", status: "ℹ️  不存在" });
      if (verbose) {
        console.log(`ℹ️  Cookies文件不存在: ${COOKIE_PATH}`);
      }
    }
  } catch (error) {
    results.push({ item: "Cookies文件", status: "❌ 删除失败" });
    if (verbose) {
      console.error(`❌ 删除Cookies失败: ${error}`);
    }
  }

  // 2. 清除 Chrome profile 目录
  try {
    const profileExists = fss.existsSync(PROFILE_DIR);
    if (profileExists) {
      await fs.rm(PROFILE_DIR, { recursive: true, force: true });
      results.push({ item: "Chrome Profile", status: "✅ 已清除" });
      clearedCount++;
      if (verbose) {
        console.log(`✅ 已清除 Chrome Profile: ${PROFILE_DIR}`);
      }
    } else {
      results.push({ item: "Chrome Profile", status: "ℹ️  不存在" });
      if (verbose) {
        console.log(`ℹ️  Chrome Profile目录不存在: ${PROFILE_DIR}`);
      }
    }
  } catch (error) {
    results.push({ item: "Chrome Profile", status: "❌ 清除失败" });
    if (verbose) {
      console.error(`❌ 清除Chrome Profile失败: ${error}`);
    }
  }

  // 3. 输出结果摘要
  console.log("═".repeat(60));
  console.log("清除结果：");
  console.log("═".repeat(60));

  for (const { item, status } of results) {
    console.log(`${item.padEnd(20)} ${status}`);
  }

  console.log("═".repeat(60));

  if (clearedCount > 0) {
    console.log("\n✅ 登录状态已清除");
    console.log("\n💡 下次使用时会自动弹出浏览器重新登录");
  } else {
    console.log("\nℹ️  没有需要清除的登录数据");
  }

  console.log(`\n📍 配置目录: ${CONFIG_DIR}`);
}

/**
 * 检查登录状态
 */
async function checkLoginStatus(): Promise<void> {
  console.log("🔍 检查登录状态...\n");

  const cookieExists = fss.existsSync(COOKIE_PATH);
  const profileExists = fss.existsSync(PROFILE_DIR);

  console.log("═".repeat(60));
  console.log("当前登录状态：");
  console.log("═".repeat(60));

  console.log(`Cookies文件:      ${cookieExists ? "✅ 存在" : "❌ 不存在"}`);
  console.log(`Chrome Profile:  ${profileExists ? "✅ 存在" : "❌ 不存在"}`);

  console.log("═".repeat(60));

  if (cookieExists || profileExists) {
    console.log("\n✅ 已登录（有保存的登录状态）");
    console.log("\n💡 提示：");
    console.log("   - 如需换号，运行: bun scripts/logout.ts");
    console.log("   - 清除后会自动重新登录");
  } else {
    console.log("\n❌ 未登录（无保存的登录状态）");
    console.log("\n💡 提示：");
    console.log("   - 首次使用时会自动打开浏览器");
    console.log("   - 在浏览器中登录Google账号即可");
  }

  console.log(`\n📍 配置目录: ${CONFIG_DIR}`);
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose") || args.includes("-v");
  const checkOnly = args.includes("--check") || args.includes("-c");
  const help = args.includes("--help") || args.includes("-h");

  if (help) {
    console.log(`
使用方法：
  bun scripts/logout.ts [选项]

选项：
  --check, -c      仅检查登录状态，不清除
  --verbose, -v    显示详细输出
  --help, -h       显示此帮助信息

示例：
  bun scripts/logout.ts               # 清除登录状态
  bun scripts/logout.ts --check       # 检查登录状态
  bun scripts/logout.ts --verbose     # 详细输出
`);
    return;
  }

  if (checkOnly) {
    await checkLoginStatus();
  } else {
    await logout({ verbose });
  }
}

main().catch((error) => {
  console.error("❌ 错误:", error);
  process.exit(1);
});
