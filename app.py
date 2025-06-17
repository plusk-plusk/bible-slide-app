from flask import Flask, render_template, request, redirect, send_file
from ppt_generator import make_bible_ppt as generate_ppt

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    verses = request.form.get("verses", "").strip()
    if not verses:
        return "❌ 구절이 입력되지 않았습니다.", 400

    with open("selected_refs.txt", "w", encoding="utf-8") as f:
        f.write(verses)

    try:
        generate_ppt(
            json_path="bible.json",
            ref_path="selected_refs.txt",
            output_path="BibleSlides.pptx",
            background_image="001.jpg"
        )
        return redirect("/done")
    except Exception as e:
        return f"❌ 슬라이드 생성 중 오류 발생: {e}", 500

@app.route("/done")
def done():
    return render_template("done.html")

@app.route("/download")
def download():
    return send_file("BibleSlides.pptx", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
