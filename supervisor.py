import json
import os
import sys
from datetime import datetime, timedelta

def check_system():
    errors = []
    warnings = []

    # posts.jsonの確認
    try:
        if os.path.exists('posts.json'):
            with open('posts.json', 'r', encoding='utf-8') as f:
                posts = json.load(f)
            
            # 未投稿の投稿が0件の場合
            unposted = [p for p in posts if not p.get("posted")]
            if len(unposted) == 0:
                warnings.append("未投稿の投稿が0件です。writer.pyを実行してください。")
            
            # 24時間以上投稿がない場合
            posted = [p for p in posts if p.get("posted")]
            if posted:
                # 文字列をdatetimeオブジェクトに変換して比較
                last_post = max(posted, key=lambda x: x.get("created_at", ""))
                last_time = datetime.fromisoformat(last_post["created_at"])
                if datetime.now() - last_time > timedelta(hours=24):
                    warnings.append("24時間以上投稿がありません！")
        else:
            errors.append("posts.jsonが見つかりません！")

    except Exception as e:
        errors.append(f"posts.jsonの読み込み中に予期せぬエラーが発生：{e}")

    # research.jsonの確認
    try:
        if os.path.exists('research.json'):
            with open('research.json', 'r', encoding='utf-8') as f:
                research = json.load(f)
            if len(research) < 5:
                warnings.append("ネタが少なくなっています。researcher.pyを実行してください。")
        else:
            warnings.append("research.jsonが見つかりません。researcher.pyを実行してください。")
    except Exception as e:
        warnings.append(f"research.jsonの読み込みエラー：{e}")

    # KILL_SWITCHの確認
    if os.path.exists('KILL_SWITCH'):
        errors.append("KILL_SWITCHが検出されました。処理を中断します。")

    # 結果表示
    print("=== システム スーパーバイザー チェック ===")
    if errors:
        print("\n[ERROR] 致命的な問題：")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("\n[WARNING] 注意事項：")
        for w in warnings:
            print(f"  - {w}")
    
    if not errors and not warnings:
        print("\n[OK] 全てのステータスは良好です。")

    print("\n==========================================")
    
    # エラーがあれば異常終了としてActionsを止める
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    check_system()
    print("チェック完了。処理を続行します。")