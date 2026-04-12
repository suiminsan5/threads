import requests
import json
import os
import sys # sysを追加

# --- ここから修正：シークレット対応と.env読み込みの安全化 ---
TOKEN = os.environ.get('THREADS_TOKEN')

if not TOKEN:
    try:
        # ローカル（自分のPC）でのテスト用
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        TOKEN = os.environ.get('THREADS_TOKEN')
    except FileNotFoundError:
        # GitHub Actions上ではここを通る（エラーにせず続行）
        pass

if not TOKEN:
    print("エラー：THREADS_TOKENが設定されていません。")
    sys.exit(1)
# --- 修正ここまで ---

def get_user_id():
    url = "https://graph.threads.net/v1.0/me"
    params = {
        "access_token": TOKEN,
        "fields": "id,username"
    }
    res = requests.get(url, params=params)
    data = res.json()
    print("ユーザー情報：" + str(data))
    if "id" not in data:
        print("エラー：ユーザーIDが取得できませんでした")
        print("トークンが正しいか確認してください")
        sys.exit(1)
    return data["id"]

def create_post(text, user_id):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    data = {
        "media_type": "TEXT",
        "text": text,
        "access_token": TOKEN
    }
    res = requests.post(url, data=data)
    result = res.json()
    if "id" not in result:
        print("投稿作成エラー：" + str(result))
        sys.exit(1)
    return result["id"]

def publish_post(creation_id, user_id):
    url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    data = {
        "creation_id": creation_id,
        "access_token": TOKEN
    }
    res = requests.post(url, data=data)
    return res.json()

# 投稿データの読み込み
with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

user_id = get_user_id()

for i, post in enumerate(posts):
    if not post["posted"]:
        print("投稿中...")
        creation_id = create_post(post["text"], user_id)
        result = publish_post(creation_id, user_id)
        print("投稿完了：" + str(result))
        posts[i]["posted"] = True
        # 投稿したIDを保存しておくと後の分析が楽になります
        if "id" in result:
            posts[i]["post_id"] = result["id"]
        break

# 状態を保存
with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)