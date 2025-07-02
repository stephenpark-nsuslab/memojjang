# 메모짱 (Memojjang)

Django 기반의 메모장 웹 애플리케이션입니다.

## 주요 기능

- 사용자 로그인 및 회원가입
- 메모 작성, 수정, 삭제
- 메모 목록 조회
- 개인별 메모 관리

## 기술 스택

### 프론트엔드
- Django 템플릿 엔진 (HTML, CSS, JavaScript)
- Bootstrap (반응형 UI)

### 백엔드
- Django Framework 4.2.x
- Django Forms (폼 처리)
- Django 내장 인증 시스템

### 데이터베이스
- SQLite (개발환경)
- PostgreSQL (프로덕션 권장)

### 배포
- Gunicorn (WSGI 서버)
- WhiteNoise (정적 파일 서빙)
- Nginx (권장, 리버스 프록시)

## 프로젝트 구조

```
memojjang/
├── .github/                    # GitHub Actions 및 설정
├── docs/                      # 문서
├── memojjang/                 # Django 프로젝트 루트
│   ├── memojjang_project/     # 메인 Django 프로젝트
│   │   ├── settings.py        # Django 설정
│   │   ├── urls.py           # URL 라우팅
│   │   ├── wsgi.py           # WSGI 설정
│   │   └── asgi.py           # ASGI 설정
│   └── manage.py             # Django 관리 스크립트
├── apps/                     # Django 앱들
│   ├── memos/                # 메모 앱
│   │   ├── models.py         # 메모 데이터 모델
│   │   ├── views.py          # 메모 뷰 로직
│   │   ├── urls.py           # 메모 URL 라우팅
│   │   └── migrations/       # 데이터베이스 마이그레이션
│   └── users/                # 사용자 앱
│       ├── models.py         # 사용자 데이터 모델
│       ├── views.py          # 사용자 뷰 로직
│       ├── urls.py           # 사용자 URL 라우팅
│       └── migrations/       # 데이터베이스 마이그레이션
├── static/                   # 정적 파일
│   └── css/                  # CSS 파일
├── templates/                # Django 템플릿
│   ├── base.html            # 기본 템플릿
│   ├── memos/               # 메모 관련 템플릿
│   └── users/               # 사용자 관련 템플릿
├── utils/                   # 유틸리티 함수
├── requirements.txt         # Python 의존성 (개발)
├── requirements-production.txt  # Python 의존성 (프로덕션)
└── README.md               # 프로젝트 문서
```

## 설치 및 실행

### 개발 환경 설정

1. **저장소 클론**
   ```bash
   git clone https://github.com/stephenpark-nsuslab/memojjang.git
   cd memojjang
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   venv\Scripts\activate     # Windows
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 필요한 환경변수 설정
   ```

5. **데이터베이스 마이그레이션**
   ```bash
   cd memojjang
   python manage.py migrate
   ```

6. **슈퍼유저 생성 (선택사항)**
   ```bash
   python manage.py createsuperuser
   ```

7. **개발 서버 실행**
   ```bash
   python manage.py runserver
   ```

   브라우저에서 `http://127.0.0.1:8000`에 접속하여 애플리케이션을 확인할 수 있습니다.

### 프로덕션 배포

#### 1. 환경변수 설정

프로덕션 환경에서는 다음 환경변수를 설정해야 합니다:

```bash
# Django 설정
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 보안 설정
SECURE_SSL_REDIRECT=True
USE_X_FORWARDED_PROTO=True
SECURE_HSTS_SECONDS=31536000

# 데이터베이스 (PostgreSQL 예시)
DATABASE_URL=postgres://user:password@localhost:5432/memojjang
```

#### 2. 프로덕션 의존성 설치

```bash
pip install -r requirements-production.txt
```

#### 3. 정적 파일 수집

```bash
python manage.py collectstatic --noinput
```

#### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

#### 5. Gunicorn으로 실행

```bash
gunicorn memojjang_project.wsgi:application --bind 0.0.0.0:8000
```

#### 6. Nginx 설정 (권장)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/your/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 환경변수 문서

### 필수 환경변수

| 변수명 | 설명 | 기본값 | 예시 |
|--------|------|--------|------|
| `DJANGO_SECRET_KEY` | Django 시크릿 키 | `your-default-secret-key` | `django-insecure-xyz...` |
| `DJANGO_DEBUG` | 디버그 모드 | `False` | `True` / `False` |
| `DJANGO_ALLOWED_HOSTS` | 허용된 호스트 목록 | `""` | `localhost,127.0.0.1,yourdomain.com` |

### 선택적 환경변수 (프로덕션)

| 변수명 | 설명 | 기본값 | 예시 |
|--------|------|--------|------|
| `SECURE_SSL_REDIRECT` | HTTPS 리다이렉트 | `True` | `True` / `False` |
| `USE_X_FORWARDED_PROTO` | X-Forwarded-Proto 헤더 사용 | `False` | `True` / `False` |
| `SECURE_HSTS_SECONDS` | HSTS 최대 시간 (초) | `31536000` | `31536000` |
| `DATABASE_URL` | 데이터베이스 URL | SQLite 사용 | `postgres://user:pass@host:5432/db` |

### .env 파일 예시

```bash
# Django 기본 설정
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# 프로덕션에서는 다음 설정들 추가
# SECURE_SSL_REDIRECT=True
# USE_X_FORWARDED_PROTO=True
# SECURE_HSTS_SECONDS=31536000
```

## 테스트

### 테스트 실행

```bash
cd memojjang
python manage.py test
```

### 특정 앱 테스트

```bash
python manage.py test apps.memos
python manage.py test apps.users
```

## 개발

### 새로운 앱 추가

```bash
cd apps
python ../memojjang/manage.py startapp newapp
```

앱 생성 후 `memojjang_project/settings.py`의 `INSTALLED_APPS`에 추가하세요.

### 데이터베이스 변경사항 적용

```bash
python manage.py makemigrations
python manage.py migrate
```

### 관리자 페이지 접속

개발 서버 실행 후 `http://127.0.0.1:8000/admin/`에서 관리자 페이지에 접속할 수 있습니다.

## 보안 고려사항

### 프로덕션 환경에서 체크리스트

- [ ] `DEBUG=False` 설정
- [ ] 강력한 `SECRET_KEY` 설정
- [ ] `ALLOWED_HOSTS` 적절히 설정
- [ ] HTTPS 사용 (`SECURE_SSL_REDIRECT=True`)
- [ ] 보안 헤더 설정 활성화
- [ ] 데이터베이스 백업 설정
- [ ] 정기적인 의존성 업데이트
- [ ] 로그 모니터링 설정

### 권장 사항

- 프로덕션에서는 PostgreSQL 또는 MySQL 사용
- Redis를 사용한 캐싱 고려
- 정기적인 보안 업데이트
- SSL 인증서 설정
- 로그 모니터링 및 오류 추적 시스템 연동

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/new-feature`)
3. 변경사항을 커밋합니다 (`git commit -am 'Add new feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/new-feature`)
5. Pull Request를 생성합니다

## 지원

문제가 발생하면 [Issues](https://github.com/stephenpark-nsuslab/memojjang/issues)에 버그 리포트나 기능 요청을 올려주세요.