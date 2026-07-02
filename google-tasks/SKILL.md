---
name: google-tasks
description: |
  음성/이미지/텍스트로 받은 할 일·검수 체크리스트를 정리해서 Google Tasks에 저장하는 스킬.
  Organize a to-do / inspection checklist (from voice, image, or text) and save it into Google Tasks.

  다음 요청에 이 스킬을 사용할 것 / Use this skill when the user asks to:
  - "구글 태스크에 저장해줘", "Google Tasks에 정리해서 넣어줘", "체크리스트 태스크로 만들어줘"
  - "save to Google Tasks", "add this checklist to Google Tasks", "organize as tasks"
  - 음성 받아쓰기/사진 속 할 일을 태스크로 정리해달라는 요청
    (requests to turn a voice transcript or a photo's to-do list into tasks)
---

# Google Tasks 저장 스킬 / Save-to-Google-Tasks Skill

## 개요 / Overview

지저분한 입력(음성 받아쓰기, 사진, 메모)을 **깔끔한 태스크 구조로 정리**한 뒤
**Google Tasks에 실제로 저장**한다. 문서·항목은 국문/영문을 함께 표기한다.

Turns messy input (voice transcript, photo, notes) into a **clean task structure** and
**writes it into Google Tasks**. All items are written in both Korean and English.

> **왜 필요한가 / Why:** Claude 앱에는 Google Tasks 전용 커넥터가 없어 Reminder로 대체 저장되는
> 경우가 있다. 이 스킬은 Google Tasks API를 직접 호출해 원하는 목록에 정확히 저장한다.
> The Claude app has no dedicated Google Tasks connector and may fall back to Reminders.
> This skill calls the Google Tasks API directly to save into the exact list you want.

---

## Step 1. 입력 정리 / Clean the input

1. 원문에서 **검수/작업 대상**과 **확인 항목**을 분리한다.
   Separate the **target** from the individual **check items**.
2. 음성 받아쓰기 오타를 문맥으로 교정한다 (예: "시복십오"→"15", "샘"→"누수").
   Fix speech-to-text errors from context.
3. 한 대상 = **부모 태스크**, 확인 항목 = **서브태스크**로 매핑한다.
   Map one target → **parent task**, each check → **subtask**.
4. 각 항목 제목은 `한국어 / English` 형식으로 작성한다.
   Write each title as `Korean / English`.

정리 예시는 `references/example.md` 참고. / See `references/example.md`.

## Step 2. JSON 작성 / Build the JSON

`references/example_tasks.json` 형식으로 태스크를 작성한다.
Author the tasks in the shape of `references/example_tasks.json`:

```json
{
  "tasklist": "수입 검수 체크리스트 / Import Inspection",
  "tasks": [
    {
      "title": "부모 태스크 제목 / Parent title",
      "notes": "설명(선택) / notes (optional)",
      "due": "2026-07-10",
      "subtasks": [
        {"title": "확인 항목 / Check item"}
      ]
    }
  ]
}
```

- `tasklist`: 저장할 목록 이름. 없으면 자동 생성 / target list; auto-created if missing.
- `due`: `YYYY-MM-DD` (선택 / optional).
- `subtasks`: Google Tasks는 1단계 들여쓰기만 지원 / one nesting level only.

## Step 3. 미리보기 / Preview

저장 전 구조를 확인한다 (토큰 불필요). / Verify structure before saving (no token needed):

```bash
python3 scripts/add_tasks.py tasks.json --dry-run
```

## Step 4. Google Tasks에 저장 / Save to Google Tasks

```bash
python3 scripts/add_tasks.py tasks.json
```

- 최초 1회 OAuth 토큰 발급 필요 → `references/setup.md` 참고.
  One-time OAuth token required → see `references/setup.md`.
- 토큰 경로 / token path: `--token`, 환경변수 `GOOGLE_TASKS_TOKEN`,
  또는 기본값 `~/.config/google-tasks/token.json`.

## Step 5. 결과 보고 / Report back

저장 후 사용자에게 아래를 보고한다 / After saving, report:
1. 저장된 **목록 이름**과 **항목 개수** / list name and item count.
2. 정리된 체크리스트 표 (국문/영문) / the cleaned checklist table (KO/EN).
3. 교정한 부분이 있으면 명시 (음성 오타 복원 등) / note any corrections made.

---

## 커넥터가 없을 때 / When no connector/token is available

토큰을 아직 못 만든 상황이면: / If a token isn't set up yet:
1. `--dry-run`으로 정리 결과를 먼저 보여주고, / show the `--dry-run` result first, then
2. `references/setup.md`의 3단계 발급 절차를 안내한다. / guide the 3-step setup.
3. 그동안 정리된 JSON(`tasks.json`)은 파일로 남겨 나중에 그대로 저장 가능.
   Keep the organized `tasks.json` so it can be pushed later unchanged.
