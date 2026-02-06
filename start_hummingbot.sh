#!/bin/bash
# 启动 Hummingbot 容器

echo "🚀 启动 Hummingbot..."

docker run -it \
  --name hummingbot \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_conf,destination=/conf/" \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_logs,destination=/logs/" \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_data,destination=/data/" \
  --mount "type=bind,source=$(pwd)/hummingbot_files/hummingbot_scripts,destination=/scripts/" \
  hummingbot/hummingbot:latest

echo "✅ Hummingbot 已启动"
