# Google Tasks 인증 설정 / Google Tasks Auth Setup

`add_tasks.py`가 실제 Google Tasks 계정에 저장하려면 OAuth 토큰이 한 번 필요합니다.
`add_tasks.py` needs a one-time OAuth token to write into your Google Tasks account.

---

## 1. API 사용 설정 / Enable the API

1. [Google Cloud Console](https://console.cloud.google.com/) 접속 / open the console.
2. 프로젝트 생성 또는 선택 / create or pick a project.
3. **APIs & Services → Library** 에서 **Google Tasks API** 검색 후 **Enable**.
   Search **Google Tasks API** and click **Enable**.

## 2. OAuth 클라이언트 만들기 / Create an OAuth client

1. **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
2. Application type: **Desktop app**.
3. 생성된 JSON을 `client_secret.json`으로 저장.
   Download the JSON as `client_secret.json`.
4. **OAuth consent screen** 에서 본인 Google 계정을 **Test user**로 추가.
   Add your own Google account as a **Test user** on the consent screen.

## 3. 토큰 발급 / Mint the token

아래 스크립트를 한 번 실행하면 브라우저가 열리고, 동의하면 토큰이 저장됩니다.
Run this once; a browser opens, you consent, and the token is stored.

```python
# mint_token.py
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/tasks"]
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)

out = os.path.expanduser("~/.config/google-tasks/token.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    f.write(creds.to_json())
print("saved:", out)
```

```bash
pip install google-api-python-client google-auth google-auth-oauthlib
python3 mint_token.py
```

기본 저장 위치 / default location: `~/.config/google-tasks/token.json`
다른 위치를 쓰려면 / to use another path:
- 환경변수 / env var: `export GOOGLE_TASKS_TOKEN=/path/to/token.json`
- 또는 / or: `python3 add_tasks.py tasks.json --token /path/to/token.json`

> 헤드리스(브라우저 없는) 환경에서는 로컬 PC에서 `token.json`을 발급한 뒤 그 파일만 옮겨오면 됩니다.
> On a headless environment, mint `token.json` on a local machine and copy just that file over.

## 4. 연결 없이 미리보기 / Preview without auth

토큰이 없어도 정리 결과를 확인할 수 있습니다.
You can inspect the organized result without a token:

```bash
python3 add_tasks.py tasks.json --dry-run
```
