# 첫 번째 스테이지: 빌드 스테이지 (Poetry 및 종속성 설치)
FROM python:3.10-slim AS builder

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 종속성 설치
RUN apt-get update && apt-get install -y curl

# Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -

# 환경 변수 설정 (Poetry가 PATH에 추가되도록)
ENV PATH="/root/.local/bin:$PATH"

# 프로젝트의 의존성 파일을 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치 (프로덕션 환경에서 필요하지 않은 개발 의존성 제외)
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# 두 번째 스테이지: 실행 스테이지 (최종 프로덕션 이미지)
FROM python:3.10-slim

# 작업 디렉터리 설정
WORKDIR /app

# 첫 번째 스테이지에서 설치된 종속성을 복사 (불필요한 파일 제외)
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 소스 코드 복사
COPY . /app

# 포트 8000을 노출
EXPOSE 8000

ENV PYTHONPATH=/app

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]