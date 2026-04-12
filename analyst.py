import anthropic
import json
import os
from datetime import datetime

# APIキーを読み込む
with open('.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

client = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])

def analyze_posts():
    # メトリクスがある投稿だけ取得
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    posts_with_metrics = [p for p in posts if p.get("metrics")]

    if len(posts_with_metrics) < 3:
        print("分析するデータがまだ少ないです。投稿を増やしてから実行してください。")
        return

    # 分析用データを作成
    analysis_data = ""
    for p in posts_with_metrics:
        analysis_data += f"\n---\n投稿文：{p['text']}\n"
        analysis_data += f"views：{p['metrics'].get('views', 0)}\n"
        analysis_data += f"likes：{p['metrics'].get('likes', 0)}\n"
        analysis_data += f"replies：{p['metrics'].get('replies', 0)}\n"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""以下のThreads投稿データを分析してください。

{analysis_data}

分析してほしいこと：
- どんな投稿が伸びているか
- どんな投稿が伸びていないか
- 次の投稿でどんな内容・形式を増やすべきか
- 避けるべき内容・形式は何か

結果をwriter.pyへの指示書として出力してください。"""
            }
        ]
    )

    feedback = message.content[0].text
    print("分析結果：")
    print(feedback)

    # フィードバックをファイルに保存
    with open('feedback.txt', 'w', encoding='utf-8') as f:
        f.write(feedback)

    print("\nfeedback.txtに保存しました！")

analyze_posts()