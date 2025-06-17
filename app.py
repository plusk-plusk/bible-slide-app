from flask import Flask, request, render_template, send_file
from pptx import Presentation
from pptx.util import Inches, Pt
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    verse = request.form['verse']  # 예: "요한복음 3:16"
    text = request.form['text']    # 예: "하나님이 세상을..."

    prs = Presentation()
    slide_layout = prs.slide_layouts[6]  # 빈 슬라이드
    slide = prs.slides.add_slide(slide_layout)

    left = Inches(1)
    top = Inches(1)
    width = Inches(8)
    height = Inches(1.5)

    title_box = slide.shapes.add_textbox(left, top, width, height)
    title_frame = title_box.text_frame
    title_frame.text = verse
    title_frame.paragraphs[0].font.size = Pt(48)

    body_top = Inches(2.5)
    body_height = Inches(3.5)

    body_box = slide.shapes.add_textbox(left, body_top, width, body_height)
    body_frame = body_box.text_frame
    body_frame.text = text
    body_frame.paragraphs[0].font.size = Pt(36)

    pptx_path = "output.pptx"
    prs.save(pptx_path)

    return send_file(pptx_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
