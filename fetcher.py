import requests
import json
import os
import sys # sysを追加
from datetime import datetime

# --- ここから修正：シークレット(Threadsトークン)対応 ---
TOKEN = os.environ.get('THREADS_TOKEN')

if not TOKEN:
    # ローカル（自分のPC）用の予備
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
    print("THREADS_TOKENが設定されていません。")
    sys.exit(1)
# --- 修正ここまで ---

def get_user_id():
    url = "https://graph.threads.net/v1.0/me"
    params = {"access_token": TOKEN}
    res = requests.get(url, params=params)
    return res.json()["id"]

def get_metrics(post_id):
    url = f"https://graph.threads.net/v1.0/{post_id}/insights"
    params = {
        "metric": "views,likes,replies,reposts,quotes",
        "access_token": TOKEN
    }
    res = requests.get(url, params=params)
    data = res.json()
    metrics = {}
    if "data" in data:
        for item in data["data"]:
            metrics[item["name"]] = item["values"][0]["value"]
    return metrics

# 投稿済みの投稿のメトリクスを取得
with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

updated = False
for i, post in enumerate(posts):
    if post.get("posted") and post.get("post_id") and not post.get("metrics"):
        print(f"メトリクス取得中：{post['text'][:30]}...")
        metrics = get_metrics(post["post_id"])
        posts[i]["metrics"] = metrics
        print(f"取得完了：{metrics}")
        updated = True

if updated:
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print("\nメトリクスをposts.jsonに保存しました！")
else:
    print("取得するメトリクスがありませんでした。")