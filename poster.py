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
    params = {"access_token": TOKEN, "fields": "id"}
    res = requests.get(url, params=params)
    return res.json()["id"]

def create_post(text, user_id):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": TOKEN
    }
    res = requests.post(url, params=params)
    result = res.json()
    if "id" not in result:
        print(f"作成失敗: {result}")
        sys.exit(1)
    return result["id"]

def publish_post(creation_id, user_id):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    params = {
        "creation_id": creation_id,
        "access_token": TOKEN
    }
    res = requests.post(url, params=params)
    return res.json()

def main():
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except FileNotFoundError:
        return

    user_id = get_user_id()

    for i, post in enumerate(posts):
        if not post.get("posted"):
            print("投稿を開始します...")
            creation_id = create_post(post["text"], user_id)
            publish_post(creation_id, user_id)
            print("投稿完了")
            
            posts[i]["posted"] = True
            break

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()