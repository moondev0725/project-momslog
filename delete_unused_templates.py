import os

# 삭제할 파일 목록
files_to_delete = [
    r"c:\workspace\d0103\mompjt\main\templates\main.html",
    r"c:\workspace\d0103\mompjt\main\templates\main\map.html",
    r"c:\workspace\d0103\mompjt\board\templates\board\flea_detail_new.html",
    r"c:\workspace\d0103\mompjt\board\templates\board\upload_example.html"
]

for file_path in files_to_delete:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"✓ 삭제됨: {file_path}")
    else:
        print(f"✗ 파일 없음: {file_path}")

print("\n완료!")
