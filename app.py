import openai
import os
import uuid

# ✅ ChatGPTでHTML＋CSSのページを生成（ファイルに保存）
def generate_custom_html(filename):
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    prompt = f"""
キャラクター画像「{filename}」から想像して、
その雰囲気・世界観・性格に合った1ページのWebページ（HTML＋CSS）を日本語で生成してください。

- ページ全体のHTMLとCSSを含めてください。
- フォント・背景・枠・アニメーションなども工夫してください。
- 画像は static/uploads/{filename} に表示される前提でコードを書いてください。
- 可愛い・クール・和風・近未来・ナチュラルなど、世界観をしっかり反映してください。

HTMLコードのみを返してください。
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 必要なら後で gpt-4o に切り替え可
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1800  # ちょっと多めにしておく（CSS込みなので）
    )

    html_code = response.choices[0].message["content"]

    # ✅ 一意なファイル名で保存
    unique_id = str(uuid.uuid4())
    result_path = f"templates/generated_{unique_id}.html"
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    return f"generated_{unique_id}.html"
