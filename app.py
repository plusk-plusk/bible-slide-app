from flask import Flask, render_template, request, send_file
import os
from make_ppt import make_bible_ppt

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    verses_raw = request.form["verses"]
    verses = [v.strip() for v in verses_raw.splitlines() if v.strip()]

    if not verses:
        return "<h1>❌ 구절을 입력해주세요.</h1>"

    with open("selected_refs.txt", "w", encoding="utf-8") as f:
        for v in verses:
            f.write(v + "\n")

    make_bible_ppt(
        json_path="bible.json",
        ref_path="selected_refs.txt",
        output_path="BibleSlides.pptx",
        background_image="001.jpg"
    )

    return send_file("BibleSlides.pptx", as_attachment=True)

if __name__ == "__main__":
    # ✅ Render에서 포트를 열어야 하기 때문에 host와 port 명시
    app.run(host="0.0.0.0", port=10000)
