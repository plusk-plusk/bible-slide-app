from flask import Flask, render_template, request, send_file
from ppt_generator import make_bible_ppt
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    verses_raw = request.form["verses"]
    verses = [v.strip() for v in verses_raw.splitlines() if v.strip()]

    if not verses:
        return "❌ 구절을 입력해주세요.", 400

    # 입력 구절을 텍스트 파일로 저장
    ref_path = "selected_refs.txt"
    with open(ref_path, "w", encoding="utf-8") as f:
        for verse in verses:
            f.write(verse + "\n")

    # PPT 생성
    make_bible_ppt(
        json_path="bible.json",
        ref_path=ref_path,
        output_path="BibleSlides.pptx",
        background_image="001.jpg"
    )

    return send_file("BibleSlides.pptx", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
