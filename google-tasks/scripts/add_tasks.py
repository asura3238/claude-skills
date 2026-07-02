#!/usr/bin/env python3
"""
add_tasks.py — Google Tasks 저장 스크립트 / Push a checklist into Google Tasks.

입력(JSON) 형식 / Input (JSON) format:
{
  "tasklist": "수입 검수 체크리스트",          # 대상 목록 이름 / target list title
  "tasks": [
    {
      "title": "fx백십 입고 검수 – 말통 20kg/15L",
      "notes": "설명 (선택) / optional notes",
      "due":   "2026-07-10",                    # 마감일 (선택, YYYY-MM-DD) / optional due date
      "subtasks": [
        {"title": "넥 뚜껑 유무 확인 / Check neck cap present"},
        {"title": "실링 여부 확인 / Check sealing"}
      ]
    }
  ]
}

사용법 / Usage:
    python3 add_tasks.py tasks.json
    cat tasks.json | python3 add_tasks.py -

인증 / Auth:
    OAuth 토큰 JSON 경로를 아래 순서로 탐색 / token JSON resolved in order:
      1. --token <path>
      2. env  GOOGLE_TASKS_TOKEN
      3. ~/.config/google-tasks/token.json
    토큰 발급 방법은 references/setup.md 참고 / see references/setup.md.
"""
import argparse
import datetime as dt
import json
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/tasks"]
DEFAULT_TOKEN = os.path.expanduser("~/.config/google-tasks/token.json")


def die(msg: str, code: int = 1):
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(code)


def load_service(token_path: str):
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        die("의존성 필요 / install deps:\n"
            "  pip install google-api-python-client google-auth google-auth-oauthlib")

    if not os.path.exists(token_path):
        die(f"토큰 파일 없음 / token not found: {token_path}\n"
            "  references/setup.md 참고해 발급 / follow references/setup.md")

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        else:
            die("토큰이 유효하지 않음 / invalid token. 재발급 필요 / re-auth needed.")
    return build("tasks", "v1", credentials=creds, cache_discovery=False)


def get_or_create_list(service, title: str) -> str:
    resp = service.tasklists().list(maxResults=100).execute()
    for item in resp.get("items", []):
        if item.get("title") == title:
            return item["id"]
    created = service.tasklists().insert(body={"title": title}).execute()
    print(f"[info] 목록 생성 / created list: {title}")
    return created["id"]


def to_rfc3339(due: str) -> str:
    # Google Tasks는 날짜만 사용(시간 무시) / date only, time ignored.
    d = dt.datetime.strptime(due, "%Y-%m-%d")
    return d.strftime("%Y-%m-%dT00:00:00.000Z")


def insert_task(service, list_id: str, title: str, notes=None, due=None, parent=None):
    body = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = to_rfc3339(due)
    kwargs = {"tasklist": list_id, "body": body}
    if parent:
        kwargs["parent"] = parent
    return service.tasks().insert(**kwargs).execute()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="JSON file path, or '-' for stdin")
    ap.add_argument("--token", default=os.environ.get("GOOGLE_TASKS_TOKEN", DEFAULT_TOKEN))
    ap.add_argument("--dry-run", action="store_true", help="저장 안 하고 출력만 / print only")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        die(f"JSON 파싱 실패 / bad JSON: {e}")

    list_title = data.get("tasklist", "Tasks")
    tasks = data.get("tasks", [])
    if not tasks:
        die("tasks 비어 있음 / no tasks to add")

    if args.dry_run:
        print(f"[dry-run] list: {list_title}")
        for t in tasks:
            print(f"  • {t['title']}")
            for st in t.get("subtasks", []):
                print(f"      - {st['title']}")
        return

    service = load_service(args.token)
    list_id = get_or_create_list(service, list_title)

    total = 0
    for t in tasks:
        parent_task = insert_task(
            service, list_id, t["title"], t.get("notes"), t.get("due")
        )
        total += 1
        print(f"[ok] {t['title']}")
        # Google Tasks는 부모→자식 순서상 역순 삽입이 화면 순서와 맞음
        for st in reversed(t.get("subtasks", [])):
            insert_task(
                service, list_id, st["title"], st.get("notes"), st.get("due"),
                parent=parent_task["id"],
            )
            total += 1
        for st in t.get("subtasks", []):
            print(f"    - {st['title']}")

    print(f"\n[done] {total}개 항목 저장 완료 / saved {total} items → '{list_title}'")


if __name__ == "__main__":
    main()
