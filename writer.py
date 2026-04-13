import anthropic
import json
import os
import random
import sys
from datetime import datetime, timedelta

# --- APIキー・シークレット対応 ---
api_key = os.environ.get('CLAUDE_API_KEY')

if not api_key:
    try:
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        api_key = os.environ.get('CLAUDE_API_KEY')
    except FileNotFoundError:
        pass

if not api_key:
    print("APIキーが設定されていません。")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

# モデル名を固定
MODEL_NAME = "claude-sonnet-4-6"

# --- 定数定義 ---
HOOK_STRATEGIES = [
    "共感・悩み型（読者の「これ私だ」を突く）",
    "ベネフィット型（数字や得られる未来を見せる）",
    "常識否定型（当たり前を疑わせて足を止める）",
    "ストーリー型（ビフォーアフターで期待させる）",
    "権威性・希少性型（損をしたくない心理を突く）",
    "結論・要約型（タイパ重視層に刺す）"
]

FIRST_LINE_TOPIC_PAIRS = [
    ("繊細さんに告白します。", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("正直に言います。", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("繊細さんあるある、言っていい？", "繊細さん（HSP）の仕事・転職・メンタルに関するあるあるの内容で自由に作成"),
    ("これ知らないと損する！", "繊細さん（HSP）のため就活アドバイス（面接に関する内容は絶対に含めない）"),
    ("転職前に絶対確認してほしいこと。", "繊細さん（HSP）が転職するとき確認したほうがいいこと。チェック項目形式で書く"),
    ("繊細さんが疲れる本当の理由", "繊細さん（HSP）の悩み。日常で疲れる具体的な原因を1つ取り上げて書く"),
    ("これ共感する人いる？", "繊細さん（HSP）が共感しそうな仕事・転職・メンタルに関する内容で自由に作成"),
    ("【 繊細さんに向いてる職場の特徴 】", "繊細さんに向いてる職場の特徴。チェック項目形式で書く"),
    ("【 HSPが絶対避けるべき職場の特徴 】", "繊細さん（HSP）が転職するとき避けるべき職場の特徴。チェック項目形式で書く"),
    ("メンタルが限界のとき、試してほしいこと", "繊細さん（HSP）のメンタル回復方法。弱ったときに使える具体的な方法を1つ書く"),
    ("【 繊細さんが仕事で消耗しやすい場面 】", "繊細さん（HSP）の消耗しやすい場面での悩み。具体的な場面を1つ取り上げて書く"),
    ("転職エージェントが言わないこと", "転職エージェントが言わないことを暴露"),
    ("【 繊細さんが自分を守る方法 】", "繊細さん（HSP）の具体的な防衛術。具体的な方法を1つ書く"),
    ("【 HSPが転職で重視すべきこと 】", "繊細さん（HSP）が転職するとき重視したほうがいいこと。チェック項目形式で書く"),
    ("こんな人がいる職場、逃げて。", "職場にいる要注意人物の特徴と対処法。高圧的な人・フレネミー・お局・不衛生な人など1つ取り上げる"),
]

def generate_post(hook_strategy, first_line, topic):
    # あなたの立場を定義する指示をプロンプトに追加しました
    prompt = f"""以下の条件でThreadsの投稿文を1つ作成してください。

【あなたの立場：絶対に厳守すること】
- あなたは「HSP（繊細さん）」の当事者です。
- 「就職支援をしてきた」「プロのアドバイザーである」といった経歴詐称は絶対にしないでください。
- あくまで「自分もHSPで悩んできたから気持ちがわかる」「周りにHSPの友達が多くて、彼らの悩みを身近に感じている」という等身大の立場で書いてください。
- 偉そうな指導ではなく、同じ目線の「共感」や「気づき」をベースにしてください。

【戦略】noteの知見に基づいた以下のフック戦略を使用：{hook_strategy}
【1行目】必ずこの書き出しで始める：{first_line}
【トピック】{topic}

条件：
- 1つの投稿で完結させること。
- 1行目は指定された通りに始める。
- noteのテクニックを使い、最初の2〜3行で強烈に興味を引くこと。
- 文字数は全体で230文字以内。
- 絵文字は ✅ 以外使わない。
- 読みやすい改行を入れる。
- 自然な日本語。
- 最後にハッシュタグを4つ。

投稿文だけを出力してください。"""

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# --- メイン処理 ---
hook_strategy = random.choice(HOOK_STRATEGIES)
first_line, topic = random.choice(FIRST_LINE_TOPIC_PAIRS)

print(f"戦略: {hook_strategy}")
post_text = generate_post(hook_strategy, first_line, topic)

# 文字の微調整
post_text = post_text.replace("**", "").replace("＃", "#").replace("!", "！").replace("?", "？")

posts_data = []
try:
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
except:
    pass

posts_data.append({
    "text": post_text,
    "created_at": datetime.now().isoformat(),
    "posted": False
})

with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=2)

print("\n=== 生成完了 ===")
print(post_text)