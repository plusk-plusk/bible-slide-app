from flask import Flask, render_template, request, send_file
from ppt_generator import make_bible_ppt

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    verses_raw = request.form["verses"]

    if not verses_raw.strip():
        return "❌ 구절을 입력해주세요."

    with open("selected_refs.txt", "w", encoding="utf-8") as f:
        f.write(verses_raw)

    try:
        make_bible_ppt(
            json_path="bible.json",
            ref_path="selected_refs.txt",
            output_path="BibleSlides.pptx",
            background_image="001.jpg"
        )
        return send_file("BibleSlides.pptx", as_attachment=True)
    except Exception as e:
        return f"⚠️ PPT 생성 중 오류 발생: {e}"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
