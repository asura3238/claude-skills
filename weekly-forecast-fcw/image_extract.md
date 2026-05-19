# 엑셀 이미지 추출 방법

## 원리
xlsx 파일은 내부적으로 zip 구조 → `xl/media/` 폴더에 이미지 저장됨

## 추출 코드

```python
import zipfile
import shutil

def extract_images_from_xlsx(xlsx_path, output_dir='/home/claude/'):
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        all_files = z.namelist()
        images = [f for f in all_files if f.startswith('xl/media/')]
        
        # 어느 시트에 어느 이미지인지 확인
        for i, sheet_num in enumerate(['sheet3', 'sheet4'], start=1):
            rel_path = f'xl/worksheets/_rels/{sheet_num}.xml.rels'
            if rel_path in all_files:
                content = z.read(rel_path).decode('utf-8')
                print(f"{sheet_num} → {content}")
        
        # 이미지 추출
        for img_path in images:
            z.extract(img_path, output_dir)
            print(f"추출: {output_dir}{img_path}")
    
    return [f"{output_dir}{img}" for img in images]

# 사용 예
images = extract_images_from_xlsx('/mnt/user-data/uploads/파일명.xlsx')
# → ['/home/claude/xl/media/image1.png', '/home/claude/xl/media/image2.png']
```

## 시트-이미지 매핑 확인

`xl/worksheets/_rels/sheet3.xml.rels` → drawing1.xml → image1.png = 이닉스 forecast
`xl/worksheets/_rels/sheet4.xml.rels` → drawing2.xml → image2.png = 지맥스 forecast

(파일에 따라 시트 번호가 다를 수 있으므로 반드시 rels 파일로 확인)

## 이미지 확인
추출 후 view 툴로 이미지 내용 읽기:
```
view('/home/claude/xl/media/image1.png')  → 이닉스 forecast 내용 확인
view('/home/claude/xl/media/image2.png')  → 지맥스 forecast 내용 확인
```
