import requests
import json
import os
import sys
import time

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
    params = {"access_token": TOKEN, "fields": "id"}
    res = requests.get(url, params=params)
    return res.json()["id"]

def create_container(text, user_id, reply_to_id=None):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    # payloadではなくparamsで送ることで確実にAPIに認識させます
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": TOKEN
    }
    # 返信の場合、公開済みの「親投稿のID」をreply_toに指定
    if reply_to_id:
        params["reply_to"] = reply_to_id
        
    res = requests.post(url, params=params)
    result = res.json()
    if "id" not in result:
        print(f"コンテナ作成失敗: {result}")
        sys.exit(1)
    return result["id"]

def publish_container(creation_id, user_id):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    params = {
        "creation_id": creation_id,
        "access_token": TOKEN
    }
    res = requests.post(url, params=params)
    result = res.json()
    if "id" not in result:
        print(f"公開失敗: {result}")
        sys.exit(1)
    return result["id"] # 公開後の「投稿ID」を返す

def main():
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except FileNotFoundError:
        print("posts.jsonが見つかりません。")
        return

    user_id = get_user_id()

    for i, post in enumerate(posts):
        if not post.get("posted"):
            print("=== スレッド投稿開始 ===")
            
            # 1. 親投稿のコンテナ作成
            p_container_id = create_container(post["parent_text"], user_id)
            
            # 2. 親投稿を公開し、「投稿ID」を取得
            parent_post_id = publish_container(p_container_id, user_id)
            print(f"親投稿公開完了 ID: {parent_post_id}")

            # 3. 確実にスレッド化させるための待機（重要）
            time.sleep(5)

            # 4. 返信投稿のコンテナ作成
            # 【ここが変更点】reply_to に「公開後の親投稿ID」を渡す
            r_container_id = create_container(post["reply_text"], user_id, reply_to_id=parent_post_id)
            
            # 5. 返信投稿を公開
            publish_container(r_container_id, user_id)
            print("返信（スレッド）公開完了")
            
            posts[i]["posted"] = True
            break

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()