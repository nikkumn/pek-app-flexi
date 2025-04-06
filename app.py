from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import openai
import os
import uuid

app = Flask(__name__)

# ✅ HTML＋CSS自動生成
def generate_custom_html(filename):
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    prompt = f"""
キャラクター画像「{filename}」から想像して、
その雰囲気・世界観・性格に合った1ページのWebページ（HTML＋CSS）を日本語で生成してください。

- フォントや色、背景、レイアウトもその世界観に合うように。
- アップロード画像（static/uploads/{filename}）を必ず表示。
- 完成したHTMLをそのまま表示できる形で返してください。
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1800
    )

    html_code = response.choices[0].message["content"]

    # 一意なファイル名で保存
    unique_id = str(uuid.uuid4())
    result_path = f"templates/generated_{unique_id}.html"
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    return f"generated_{unique_id}.html"

# ✅ フォーム画面
@app.route('/')
def index():
    return render_template('index.html')

# ✅ アップロード＆生成
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "ファイルが送信されていません", 400

    file = request.files['file']
    if file.filename == '':
        return "ファイル名が空です", 400

    ext = os.path.splitext(file.filename)[1]
    unique_filename = secure_filename(str(uuid.uuid4()) + ext)
    filepath = os.path.join('static/uploads', unique_filename)
    file.save(filepath)

    html_file = generate_custom_html(unique_filename)

    return redirect(url_for('render_generated', page=html_file))

# ✅ 自動生成HTMLの表示
@app.route('/generated/<page>')
def render_generated(page):
    return render_template(page)

# ✅ Render用ポート設定
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
