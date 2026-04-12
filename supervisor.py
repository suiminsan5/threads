import json
import os
import sys
from datetime import datetime, timedelta

def check_system():
    errors = []
    warnings = []

    # posts.jsonの確認
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
        
        # 未投稿の投稿が0件の場合
        unposted = [p for p in posts if not p.get("posted")]
        if len(unposted) == 0:
            warnings.append("未投稿の投稿が0件です。writer.pyを実行してください。")
        
        # 24時間以上投稿がない場合
        posted = [p for p in posts if p.get("posted")]
        if posted:
            last_post = max(posted, key=lambda x: x.get("created_at", ""))
            last_time = datetime.fromisoformat(last_post["created_at"])
            if datetime.now() - last_time > timedelta(hours=24):
                warnings.append("24時間以上投稿がありません！")

    except FileNotFoundError:
        errors.append("posts.jsonが見つかりません！")
    except Exception as e:
        errors.append(f"posts.jsonの読み込みエラー：{e}")

    # research.jsonの確認
    try:
        with open('research.json', 'r', encoding='utf-8') as f:
            research = json.load(f)
        if len(research) < 5:
            warnings.append("ネタが少なくなっています。researcher.pyを実行してください。")
    except FileNotFoundError:
        warnings.append("research.jsonが見つかりません。researcher.pyを実行してください。")

    # KILL_SWITCHの確認
    if os.path.exists('KILL_SWITCH'):
        errors.append("KILL_SWITCHが有効です！投稿を停止します。")
        sys.exit(1)

    # 結果表示
    print("=== スーパーバイザー チェック結果 ===")
    if errors:
        print("\n[ERROR]：")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("\n[WARNING]：")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("\n[OK] 全て正常です！")

    print("\n=====================================")
    
    # エラーがあれば終了
    if errors:
        sys.exit(1)

check_system()
print("システム正常。処理を続行します。")