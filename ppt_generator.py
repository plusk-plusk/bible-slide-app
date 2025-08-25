import os
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from extractor import extract_bible_verses

# ==============================
# 템플릿 경로 (절대경로로 안전하게)
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "bible_verse_template.pptx")

# 레이아웃/자리표시자 이름
LAYOUT_NAME = None                  # 특정 레이아웃명을 쓸 경우 문자열로 지정, 모르면 None(0번 사용)
TITLE_PLACEHOLDER_NAME = "Title"    # 마스터에서 만든 제목 자리표시자 이름
BODY_PLACEHOLDER_NAME  = "Verse"    # 마스터에서 만든 본문 자리표시자 이름

# ==============================
# 유틸
# ==============================
def _get_layout(prs, name_or_none):
    """레이아웃 이름으로 찾고, 없으면 0번 반환"""
    if name_or_none:
        for layout in prs.slide_layouts:
            if getattr(layout, "name", "") == name_or_none:
                return layout
    return prs.slide_layouts[0]

def _find_placeholder_by_name(slide, name):
    for ph in slide.placeholders:
        if ph.name == name:
            return ph
    return None

def _has_text_frame(shape):
    try:
        return getattr(shape, "has_text_frame", False) and shape.has_text_frame
    except Exception:
        return False

def _safe_set_text(shape, text):
    """
    BODY / SUBTITLE / CONTENT 등 어떤 placeholder든
    text_frame이 있으면 안전하게 텍스트를 설정.
    """
    if not _has_text_frame(shape):
        raise ValueError("선택된 placeholder에 text_frame이 없습니다.")
    tf = shape.text_frame
    tf.clear()              # 남아있는 단락/런 정리
    tf.text = text or ""

def _find_title_placeholder(slide):
    # 1) 이름 우선
    ph = _find_placeholder_by_name(slide, TITLE_PLACEHOLDER_NAME)
    if ph and _has_text_frame(ph):
        return ph
    # 2) 타입(TITLE, CENTER_TITLE)
    for typ in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
        for shp in slide.placeholders:
            try:
                if shp.placeholder_format.type == typ and _has_text_frame(shp):
                    return shp
            except Exception:
                continue
    # 3) 보조
    if slide.shapes.title and _has_text_frame(slide.shapes.title):
        return slide.shapes.title
    return None

def _find_body_placeholder(slide):
    # 1) 이름 우선
    ph = _find_placeholder_by_name(slide, BODY_PLACEHOLDER_NAME)
    if ph and _has_text_frame(ph):
        return ph
    # 2) 타입 우선순위: BODY → SUBTITLE → CONTENT → OBJECT
    type_order = [
        PP_PLACEHOLDER.BODY,
        PP_PLACEHOLDER.SUBTITLE,
        PP_PLACEHOLDER.CONTENT,
        PP_PLACEHOLDER.OBJECT,
    ]
    for t in type_order:
        for shp in slide.placeholders:
            try:
                if shp.placeholder_format.type == t and _has_text_frame(shp):
                    return shp
            except Exception:
                continue
    # 3) 마지막: 제목이 아닌 텍스트프레임 보유 placeholder
    for shp in slide.placeholders:
        try:
            if shp.placeholder_format.type != PP_PLACEHOLDER.TITLE and _has_text_frame(shp):
                return shp
        except Exception:
            continue
    return None

# ==============================
# 메인
# ==============================
def make_bible_ppt(json_path, ref_path, output_path, background_image=None):
    """
    템플릿(.pptx)을 로드해 Title/Verse 자리표시자에 텍스트만 주입합니다.
    background_image 인자는 템플릿 방식에선 사용하지 않습니다.
    """
    print("TEMPLATE_PATH:", TEMPLATE_PATH)
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"템플릿이 없습니다: {TEMPLATE_PATH}\n"
            f"- templates 폴더에 bible_verse_template.pptx 가 있는지 확인하세요."
        )

    prs = Presentation(TEMPLATE_PATH)
    layout = _get_layout(prs, LAYOUT_NAME)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(layout)

        # 제목
        title_ph = _find_title_placeholder(slide)
        if title_ph is not None:
            try:
                _safe_set_text(title_ph, verse.get("title", ""))
            except Exception as e:
                print("제목 채우기 오류:", repr(e))
        else:
            print("⚠️ 제목 placeholder를 찾지 못했습니다.")

        # 본문
        body_ph = _find_body_placeholder(slide)
        if body_ph is not None:
            try:
                _safe_set_text(body_ph, verse.get("text", ""))
            except Exception as e:
                print("본문 채우기 오류:", repr(e))
        else:
            print("⚠️ 본문 placeholder를 찾지 못했습니다.")

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
