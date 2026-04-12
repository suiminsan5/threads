import anthropic
import json
import os
import random
import sys
from datetime import datetime, timedelta

with open('.env') as f:
    for line in f:
        key, value = line.strip().split('=', 1)
        os.environ[key] = value

client = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])

PATTERNS = [
    "短文完結・暴露系",
    "短文完結・需要確認型",
    "短文完結・共感型",
    "リスト系・チェックリスト型",
    "リスト系・ランキング型",
    "リスト系・比較型",
    "コメント誘導型・質問型",
    "コメント誘導型・共感募集型",
    "コメント誘導型・投票型",
    "ツリー展開型・続きが気になる型",
    "ツリー展開型・段階解説型",
    "暴露系・業界の裏側型",
    "暴露系・失敗談型",
    "需要確認型・あるある型",
    "需要確認型・悩み提起型",
]

# 冒頭パターン10種類
OPENING_PATTERNS = [
    "自己紹介系（属性を語りターゲットに共感を生む）",
    "数字を入れる系（納得感と期待感を高める）",
    "続きが気になる系（「ここだけの話」などで好奇心を刺激する）",
    "専門性アピール系（誰が言っているかの信憑性を高める）",
    "限定公開系（緊急性を演出して保存を促す）",
    "逆張り系（常識の逆を行き目を引く）",
    "面白悪口系（自虐やあるあるで親近感を持たせる）",
    "トレンド系（季節のイベントや話題に絡める）",
    "あるある系（強い共感でフォローを増やす）",
    "断言系（緊急性や重要性を強調する）",
]

FIRST_LINE_TOPIC_PAIRS = [
    ("『 繊細さんに告白します 』", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("『 HSPの人だけ読んでほしい 』", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("『 これ知らないと損する 』", "繊細さん（HSP）への転職アドバイス（面接に関する内容は絶対に含めない）"),
    ("『 繊細さんが転職で失敗する理由、わかった 』", "繊細さん（HSP）への転職アドバイス（面接に関する内容は絶対に含めない）"),
    ("『 正直に言います 』", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("『 繊細さんあるある、言っていい？ 』", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("『 職場でこれやってる人、要注意 』", "職場にいる要注意人物の特徴と対処法。高圧的な人・フレネミー・お局など1つ取り上げる"),
    ("『 転職前に絶対確認してほしいこと 』", "繊細さん（HSP）が転職するとき重視したほうがいいこと。チェック項目形式で書く"),
    ("『 繊細さんが疲れる本当の理由 』", "繊細さん（HSP）の体力温存方法。日常で使える具体的な方法を1つ取り上げて書く"),
    ("『 これ共感する人いる？ 』", "繊細さん（HSP）の仕事・転職・メンタルに関する内容で自由に作成"),
    ("『 繊細さんに向いてる職場の特徴 』", "繊細さん（HSP）が転職するとき重視したほうがいいこと。チェック項目形式で書く"),
    ("『 HSPが絶対避けるべき職場の特徴 』", "繊細さん（HSP）が転職するとき重視したほうがいいこと。チェック項目形式で書く"),
    ("『 繊細さんの体力温存術、教えます 』", "繊細さん（HSP）の体力温存方法。日常で使える具体的な方法を1つ取り上げて書く"),
    ("『 メンタルが限界のとき、試してほしいこと 』", "繊細さん（HSP）のメンタル回復方法。弱ったときに使える具体的な方法を1つ書く"),
    ("『 繊細さんが仕事で消耗しやすい場面 』", "繊細さん（HSP）の体力温存方法。日常で使える具体的な方法を1つ取り上げて書く"),
    ("『 転職エージェントが言わないこと 』", "繊細さん（HSP）への転職アドバイス（面接に関する内容は絶対に含めない）"),
    ("『 職場のあの人、こう対処してます 』", "職場にいる要注意人物の特徴と対処法。高圧的な人・フレネミー・お局など1つ取り上げる"),
    ("『 繊細さんが自分を守る方法 』", "繊細さん（HSP）の体力温存方法。日常で使える具体的な方法を1つ取り上げて書く"),
    ("『 HSPが転職で重視すべきこと 』", "繊細さん（HSP）が転職するとき重視したほうがいいこと。チェック項目形式で書く"),
    ("『 これ言ってる職場、逃げてOK 』", "職場にいる要注意人物の特徴と対処法。高圧的な人・フレネミー・お局など1つ取り上げる"),
]

def get_recent_patterns():
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
            recent = posts[-3:]
            return [p.get("pattern", "") for p in recent]
    except:
        return []

def is_list_pattern(pattern):
    return "リスト系" in pattern

def generate_post(pattern, opening_pattern, first_line, topic, past_posts):
    past_text = ""
    if past_posts:
        past_text = "\n\n過去の投稿（これらと似た内容にしないこと）:\n"
        for i, p in enumerate(past_posts):
            past_text += f"\n--- 過去{i+1} ---\n{p}\n"

    list_rule = ""
    if is_list_pattern(pattern):
        list_rule = "- リスト形式の場合、各項目は✅で始めること\n"
        list_rule += "- リストを全部出力したあとに、各項目の説明を「・〇〇 → 説明文」の形式で追記すること\n"
        list_rule += "- 投稿は必ず300文字以内に収めること\n"
    else:
        list_rule = "- 200文字以内\n"

    prompt = "以下の条件でThreadsの投稿文を1つ作成してください。\n\n"
    prompt += "【投稿パターン】" + pattern + "\n"
    prompt += "【冒頭パターン】" + opening_pattern + "\n"
    prompt += "【1行目】必ず以下の書き出しで始めること（この文字列をそのまま1行目に使うこと）：" + first_line + "\n"
    prompt += "【トピック】" + topic + "\n"
    prompt += "【重要】1行目のタイトルと投稿内容を必ず一致させること\n\n"
    prompt += "条件：\n"
    prompt += list_rule
    prompt += "- HSPや繊細さんが共感できる内容\n"
    prompt += "- 具体的で実用的な内容\n"
    prompt += "- 読みやすい改行\n"
    prompt += "- 語尾の連続がないか確認すること（例：〜です。〜です。〜です。はNG）\n"
    prompt += "- 主語と述語のねじれがないか確認すること\n"
    prompt += "- 専門用語を多用しないこと\n"
    prompt += "- 最後にハッシュタグを必ず3つ、全て#から始める（例：#HSP #繊細さん #転職）\n"
    prompt += "- ハッシュタグは必ず#記号をつけること。#が抜けたタグは絶対に書かない\n"
    prompt += "- *や**のような記号は絶対に使わない\n"
    prompt += "- マークダウン記法は一切使わない\n"
    prompt += "- 面接で発言する系の内容は絶対に入れない\n"
    prompt += "- 自然な日本語でAIっぽくない表現にする\n"
    prompt += "- !や?は全角（！や？）を使う\n"
    prompt += "- 🍀などの四つ葉クローバーの絵文字は絶対に使わない\n"
    prompt += "- 過去の投稿と内容が被らないようにする\n"
    prompt += "- チェックリスト形式の場合、実際に求人票・口コミサイト・会社HPで確認できる項目のみにする\n"
    prompt += past_text + "\n"
    prompt += "投稿文だけを出力してください。"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def score_post(post, first_line):
    prompt = "以下のThreads投稿を10項目で採点してください。\n\n"
    prompt += "1行目：" + first_line + "\n"
    prompt += "投稿文：\n" + post + "\n\n"
    prompt += "採点項目（各10点満点）：\n"
    prompt += "1. フックの強さ（1行目で引きつけられるか）\n"
    prompt += "2. 有益性（読んで役に立つか）\n"
    prompt += "3. 具体性（具体的な内容か）\n"
    prompt += "4. テンポ感（読みやすいか）\n"
    prompt += "5. ペルソナ一致度（HSP・繊細さんに刺さるか）\n"
    prompt += "6. 共感度（共感できるか）\n"
    prompt += "7. 独自性（ありきたりでないか）\n"
    prompt += "8. 自然さ（AIっぽくないか）\n"
    prompt += "9. 行動喚起（いいねやコメントしたくなるか）\n"
    prompt += "10. 1行目と内容の一致度（タイトルと本文が合っているか）\n\n"
    prompt += "合計点と平均点だけを以下の形式で出力してください。\n"
    prompt += "平均点:X.X"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text
    try:
        score = float(result.split("平均点:")[1].strip())
    except:
        score = 7.0
    return score

# 過去の投稿を読み込む
past_posts = []
try:
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
        past_posts = [p["text"] for p in posts[-10:]]
except:
    pass

# パターン・冒頭パターン・1行目・トピックを選択
recent_patterns = get_recent_patterns()
available_patterns = [p for p in PATTERNS if p not in recent_patterns]
if not available_patterns:
    available_patterns = PATTERNS
pattern = random.choice(available_patterns)
opening_pattern = random.choice(OPENING_PATTERNS)
first_line, topic = random.choice(FIRST_LINE_TOPIC_PAIRS)

print("今回のパターン：" + pattern)
print("今回の冒頭パターン：" + opening_pattern[:20] + "...")
print("今回の1行目：" + first_line)
print("今回のトピック：" + topic[:30] + "...")

# 投稿生成ループ（最大3回試行）
max_attempts = 3
final_post = None
final_score = 0

for attempt in range(max_attempts):
    print(f"\n生成試行 {attempt + 1}/{max_attempts}")
    post = generate_post(pattern, opening_pattern, first_line, topic, past_posts)
    post = post.replace("**", "")
    post = post.replace("!", "！").replace("?", "？")

    # 1行目を強制的に置き換え
    lines = post.strip().split('\n')
    lines[0] = first_line
    post = '\n'.join(lines)

    # ハッシュタグの#抜けを修正
    lines = post.strip().split('\n')
    fixed_lines = []
    for line in lines:
        if line.strip() and not line.startswith('#') and not line.startswith('『'):
            words = line.split()
            if any(w.startswith('#') for w in words):
                fixed_words = []
                for w in words:
                    if not w.startswith('#') and len(w) > 1:
                        w = '#' + w
                    fixed_words.append(w)
                line = ' '.join(fixed_words)
        fixed_lines.append(line)
    post = '\n'.join(fixed_lines)

    # 自己採点
    print("採点中...")
    score = score_post(post, first_line)
    print(f"スコア：{score}/10")

    if score >= 7.0:
        print("合格！投稿をキューに追加します。")
        final_post = post
        final_score = score
        break
    elif attempt < max_attempts - 1:
        print(f"スコアが低いため書き直します。（{score}/10）")
    else:
        print("3回試行しましたが基準に達しませんでした。今回は棄却します。")
        sys.exit(0)

print("\n生成された投稿：")
sys.stdout.buffer.write((final_post + "\n").encode('utf-8'))

# 保存処理（2週間以上前のデータを削除するロジックを追加）
posts_data = []
try:
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
except:
    pass

# 新しい投稿を追加
posts_data.append({
    "text": final_post,
    "pattern": pattern,
    "opening_pattern": opening_pattern,
    "score": final_score,
    "created_at": datetime.now().isoformat(),
    "posted": False
})

# 現在から14日（2週間）前の日時を取得
two_weeks_ago = datetime.now() - timedelta(days=14)

# 2週間以内のデータのみを抽出してリストを更新
posts_data = [
    p for p in posts_data 
    if datetime.fromisoformat(p["created_at"]) > two_weeks_ago
]

with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=2)

print("2週間以上前のデータを整理し、posts.jsonに保存しました！")