# 1. 베이스 이미지 지정
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 모든 파일 복사
COPY . /app

# 4. 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. Render에서 요구하는 포트 개방
EXPOSE 10000

# 6. 앱 실행 (app.py 기준, 포트 10000)
CMD ["python", "app.py"]
