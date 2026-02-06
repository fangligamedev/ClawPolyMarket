#!/bin/bash
# 停止 Hummingbot 容器

echo "🛑 停止 Hummingbot..."
docker stop hummingbot
docker rm hummingbot
echo "✅ Hummingbot 已停止"
