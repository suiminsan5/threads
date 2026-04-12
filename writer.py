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

# モデル名を指定通りに固定
MODEL_NAME = "claude-sonnet-4-6"

# --- 定数定義 ---
PATTERNS = [
    "短文完結・暴露系", "短文完結・需要確認型", "短文完結・共感型",
    "リスト系・チェックリスト型", "リスト系・ランキング型", "リスト系・比較型",
    "コメント誘導型・質問型", "コメント誘導型・共感募集型", "コメント誘導型・投票型",
    "ツリー展開型・段階解説型", # ツリー展開型でも1投稿完結を促す
    "暴露系・業界の裏側型", "暴露系・失敗談型", "需要確認型・あるある型", "需要確認型・悩み提起型",
]

OPENING_PATTERNS = [
    "自己紹介系（属性を語りターゲットに共感を生む）",
    "数字を入れる系（納得感と期待感を高める）",
    "続きが気になる系（「ここだけの話」などで好奇心を刺激する）",
    "専門性アピール系（誰が言っているかなど信憑性を高める）",
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

def get_recent_data():
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
            recent = posts[-3:]
            return {
                "patterns": [p.get("pattern", "") for p in recent],
                "openings": [p.get("opening_pattern", "") for p in recent]
            }
    except:
        return {"patterns": [], "openings": []}

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
        list_rule = "- リスト形式の場合、各項目は必ず ✅ で始めること（☐などの記号は絶対に使わない）\n"
        list_rule += "- リストを全部出力したあとに、各項目の説明を以下の形式で書くこと\n"
        list_rule += "  ・〇〇→ \n"
        list_rule += "  説明文（適宜改行を入れて読みやすくする）\n"
        list_rule += "- 説明文の前には必ず改行を入れること（・〇〇のすぐ横に書かない）\n"
        list_rule += "- 投稿は必ず250文字以内に収めること\n"
    else:
        list_rule = "- 200文字以内\n"

    prompt = "以下の条件でThreadsの投稿文を1つ作成してください。\n\n"
    prompt += "【投稿パターン】" + pattern + "\n"
    prompt += "【冒頭パターン】" + opening_pattern + "\n"
    prompt += "【1行目】必ず以下の書き出しで始めること：" + first_line + "\n"
    prompt += "【トピック】" + topic + "\n"
    prompt += "【重要】1行目のタイトルと投稿内容を必ず一致させること\n\n"
    prompt += "条件：\n"
    prompt += list_rule
    prompt += "- **【重要】必ず1つの投稿で内容を完結させること。**\n"
    prompt += "- 「続きは次のスレで」「続きはリプ欄」「(1/2)」といった、次があることを示唆する表現は一切禁止です。\n"
    prompt += "- HSPや繊細さんが共感できる、具体的で実用的な内容\n"
    prompt += "- 「面接で非現実的な事を聞く」「怒号があるか聞く」といった、現実的に不可能なことや、応募者の印象を下げるNG提案は絶対にしないこと\n"
    prompt += "- 読みやすい改行。語尾の連続を避けること\n"
    prompt += "- 最後にハッシュタグを必ず3つ、全て#から始めること\n"
    prompt += "- *や**のようなマークダウン記法は絶対に使わない\n"
    prompt += "- 自然な日本語でAIっぽくない表現にする\n"
    prompt += "- ✅ 以外の絵文字は使わない\n"
    prompt += past_text + "\n"
    prompt += "投稿文だけを出力してください。"

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def score_post(post, first_line):
    prompt = f"以下のThreads投稿を採点してください。\n\n1行目：{first_line}\n投稿文：\n{post}\n\n平均点:X.X の形式で出力してください。"
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        score_str = message.content[0].text
        if "平均点:" in score_str:
            score = float(score_str.split("平均点:")[1].split()[0].strip())
        else:
            score = 7.0
    except:
        score = 7.0
    return score

# --- 実行メイン処理 ---
recent_data = get_recent_data()
available_patterns = [p for p in PATTERNS if p not in recent_data["patterns"]]
pattern = random.choice(available_patterns if available_patterns else PATTERNS)
available_openings = [o for o in OPENING_PATTERNS if o not in recent_data["openings"]]
opening_pattern = random.choice(available_openings if available_openings else OPENING_PATTERNS)
first_line, topic = random.choice(FIRST_LINE_TOPIC_PAIRS)

past_posts = []
try:
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
        past_posts = [p["text"] for p in posts[-10:]]
except:
    pass

max_attempts = 3
final_post = None
final_score = 0

for attempt in range(max_attempts):
    print(f"生成試行 {attempt + 1}/{max_attempts}")
    post = generate_post(pattern, opening_pattern, first_line, topic, past_posts)
    post = post.replace("**", "").replace("＃", "#")
    post = post.replace("!", "！").replace("?", "？")

    lines = post.strip().split('\n')
    if lines:
        lines[0] = first_line
    
    fixed_lines = []
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            fixed_lines.append("")
            continue
        if "#" in clean_line:
            words = clean_line.split()
            new_words = [w if w.startswith('#') else '#' + w for w in words if w]
            fixed_lines.append(' '.join(new_words))
        else:
            fixed_lines.append(line)
    post = '\n'.join(fixed_lines)

    score = score_post(post, first_line)
    print(f"スコア: {score}")
    if score >= 7.0:
        final_post = post
        final_score = score
        break
    elif attempt == max_attempts - 1:
        final_post = post
        final_score = score

posts_data = []
try:
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
except:
    pass

posts_data.append({
    "text": final_post,
    "pattern": pattern,
    "opening_pattern": opening_pattern,
    "score": final_score,
    "created_at": datetime.now().isoformat(),
    "posted": False
})

two_weeks_ago = datetime.now() - timedelta(days=14)
posts_data = [p for p in posts_data if datetime.fromisoformat(p["created_at"]) > two_weeks_ago]

with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=2)

print("\n=== 生成完了 ===")
print(final_post)