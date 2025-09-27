#!/bin/bash

# Fortinet PSIRT Translate - Deploy Demo to GitHub Pages
# This script builds and prepares the demo for GitHub Pages deployment

set -e

echo "🚀 開始部署 Fortinet PSIRT 翻譯器演示版本到 GitHub Pages"

# 確保在專案根目錄
cd "$(dirname "$0")"

echo "📦 複製示例數據到前端..."
cp data/advisories.json frontend/public/data/

echo "🔨 建置前端應用..."
cd frontend
npm ci
npm run build

echo "✅ 建置完成！"
echo ""
echo "📋 部署說明："
echo "1. 將 frontend/dist 目錄的內容推送到 GitHub Pages"
echo "2. 或使用 GitHub Actions 自動部署（已配置）"
echo ""
echo "🌐 演示地址：https://your-username.github.io/fortinet-psirt-translate/"
echo ""
echo "📁 建置輸出位於：frontend/dist/"
