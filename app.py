from flask import Flask, render_template, request, send_file
from pptx import Presentation
from pptx.util import Inches, Pt
import json
import os
import uuid

app = Flask(__name__)

# JSON 경로 설정
BIBLE_JSON_PATH = os.path.join(os.path.dirname(__file__), "bible.json")

# JSON 로드
with open(BIBLE_JSON_PATH, "r", encoding="utf-8") as f:
    bible_data = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    verses_raw = request.form["verses"]
    verses = [v.strip() for v in verses_raw.splitlines() if v.strip()]

    prs = Presentation()
    blank_slide_layout = prs.slide_layouts[6]

    for verse in verses:
        verse_text = bible_data.get(verse)
        slide = prs.slides.add_slide(blank_slide_layout)
        
        # 제목
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(8.5), Inches(1.0))
        title_frame = title_box.text_frame
        p = title_frame.paragraphs[0]
        p.text = verse
        p.font.size = Pt(44)
        p.font.bold = True

        # 본문
        body_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(8.5), Inches(5.0))
        body_frame = body_box.text_frame
        p = body_frame.paragraphs[0]
        p.text = verse_text if verse_text else f"⚠️ 구절 파싱 오류: {verse}"
        p.font.size = Pt(60)
        body_frame.line_spacing = 1.2

    output_path = f"output_{uuid.uuid4().hex}.pptx"
    prs.save(output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
