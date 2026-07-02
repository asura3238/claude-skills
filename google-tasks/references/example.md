# 예제 / Worked Example — 수입 검수 체크리스트

음성으로 받아쓴 원문(오타/중복 포함)을 정리해 Google Tasks 항목으로 만드는 예시입니다.
Example of turning a messy voice transcript into clean Google Tasks items.

## 원본 음성 받아쓰기 / Raw voice transcript (KO)

> "fx 백십에 수입해야 되는데 거기서 확인해야 될 것들이 있어. 말통이 20킬로그램 15리터짜리가
> 들어오는데, 넥 뚜껑이 있는지 실링이 있는지 뒤집어도 흐르지 않는지, 혹시 재포장 했을 때 —
> 재포장이라는 건 뚜껑만 열었다 다시 닫았을 때 — 그때 샘이 있는지 없는지 실링이 있는지
> 이것도 확인해야 되거든."

## 정리 규칙 / Cleanup rules

- 음성 오타 교정: "시복십오→15", "르세스 넥면→다음 공정" 등 문맥으로 복원.
  Fix speech-to-text errors from context.
- 한 검수 대상 = 부모 태스크, 확인 항목 = 서브태스크.
  One inspection target = parent task; each check = subtask.
- 중복(실링 언급 2회)은 "초기/재포장 후"로 구분해 보존.
  Keep duplicates by distinguishing context (initial vs. after repackaging).

## 정리 결과 / Cleaned result

**부모 / Parent:** fx백십 입고 검수 – 말통 20kg / 15L
(fx-baeksip inbound inspection – jerrycan 20kg / 15L)

| # | 확인 항목 (KO) | Check item (EN) |
|---|----------------|-----------------|
| 1 | 넥(neck) 뚜껑이 있는지 | Neck cap present |
| 2 | 실링(sealing)이 되어 있는지 | Sealing intact |
| 3 | 뒤집어도 새지(흐르지) 않는지 | No leak when inverted |
| 4 | 재포장(뚜껑만 열었다 닫음) 시 샘(누수) 여부 | Leak check after reopen-and-reclose |
| 5 | 재포장 후에도 실링이 유지되는지 | Sealing still intact after repackaging |

대응 JSON은 `example_tasks.json` 참고 / see `example_tasks.json`.
