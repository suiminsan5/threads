import requests
import json
import os
import sys
import time

# --- シークレット対応：環境変数または.envからトークンを取得 ---
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
    """ユーザーIDを取得する"""
    url = "https://graph.threads.net/v1.0/me"
    params = {"access_token": TOKEN, "fields": "id,username"}
    res = requests.get(url, params=params)
    data = res.json()
    if "id" not in data:
        print(f"エラー：ユーザーID取得失敗 {data}")
        sys.exit(1)
    return data["id"]

def create_container(text, user_id, reply_to_id=None):
    """投稿または返信のコンテナ（予約枠）を作成する"""
    url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    payload = {
        "media_type": "TEXT",
        "text": text,
        "access_token": TOKEN
    }
    # 【重要】スレッドにする場合、ここに親の「コンテナID」を渡す
    if reply_to_id:
        payload["reply_to"] = reply_to_id
        
    res = requests.post(url, data=payload)
    result = res.json()
    if "id" not in result:
        print(f"コンテナ作成失敗: {result}")
        sys.exit(1)
    return result["id"]

def publish_container(creation_id, user_id):
    """作成したコンテナを実際に公開する"""
    url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    payload = {"creation_id": creation_id, "access_token": TOKEN}
    res = requests.post(url, data=payload)
    result = res.json()
    if "id" not in result:
        print(f"公開失敗: {result}")
        # 公開に失敗しても、エラー内容を確認するために続行せず停止
        sys.exit(1)
    return result

# --- メイン実行処理 ---
def main():
    # 投稿データの読み込み
    try:
        with open('posts.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except FileNotFoundError:
        print("エラー：posts.jsonが見つかりません。")
        return

    user_id = get_user_id()

    for i, post in enumerate(posts):
        # 未投稿のセット（親＋返信）を1つだけ処理
        if not post.get("posted"):
            print("=== スレッド投稿プロセス開始 ===")
            
            # 1. 親投稿のコンテナを作成
            # 後で返信を紐付けるために、この「parent_container_id」を保持する
            parent_container_id = create_container(post["parent_text"], user_id)
            print(f"親コンテナ作成完了 ID: {parent_container_id}")

            # 2. 親投稿を公開
            # 公開することで初めてタイムラインに現れる
            publish_res = publish_container(parent_container_id, user_id)
            print(f"親投稿の公開に成功しました。")

            # 3. 反映待ち（Threads側の同期ミスを防ぐために3秒待機）
            print("反映を待っています（3秒）...")
            time.sleep(3)

            # 4. 返信投稿のコンテナを作成
            # 【重要】reply_toに「公開後のID」ではなく「親のコンテナID」を指定
            reply_container_id = create_container(post["reply_text"], user_id, reply_to_id=parent_container_id)
            print(f"返信コンテナ作成完了 ID: {reply_container_id}")

            # 5. 返信投稿を公開
            reply_publish_res = publish_container(reply_container_id, user_id)
            print(f"返信（スレッド）の公開に成功しました。")
            
            # 完了フラグを立てて保存
            posts[i]["posted"] = True
            posts[i]["parent_container_id"] = parent_container_id
            break

    # 状態をposts.jsonに書き戻す
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print("=== 全てのプロセスが正常に完了しました ===")

if __name__ == "__main__":
    main()