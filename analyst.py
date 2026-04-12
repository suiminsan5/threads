import anthropic
import json
import os
import sys

# --- APIキー取得 ---
api_key = os.environ.get('CLAUDE_API_KEY')

if not api_key:
    print("エラー：CLAUDE_API_KEY が環境変数に見つかりません。")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

def analyze_posts():
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except FileNotFoundError:
        print("posts.jsonが見つかりません。")
        return

    posts_with_metrics = [p for p in posts if p.get("metrics")]

    if not posts_with_metrics:
        print("分析するデータがまだありません。")
        return

    analysis_data = ""
    for p in posts_with_metrics:
        analysis_data += f"\n---\n内容：{p['text']}\n数値：{p['metrics']}\n"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"以下のデータを分析して指示書を作って：\n{analysis_data}"}]
    )

    print("\n=== 分析完了 ===")
    print(message.content[0].text)

if __name__ == "__main__":
    analyze_posts()