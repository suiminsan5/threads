import os
import subprocess
import sys

def run(script):
    # スクリプトが存在するかチェック
    if not os.path.exists(script):
        print(f"警告：{script} が見つかりません。スキップします。")
        return True # 存在しないだけなら続行、または必要に応じてFalseに

    print(f"\n▶ {script} を実行中...")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True, # encoding='utf-8' の代わりにより一般的な書き方
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

# 順番に実行し、一つでも失敗（False）ならそこで終了する
scripts = [
    "supervisor.py",
    "researcher.py",
    "writer.py",
    "poster.py",
    "analyzer.py",    # 分析も自動化に含める場合
    "get_metrics.py"  # メトリクス取得も自動化に含める場合
]

for script in scripts:
    if not run(script):
        print(f"\n[中止] {script} の失敗によりシステムを停止します。")
        sys.exit(1)

print("\n=== 全ての処理が正常に完了しました！ ===")