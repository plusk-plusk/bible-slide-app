from flask import Flask, render_template, request, send_file
from ppt_generator import generate_ppt  # 별도 모듈에 정의된 PPT 생성 함수

app = Flask(__name__)

# ✅ 루트 페이지 - index.html 렌더링
@app.route("/")
def home():
    return render_template("index.html")

# ✅ POST 요청으로 구절을 받아서 PPT 생성
@app.route("/generate", methods=["POST"])
def generate():
    verses_raw = request.form.get("verses", "")
    if not verses_raw.strip():
        return "❌ 구절을 입력해주세요.", 400

    # 요청된 구절을 파일로 저장
    with open("selected_refs.txt", "w", encoding="utf-8") as f:
        f.write(verses_raw)

    # PPT 생성 함수 호출
    try:
        generate_ppt(
            json_path="bible.json",
            ref_path="selected_refs.txt",
            output_path="BibleSlides.pptx",
            background_image="001.jpg"
        )
        return send_file("BibleSlides.pptx", as_attachment=True)
    except Exception as e:
        return f"❌ PPT 생성 중 오류 발생: {e}", 500

# ✅ 실행부
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render 배포 시 필수
