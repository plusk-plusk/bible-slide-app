import os
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from extractor import extract_bible_verses


# ==============================
# 템플릿 설정 (절대경로 안전)
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 템플릿 파일이 templates/ 폴더 안에 "bible_verse_template.pptx" 로 있어야 합니다.
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "bible_verse_template.pptx")

# 슬라이드 마스터에서 만든 레이아웃 이름 (모르면 None 으로 두세요: 0번 레이아웃 사용)
LAYOUT_NAME = None          # 예: "Verse Slide"
# 자리표시자 이름(선택). 이름이 다르면 자동으로 타입 기반 탐색을 시도합니다.
TITLE_PLACEHOLDER_NAME = "Title"
BODY_PLACEHOLDER_NAME  = "Verse"


# ==============================
# 유틸: 레이아웃/플레이스홀더 찾기
# ==============================
def _get_layout(prs, name_or_none):
    """레이아웃 이름으로 찾고, 없으면 0번 레이아웃 반환"""
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

def _find_title_placeholder(slide):
    # 1) 이름으로 시도
    ph = _find_placeholder_by_name(slide, TITLE_PLACEHOLDER_NAME)
    if ph:
        return ph
    # 2) 타입으로 시도
    for ph in slide.placeholders:
        try:
            if ph.placeholder_format.type == PP_PLACEHOLDER.TITLE:
                return ph
        except Exception:
            continue
    # 3) 보조: shapes.title
    if slide.shapes.title:
        return slide.shapes.title
    return None

def _find_body_placeholder(slide):
    # 1) 이름으로 시도
    ph = _find_placeholder_by_name(slide, BODY_PLACEHOLDER_NAME)
    if ph:
        return ph
    # 2) 타입 후보군에서 첫 번째 (BODY → CONTENT → SUBTITLE → OBJECT)
    type_order = [
        PP_PLACEHOLDER.BODY,
        PP_PLACEHOLDER.CONTENT,
        PP_PLACEHOLDER.SUBTITLE,
        PP_PLACEHOLDER.OBJECT,
    ]
    for ph in slide.placeholders:
        try:
            if ph.placeholder_format.type in type_order:
                return ph
        except Exception:
            continue
    # 3) 마지막 수단: 제목이 아닌 첫 번째 placeholder
    for ph in slide.placeholders:
        try:
            if ph.placeholder_format.type != PP_PLACEHOLDER.TITLE:
                return ph
        except Exception:
            continue
    return None


# ==============================
# 메인: 템플릿에 텍스트만 채우기
# ==============================
def make_bible_ppt(json_path, ref_path, output_path, background_image=None):
    """
    템플릿(.pptx)을 불러와서 레이아웃/스타일은 그대로 사용하고,
    Title/Verse 자리표시자에 텍스트만 채워 넣습니다.
    (background_image 인자는 템플릿 방식에서는 사용하지 않음)
    """

    # 0) 템플릿 존재 확인(문제 진단용 로그)
    print("TEMPLATE_PATH:", TEMPLATE_PATH)
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"템플릿 파일을 찾을 수 없습니다: {TEMPLATE_PATH}\n"
            f"- templates 폴더에 'bible_verse_template.pptx' 가 존재하는지 확인하세요.\n"
            f"- Docker/Dockerfile 에서 templates 폴더가 이미지에 포함되는지도 확인하세요."
        )

    # 1) 템플릿 로드
    prs = Presentation(TEMPLATE_PATH)

    # 2) 사용할 레이아웃 결정
    layout = _get_layout(prs, LAYOUT_NAME)

    # 3) 구절 로드
    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    # 4) 슬라이드 생성 및 텍스트 배치
    for verse in verses:
        slide = prs.slides.add_slide(layout)

        # 제목
        title_ph = _find_title_placeholder(slide)
        if title_ph is not None:
            title_ph.text = verse.get("title", "")
        else:
            print("⚠️ 제목 placeholder를 찾지 못해 이 슬라이드의 제목을 건너뜁니다.")

        # 본문
        body_ph = _find_body_placeholder(slide)
        if body_ph is not None:
            body_ph.text = verse.get("text", "")
        else:
            print("⚠️ 본문 placeholder를 찾지 못해 이 슬라이드의 본문을 건너뜁니다.")

    # 5) 저장
    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
