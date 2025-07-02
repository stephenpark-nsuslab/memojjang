# 메모짱 배포 가이드

이 문서는 메모짱 애플리케이션을 프로덕션 환경에 배포하는 방법을 설명합니다.

## 프로덕션 배포 체크리스트

### 1. 환경 설정

- [ ] **환경변수 설정**
  - [ ] `DJANGO_SECRET_KEY`: 강력한 시크릿 키 생성 및 설정
  - [ ] `DJANGO_DEBUG=False`: 디버그 모드 비활성화
  - [ ] `DJANGO_ALLOWED_HOSTS`: 도메인 설정
  - [ ] `SECURE_SSL_REDIRECT=True`: HTTPS 리다이렉트 활성화

- [ ] **보안 설정**
  - [ ] SSL/TLS 인증서 설정
  - [ ] 방화벽 설정
  - [ ] 데이터베이스 보안 설정

### 2. 서버 준비

- [ ] **시스템 의존성 설치**
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib
  
  # CentOS/RHEL
  sudo yum install python3 python3-pip nginx postgresql postgresql-server
  ```

- [ ] **Python 가상환경 설정**
  ```bash
  python3 -m venv /opt/memojjang/venv
  source /opt/memojjang/venv/bin/activate
  ```

### 3. 애플리케이션 배포

#### 3.1 코드 배포

```bash
# 프로덕션 디렉토리 생성
sudo mkdir -p /opt/memojjang
sudo chown $USER:$USER /opt/memojjang

# 저장소 클론
cd /opt/memojjang
git clone https://github.com/stephenpark-nsuslab/memojjang.git .

# 가상환경 활성화
source venv/bin/activate

# 프로덕션 의존성 설치
pip install -r requirements-production.txt
```

#### 3.2 환경변수 설정

```bash
# 환경변수 파일 생성
cp .env.example .env

# 환경변수 편집
nano .env
```

**중요한 환경변수:**
```bash
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
USE_X_FORWARDED_PROTO=True
DATABASE_URL=postgres://memojjang_user:password@localhost:5432/memojjang_db
```

#### 3.3 데이터베이스 설정

##### PostgreSQL 설정 (권장)

```bash
# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 및 사용자 생성
sudo -u postgres psql

-- PostgreSQL 내에서 실행
CREATE DATABASE memojjang_db;
CREATE USER memojjang_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE memojjang_db TO memojjang_user;
\q
```

#### 3.4 Django 설정

```bash
# 데이터베이스 마이그레이션
cd /opt/memojjang/memojjang
python manage.py migrate

# 정적 파일 수집
python manage.py collectstatic --noinput

# 슈퍼유저 생성
python manage.py createsuperuser
```

### 4. 웹 서버 설정

#### 4.1 Gunicorn 서비스 설정

**Systemd 서비스 파일 생성:** `/etc/systemd/system/memojjang.service`

```ini
[Unit]
Description=Memojjang Django Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/memojjang/memojjang
Environment=PATH=/opt/memojjang/venv/bin
EnvironmentFile=/opt/memojjang/.env
ExecStart=/opt/memojjang/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/opt/memojjang/memojjang.sock \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    memojjang_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**서비스 활성화:**
```bash
sudo systemctl daemon-reload
sudo systemctl start memojjang
sudo systemctl enable memojjang
sudo systemctl status memojjang
```

#### 4.2 Nginx 설정

**Nginx 설정 파일:** `/etc/nginx/sites-available/memojjang`

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # HTTPS로 리다이렉트
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 인증서 설정
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL 보안 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 보안 헤더
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 정적 파일 서빙
    location /static/ {
        alias /opt/memojjang/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 메인 애플리케이션
    location / {
        proxy_pass http://unix:/opt/memojjang/memojjang.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # 타임아웃 설정
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # 파일 업로드 크기 제한
    client_max_body_size 10M;
}
```

**Nginx 설정 활성화:**
```bash
sudo ln -s /etc/nginx/sites-available/memojjang /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL/TLS 인증서 설정

#### Let's Encrypt 사용 (무료)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# 인증서 발급
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

### 6. 모니터링 및 로깅

#### 6.1 로그 설정

**Django 로그 설정을 settings.py에 추가:**

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/memojjang/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

#### 6.2 로그 디렉토리 생성

```bash
sudo mkdir -p /opt/memojjang/logs
sudo chown www-data:www-data /opt/memojjang/logs
```

### 7. 백업 설정

#### 7.1 데이터베이스 백업 스크립트

**백업 스크립트:** `/opt/memojjang/scripts/backup.sh`

```bash
#!/bin/bash
BACKUP_DIR="/opt/memojjang/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="memojjang_db"
DB_USER="memojjang_user"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 데이터베이스 백업
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

#### 7.2 Cron 작업 설정

```bash
# crontab 편집
sudo crontab -e

# 매일 오전 2시에 백업 실행
0 2 * * * /opt/memojjang/scripts/backup.sh
```

### 8. 성능 최적화

#### 8.1 데이터베이스 최적화

```sql
-- PostgreSQL 설정 최적화 (/etc/postgresql/13/main/postgresql.conf)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

#### 8.2 Redis 캐싱 (선택사항)

```bash
# Redis 설치
sudo apt install redis-server

# Django 설정에 캐시 추가
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 9. 보안 강화

#### 9.1 방화벽 설정

```bash
# UFW 설정
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

#### 9.2 실패한 로그인 시도 차단 (fail2ban)

```bash
# fail2ban 설치
sudo apt install fail2ban

# 설정 파일 생성: /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
findtime = 600
bantime = 7200
maxretry = 10
```

### 10. 배포 후 확인사항

- [ ] **기능 테스트**
  - [ ] 웹사이트 접속 확인
  - [ ] 로그인/회원가입 기능
  - [ ] 메모 CRUD 기능
  - [ ] 관리자 페이지 접속

- [ ] **성능 테스트**
  - [ ] 페이지 로딩 속도
  - [ ] 동시 접속자 처리
  - [ ] 서버 리소스 사용량

- [ ] **보안 테스트**
  - [ ] SSL 인증서 확인
  - [ ] 보안 헤더 확인
  - [ ] 취약점 스캔

### 11. 유지보수

#### 11.1 정기 업데이트

```bash
# 애플리케이션 업데이트
cd /opt/memojjang
git pull origin main
source venv/bin/activate
pip install -r requirements-production.txt
python memojjang/manage.py migrate
python memojjang/manage.py collectstatic --noinput
sudo systemctl restart memojjang
```

#### 11.2 모니터링

- 서버 리소스 모니터링 (CPU, 메모리, 디스크)
- 애플리케이션 로그 모니터링
- 데이터베이스 성능 모니터링
- SSL 인증서 만료일 확인

### 트러블슈팅

#### 일반적인 문제들

1. **502 Bad Gateway**
   - Gunicorn 서비스 상태 확인: `sudo systemctl status memojjang`
   - 소켓 파일 권한 확인

2. **정적 파일이 로드되지 않음**
   - `collectstatic` 재실행
   - Nginx 정적 파일 경로 확인

3. **데이터베이스 연결 오류**
   - 환경변수 확인
   - PostgreSQL 서비스 상태 확인

4. **SSL 인증서 문제**
   - 인증서 경로 확인
   - Certbot 갱신 상태 확인

더 자세한 트러블슈팅은 로그 파일을 확인하세요:
- Django: `/opt/memojjang/logs/django.log`
- Nginx: `/var/log/nginx/error.log`
- Gunicorn: `sudo journalctl -u memojjang`