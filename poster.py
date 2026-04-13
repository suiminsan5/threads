import requests
import json
import os
import sys

# --- シークレット対応 ---
TOKEN = os.environ.get('THREADS_TOKEN')

if not TOKEN:
    try:
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        TOKEN = os.environ.get('THREADS_TOKEN')
    except FileNotFoundError:
        pass

if not TOKEN:
    print("エラー：THREADS_TOKENが設定されていません。")
    sys.exit(1)

def get_user_id():
    url = "https://graph.threads.net/v1.0/me"
    params = {"access_token": TOKEN, "fields": "id,username"}
    res = requests.get(url, params=params)
    data = res.json()
    if "id" not in data:
        print("エラー：ユーザーID取得失敗")
        sys.exit(1)
    return data["id"]

def create_post(text, user_id, reply_to_id=None):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    data = {
        "media_type": "TEXT",
        "text": text,
        "access_token": TOKEN
    }
    # 返信（スレッド）の場合は、親のIDをセットする
    if reply_to_id:
        data["reply_to"] = reply_to_id
        
    res = requests.post(url, data=data)
    result = res.json()
    if "id" not in result:
        print(f"投稿作成エラー：{result}")
        sys.exit(1)
    return result["id"]

def publish_post(creation_id, user_id):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    data = {"creation_id": creation_id, "access_token": TOKEN}
    res = requests.post(url, data=data)
    return res.json()

# 投稿データの読み込み
with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

user_id = get_user_id()

for i, post in enumerate(posts):
    # postedがFalseのものを1セット（親＋返信）だけ処理する
    if not post.get("posted"):
        print("スレッド投稿を開始します...")
        
        # 1. 親投稿（1枚目）の作成
        print("親投稿を作成中...")
        parent_creation_id = create_post(post["parent_text"], user_id)
        parent_result = publish_post(parent_creation_id, user_id)
        parent_post_id = parent_result.get("id")
        
        if not parent_post_id:
            print(f"親投稿の公開に失敗しました：{parent_result}")
            break
            
        print(f"親投稿完了。ID: {parent_post_id}")

        # 2. 返信投稿（2枚目）をスレッドとして作成
        print("返信投稿（スレッド）を作成中...")
        reply_creation_id = create_post(post["reply_text"], user_id, reply_to_id=parent_post_id)
        reply_result = publish_post(reply_creation_id, user_id)
        
        print(f"返信投稿完了：{reply_result}")
        
        # 状態更新
        posts[i]["posted"] = True
        posts[i]["parent_post_id"] = parent_post_id
        break

# 状態を保存
with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print("\n=== 全ての処理が完了しました ===")