# -*- coding: utf-8 -*-
"""
템플릿(.pptx) 기반 성경 슬라이드 생성기
- 슬라이드 마스터/레이아웃에 '제목(Title)' + '본문(Body)' 자리표시자가 있어야 함
- 배경/폰트/그림자 같은 시각효과는 템플릿에서 제어 (코드는 텍스트만 주입)
"""

import os
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.enum.text import PP_ALIGN
from extractor import extract_bible_verses

# ---- 템플릿 경로(절대경로) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "bible_verse_template.pptx")

# 필요하면 특정 레이아웃 이름으로 고정 가능 (None이면 자동 탐색)
PREFERRED_LAYOUT_NAME = None  # 예: "Verse Layout"

def _pick_layout(prs):
    """
    템플릿에서 '제목 + 본문' 자리표시자가 동시에 있는 레이아웃을 선택.
    이름을 지정했다면 이름 우선, 없으면 자동 탐색.
    """
    if PREFERRED_LAYOUT_NAME:
        for lo in prs.slide_layouts:
            if lo.name == PREFERRED_LAYOUT_NAME:
                return lo

    # 자동 탐색: TITLE과 BODY 자리표시자를 둘 다 가진 첫 레이아웃
    for lo in prs.slide_layouts:
        kinds = []
        for shp in lo.shapes:
            if shp.is_placeholder:
                kinds.append(shp.placeholder_format.type)
        if (PP_PLACEHOLDER.TITLE in kinds) and (PP_PLACEHOLDER.BODY in kinds):
            return lo

    # 못 찾으면 첫 레이아웃이라도 반환 (최악의 경우)
    return prs.slide_layouts[0]

def _get_placeholder(slide, ptype):
    """슬라이드에서 지정 타입(TITLE/BODY)의 자리표시자 객체 반환 (없으면 None)"""
    for shp in slide.shapes:
        if shp.is_placeholder and shp.placeholder_format.type == ptype:
            return shp
    return None

def _set_text(shape, text, align=None):
    """자리표시자에 텍스트 넣기 (기존 내용 비우고 1문단만 사용)"""
    if shape is None:
        return
    tf = shape.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    if align is not None:
        p.alignment = align
    p.text = text or ""

def make_bible_ppt(json_path, ref_path, output_path, background_image=None):
    """
    템플릿 기반으로 슬라이드 생성.
    - 텍스트만 채움 (시각효과는 템플릿에서 설정)
    - background_image 인자는 무시(템플릿 배경 사용). 필요 시 템플릿에서 바꿔주세요.
    """
    # 템플릿 열기
    prs = Presentation(TEMPLATE_PATH)

    # 사용할 레이아웃 선택
    layout = _pick_layout(prs)

    # 구절 로드
    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        # 레이아웃으로 새 슬라이드 추가
        slide = prs.slides.add_slide(layout)

        # 자리표시자 찾기
        t_shp = _get_placeholder(slide, PP_PLACEHOLDER.TITLE)
        b_shp = _get_placeholder(slide, PP_PLACEHOLDER.BODY)

        # 텍스트 주입
        _set_text(t_shp, verse.get("title", ""), align=PP_ALIGN.LEFT)
        _set_text(b_shp, verse.get("text", ""),  align=PP_ALIGN.JUSTIFY)

        # 만약 템플릿이 SUBTITLE을 쓴 경우(드물지만) 보정
        if b_shp is None:
            sub = _get_placeholder(slide, PP_PLACEHOLDER.SUBTITLE)
            if sub is not None:
                _set_text(sub, verse.get("text", ""), align=PP_ALIGN.JUSTIFY)

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
