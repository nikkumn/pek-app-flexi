from flask import Flask, render_template, request, redirect, url_for
from colorthief import ColorThief
import openai
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ 色取得（Colorthief）
def get_dominant_color(image_path):
    color_thief = ColorThief(image_path)
    return color_thief.get_color(quality=1)

# ✅ OpenAIでHTML生成（画像の雰囲気を元に）
def generate_html_from_mood(mood, bg_color):
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    prompt = f"""
画像の雰囲気が「{mood}」で、背景色はRGB({bg_color[0]}, {bg_color[1]}, {bg_color[2]})です。
この情報をもとに、キャラクター紹介用の HTML + CSS を生成してください。

- 見出し（h1）と、かわいい or クール or 和風などに合った雰囲気の、スクエア構成を基本にしたレイアウト
- ユーザーがアップした画像（URL: static/uploads/〇〇.jpg）を使う前提で、imgタグを含めてください。
- HTML全体を、出力してください。
- 画像ファイル名は {{filename}} に置き換えてください（後で挿入されます）
- 日本語で生成してください。
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )

    return response.choices[0].message["content"]

# ✅ ルート（index）
@app.route('/')
def index():
    return render_template('index.html')

# ✅ アップロード処理
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or 'mood' not in request.form:
        return "ファイルまたは雰囲気の入力がありません", 400

    file = request.files['file']
    mood = request.form['mood']

    if file.filename == '':
        return "ファイル名が空です", 400

    # ランダムファイル名に変換
    ext = os.path.splitext(file.filename)[1]
    unique_filename = secure_filename(str(uuid.uuid4()) + ext)
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)

    # 背景色取得
    bg_color = get_dominant_color(filepath)

    # OpenAIにHTML+CSSを生成してもらう
    html_template = generate_html_from_mood(mood, bg_color)

    # {{filename}} を画像名に置き換え
    final_html = html_template.replace("{{filename}}", unique_filename)

    # 出力ファイル保存
    output_path = os.path.join("static/generated", unique_filename + ".html")
    os.makedirs("static/generated", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    return redirect(url_for('show_page', filename=unique_filename + ".html"))

# ✅ 作成されたHTMLを表示
@app.route('/page/<filename>')
def show_page(filename):
    return redirect(url_for('static', filename=f"generated/{filename}"))

# ✅ Renderポート設定
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
