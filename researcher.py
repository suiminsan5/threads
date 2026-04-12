import requests
import json
import os
from datetime import datetime

# APIキーを読み込む
with open('.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']

# 検索キーワード一覧
KEYWORDS = [
    "HSP 転職",
    "繊細さん 仕事",
    "HSP 職場 人間関係",
    "繊細さん 転職 アドバイス",
    "HSP 疲れ 仕事",
    "繊細さん メンタル 回復",
    "HSP 向いてる仕事",
    "職場 高圧的な人 対処",
    "フレネミー 職場",
    "HSP 体力温存"
]

def search_youtube(keyword):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": 3,
        "order": "relevance",
        "key": YOUTUBE_API_KEY
    }
    res = requests.get(url, params=params)
    data = res.json()
    
    results = []
    if "items" in data:
        for item in data["items"]:
            results.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "keyword": keyword
            })
    return results

# 全キーワードで検索
print("YouTubeからネタを収集中...")
all_results = []
for keyword in KEYWORDS:
    print(f"検索中：{keyword}")
    results = search_youtube(keyword)
    all_results.extend(results)

# 結果をJSONに保存
with open('research.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n{len(all_results)}件のネタを収集しました！")
print("research.jsonに保存しました！")