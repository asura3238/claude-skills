---
name: weekly-forecast-fcw
description: |
  FCW(FCW Korea) TIX-20A / TIX-10C_SV 품목의 Weekly Forecast 통합 관리표를 자동 생성하는 스킬.
  이닉스 수요예측(TIX-20A), 지맥스 수요예측(TIX-10C_SV), 구매마스터 파일을 입력받아
  Weekly_Forecast 시트에 예상수요 / 예상입고 / 기말재고를 계산하고 작성한다.

  다음 표현이 포함된 요청에 반드시 이 스킬을 사용할 것:
  - "weekly forecast 작성", "주간 forecast", "통합 관리표", "forecast 시트"
  - "이닉스/지맥스 forecast로 작성", "구매마스터 참고해서 forecast"
  - "예상수요 채워줘", "기말재고 마이너스 안 나오게"
  - "Weekly_Forecast_시트 작성", "수요예측 반영해줘"
---

# Weekly Forecast FCW 스킬

## 개요

이닉스 수요예측(TIX-20A 수요/입고), 지맥스 수요예측(TIX-10C_SV 수요), 구매마스터(예상 입고 일정)를
종합하여 Weekly_Forecast 시트의 예상수요 / 예상입고 / 기말재고를 자동 작성한다.

### 색상 규칙 (중요)
| 셀 유형 | 색상 | 의미 |
|--------|------|------|
| 예상입고 (데이터 기반) | **파란색** (`0000FF`) | 구매마스터에 근거 있는 입고 |
| 예상입고 (임의 배치) | **노란색** (`FFFF00`) | 기말재고 음수 방지용 임의 입고 (발주 확정 필요) |

---

## 입력 파일

1. **FCWKR_Forecast_통합_관리표.xlsx** — 결과를 작성할 대상 파일
   - `Weekly_Forecast` 시트에 작성
   - 대상 품목: TIX-20A, TIX-10C_SV

2. **이닉스 수요예측** — 메일 또는 이미지/엑셀로 전달
   - 읽어야 할 정보: **TIX-20A** 월별 수요량, 입고요청일, 구매요청수량
   - 이미지로 삽입된 경우: `references/image_extract.md` 참고

3. **지맥스 수요예측** — 메일 또는 이미지/엑셀로 전달
   - 읽어야 할 정보: **TIX-10C_SV** 월별 수요량
   - 주간 수요 = 월별 수요 ÷ 4 (ROUNDDOWN, 마지막 주는 나머지)

4. **구매마스터.xlsx** — 실제 발주/입고 일정
   - 시트: `구매마스터 (FCW)`
   - 읽어야 할 컬럼: 물품명, 물품규격, 수량, Ready date, ETD, ETA, 입고일, 입고일 비고

---

## Step 1. 수요예측 데이터 분석

### 입력 형태별 처리

**메일로 받은 경우**: 메일 본문 또는 첨부 이미지/엑셀에서 수치 추출

**이미지로 삽입된 경우**: xlsx에서 이미지 추출 후 view 툴로 확인
```python
import zipfile

with zipfile.ZipFile('파일명.xlsx', 'r') as z:
    for f in z.namelist():
        if f.startswith('xl/media/'):
            z.extract(f, '/home/claude/')
```

### 이닉스 수요예측 (TIX-20A)
- 월별 소요량(수요) 추출
- 구매요청수량 및 입고요청일 확인
- 주간 수요 = 월별 수요 ÷ 4 (ROUNDDOWN, 마지막 주 나머지)

### 지맥스 수요예측 (TIX-10C_SV)
- 월별 수요량 추출 (비정규증량 행 우선 적용)
- 주간 수요 = 월별 수요 ÷ 4 (ROUNDDOWN, 마지막 주 나머지)

---

## Step 2. 구매마스터에서 입고 일정 파악

`구매마스터 (FCW)` 시트에서 대상 품목 필터링:

| 품목명 | 규격 키워드 |
|--------|------------|
| TIX-20A | 해당 규격 |
| TIX-10C_SV | 해당 규격 |

**입고일 결정 기준** (우선순위):
1. `입고일` 컬럼에 날짜 있으면 해당 날짜
2. `입고일`이 텍스트("5월초", "6월말" 등) → 해당 월의 첫째/마지막 주로 매핑
3. `ETA` 날짜 기준으로 주차 배정
4. `Ready date`만 있으면 약 2주 후 입고로 추정

**주차 매핑**: `references/week_mapping.md` 참고 (W10~W52)

---

## Step 3. 시트 구조 및 수식 규칙

### 시트 구조 (Weekly_Forecast 기준)

```
품목별 4행 구조:
  행 A: 예상수요
  행 B: 재고 (= 전주 기말재고)
  행 C: 예상입고
  행 D: 기말재고
```

⚠️ 실제 행 번호는 파일을 열어 확인 후 적용할 것

### 수식 패턴 (중요)

```
재고[col]     = 전주 기말재고 참조  → 예: =PREV_COL_D
기말재고[col] = 재고[col] + 입고[col] - 수요[col]  ← 반드시 현재 열 수요
```

⚠️ **절대 다음 열 수요를 빼지 말 것** (현재 열 수요 기준)

### 예상수요 수식

```excel
=ROUNDDOWN(월합계/4, 0)              ← 첫째~셋째 주
=월합계 - 첫주 - 둘째주 - 셋째주    ← 마지막 주 (나머지)
```

---

## Step 4. 재고 시뮬레이션 및 입고 배치

### 핵심 로직

```python
inventory = 직전_기말재고  # 기작성된 마지막 기말재고값

for each week:
    inventory = inventory + 입고 - 수요

    if inventory < 0:
        # 해당 주 또는 직전 주에 입고 임의 배치 → 노란색
        # 입고 단위: 기존 입고 패턴 유지
```

### 입고 배치 원칙

1. **구매마스터에 근거 있는 입고** → 해당 주차에 배치, **파란색** (`0000FF`)
2. **임의 배치 입고** (재고 음수 방지) → 음수 발생 직전 주에 배치, **노란색** (`FFFF00`)
3. 기존 입고 패턴 단위 유지
4. 동일 품목·동일 주차 중복 입고 금지

---

## Step 5. 파일 작성

### openpyxl 작성

```python
import openpyxl
from openpyxl.styles import PatternFill

blue_fill   = PatternFill(start_color='0000FF', end_color='0000FF', fill_type='solid')  # 데이터 기반 입고
yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')  # 임의 배치 입고

wb = openpyxl.load_workbook('대상파일.xlsx')
ws = wb['Weekly_Forecast']

# 예상수요 입력
ws.cell(row=수요행, column=col_idx).value = '=ROUNDDOWN(월합계/4,0)'

# 예상입고 - 데이터 기반 (파란색)
cell = ws.cell(row=입고행, column=col_idx)
cell.value = 입고수량
cell.fill = blue_fill

# 예상입고 - 임의 배치 (노란색)
cell = ws.cell(row=입고행, column=col_idx)
cell.value = 입고수량
cell.fill = yellow_fill

# 재고 수식
ws.cell(row=재고행, column=col_idx).value = f'={prev_col}{기말재고행}'
ws.cell(row=기말재고행, column=col_idx).value = f'={col}{재고행}+{col}{입고행}-{col}{수요행}'

wb.save('결과파일.xlsx')
```

### 수식 재계산

```bash
python3 /mnt/skills/public/xlsx/scripts/recalc.py 결과파일.xlsx 45
```

### 검증 체크리스트

- [ ] 기말재고 음수 없음 (임의 입고 배치 후)
- [ ] 수식 오류 없음 (#REF!, #DIV/0! 등)
- [ ] 데이터 기반 입고 셀 파란색 표시
- [ ] 임의 입고 셀 노란색 표시
- [ ] 중복 입고 없음
- [ ] 합계 열 수식 범위 정확

---

## Step 6. 결과 전달

완성 파일을 `/mnt/user-data/outputs/`에 저장 후 `present_files`로 전달.

완료 후 테오님께 아래 내용 보고:
1. 품목별 입고 계획 요약 표 (주차, 수량, 근거)
2. **파란색**: 구매마스터 기반 입고 항목
3. **노란색**: 임의 배치 입고 항목 (발주 계획 확정 필요)
4. 기말재고 음수 구간 있으면 명시
