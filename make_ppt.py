from flask import Flask, request, render_template, send_file
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
        return "❌ 구절을 입력해주세요.", 400

    with open("selected_refs.txt", "w", encoding="utf-8") as f:
        for verse in verses:
            f.write(verse + "\n")

    make_bible_ppt(
        json_path="bible.json",
        ref_path="selected_refs.txt",
        output_path="BibleSlides.pptx",
        background_image="001.jpg"
    )

    return send_file("BibleSlides.pptx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
