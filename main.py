import os
import subprocess
import sys

def run(script):
    if not os.path.exists(script):
        print(f"警告：{script} が見つかりません。スキップします。")
        return True

    print(f"\n▶ {script} を実行中...")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True,
        errors='replace'
    )
    
    if result.stdout:
        print(result.stdout)
        
    if result.returncode != 0:
        print(f"【！】{script} でエラーが発生しました。")
        if result.stderr:
            print("エラー詳細：" + result.stderr)
        return False
    return True

print("=== 自動投稿システム開始 ===")

scripts = [
    "supervisor.py",
    "researcher.py",
    "fetcher.py",
    "analyst.py",
    "writer.py",
    "poster.py"
]

for script in scripts:
    if not run(script):
        print(f"\n[中止] {script} の失敗によりシステムを停止します。")
        sys.exit(1)

print("\n=== 全ての処理が正常に完了しました！ ===")