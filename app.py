from flask import Flask, render_template, request, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from openai import OpenAI

app = Flask(__name__)

# OpenAIクライアントを初期化（環境変数 OPENAI_API_KEY が必要）
client = OpenAI()

# HTMLを自動生成する関数
def generate_custom_html(filename):
    prompt = f"""
    このキャラクター画像のファイル名「{filename}」から、以下の特徴を想像して日本語で簡潔に教えてください。

    🎨 色合い（例：パステル・ビビッド）
    😌 雰囲気（例：キュート・クール・優しい）
    🧁 テイスト（例：レトロ・未来感・和風）
    ✍️ タイポ（フォントの印象）
    💡 コンセプト（世界観・言葉）

    そしてその特徴をもとに、キャラに似合うWebページのHTMLコード（日本語・スタイル付き）を作ってください。
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content

# トップページ：アップロードフォーム表示
@app.route('/')
def index():
    return render_template('index.html')

# アップロード処理
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "ファイルが送信されていません", 400

    file = request.files['file']
    if file.filename == '':
        return "ファイル名が空です", 400

    # 保存先とユニークファイル名の生成
    ext = os.path.splitext(file.filename)[1]
    unique_filename = secure_filename(str(uuid.uuid4()) + ext)
    upload_path = os.path.join('static/uploads', unique_filename)
    file.save(upload_path)

    # OpenAIでHTML生成
    html_code = generate_custom_html(unique_filename)

    # ユーザーごとのHTMLを保存
    output_filename = f"{uuid.uuid4().hex}.html"
    output_path = os.path.join('static/generated', output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_code)

    # 完成したページへリダイレクト
    return redirect(url_for('static', filename=f'generated/{output_filename}'))

# ポート指定（Render用）
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
