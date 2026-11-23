#!/bin/bash
# nice 第4部バックナンバーの毎晩の自動更新。launchd (com.satsumaimo.nice-reader) から呼ばれる。
#
# 1. build.py が新都社の作者コメントを見て、公開済みの話までの画像と data.json を作る
# 2. 変わったファイルがあればコミットして push する（GitHub Pages が数分で反映）
# 変化が無い日は何もしない。
set -uo pipefail

cd "$(dirname "$0")" || exit 1
mkdir -p logs
LOG="logs/$(date +%Y%m).log"
PY=/Volumes/sat_SSD/manga/nice/nice4/latest/.venv/bin/python
GIT=/usr/bin/git

{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') 開始 ====="
  "$PY" -I build.py || { echo "build.py 失敗 exit=$?"; exit 1; }
  if [ -z "$($GIT status --porcelain -- docs)" ]; then
    echo "変化なし"
    exit 0
  fi
  pub=$("$PY" -I -c 'import json;print(json.load(open("docs/data.json"))["published"])')
  $GIT add -A docs &&
    $GIT commit -q -m "${pub}話まで更新（自動）" &&
    $GIT pull -q --rebase origin main &&
    $GIT push -q origin main &&
    echo "push 済み: ${pub}話まで"
  code=$?
  echo "===== 終了 exit=$code ====="
  exit $code
} >> "$LOG" 2>&1
