from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from extractor import extract_bible_verses

def make_bible_ppt(json_path, ref_path, output_path, background_image):
    prs = Presentation()
    prs.slide_width  = Inches(13.33)  # 16:9
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)

    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # 배경 전체
        slide.shapes.add_picture(
            background_image, 0, 0,
            width=prs.slide_width, height=prs.slide_height
        )

        # 여백/영역
        margin_h  = Inches(1.3)
        box_width = prs.slide_width - 2 * margin_h

        # ─────────────────────────────────────────────
        # ① 제목: 텍스트 박스 + 아주 옅은 음영(텍스트 박스 배경)
        # ─────────────────────────────────────────────
        title_top  = Inches(1.0)
        title_h    = Inches(0.9)  # 필요시 0.7~1.0 사이로 조정

        title_box = slide.shapes.add_textbox(margin_h, title_top, box_width, title_h)
        title_frame = title_box.text_frame
        title_frame.word_wrap = True

        # (음영) 텍스트 박스 배경을 아주 옅게
        tfill = title_box.fill
        tfill.solid()
        tfill.fore_color.rgb = RGBColor(0, 0, 0)   # 검정
        tfill.transparency   = 0.16                # ← 너무 어두우면 0.18→0.14→0.12로 낮추기
        title_box.line.fill.background()           # 테두리 제거

        p_title = title_frame.paragraphs[0]
        p_title.alignment = PP_ALIGN.LEFT
        run_title = p_title.add_run()
        run_title.text = verse["title"]
        run_title.font.size = Pt(36)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
        run_title.font.name = 'Apple SD Gothic Neo'

        # ─────────────────────────────────────────────
        # ② 본문: 텍스트 박스 + 아주 옅은 음영(텍스트 박스 배경)
        # ─────────────────────────────────────────────
        body_top = title_top + Inches(0.85)
        body_h   = Inches(3.6)  # 필요시 3.2~3.8로 조정

        body_box = slide.shapes.add_textbox(margin_h, body_top, box_width, body_h)
        body_frame = body_box.text_frame
        body_frame.word_wrap = True

        # (음영) 본문 박스도 아주 옅게
        bfill = body_box.fill
        bfill.solid()
        bfill.fore_color.rgb = RGBColor(0, 0, 0)
        bfill.transparency   = 0.14                # 본문은 한 단계 더 옅게 권장(예: 0.12~0.16)
        body_box.line.fill.background()

        p_body = body_frame.paragraphs[0]
        p_body.alignment = PP_ALIGN.JUSTIFY
        p_body.line_spacing = 1.2
        run_body = p_body.add_run()
        run_body.text = verse["text"]
        run_body.font.size = Pt(53)
        run_body.font.bold = True
        run_body.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
        run_body.font.name = 'Apple SD Gothic Neo'

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
