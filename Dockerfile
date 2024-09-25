# TODO: 멀티 스테이징 빌드 적용하기

# 베이스 이미지로 Python 3.10 사용
FROM python:3.10.0-slim

# 작업 디렉터리를 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 종속성 설치
RUN apt-get update && apt-get install -y curl

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -

# 환경 변수 설정 (Poetry가 PATH에 추가되도록)
ENV PATH="/root/.local/bin:$PATH"

# 프로젝트의 의존성 파일을 복사
COPY pyproject.toml .
COPY poetry.lock .

# 프로젝트 의존성 설치
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# 애플리케이션 소스 코드를 복사
COPY app /app

# 포트 8000을 노출
EXPOSE 8000

ENV PYTHONPATH=/app

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
