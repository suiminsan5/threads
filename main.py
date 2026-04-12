import os
import subprocess
import sys

def run(script):
    print(f"\n▶ {script} を実行中...")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print("エラー：" + result.stderr)
        return False
    return True

print("=== 自動投稿システム開始 ===")

if not run("supervisor.py"):
    print("システムエラーのため停止します。")
    exit(1)

run("researcher.py")
run("writer.py")
run("poster.py")

print("\n=== 完了！ ===")