   # FastAPI로 게시글 REST API 서버 구현하기 #

## FastAPI로 게시글 ~~~ 소개글 ##

***
#### requirements ####
python 3.10.0

fastapi 0.0.4
***
 
### - install ###
window OS 를 사용하는 PC에 대한 install 방법입니다.

#### pyenv-win 설치 ####
```
    Invoke-WebRequest -UseBasicParsing -Uri https://pyenv.run | Invoke-Expression
```

#### python 버전 설치 및 설정 ####
```
    pyenv install 3.10.0
    pyenv global 3.10.0
```

#### poetry 설치 ####
```
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Poetry 프로젝트 초기화 ####
```
    poetry init --no-interaction
```

#### FastAPI 및 Uvicorn 설치 ####
```
    poetry add fastapi uvicorn
```

### - 실행 ###

#### Poetry 쉘 활성화 ####
```
    poetry shell
```

####  FastAPI 애플리케이션 실행 ####
```
    uvicorn main:app --reload
```

#### 설명 ####
