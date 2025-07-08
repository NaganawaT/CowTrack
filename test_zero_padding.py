import pandas as pd

# テストデータ
test_data = {
    '個体識別番号': ['1234567890', '123456789', '12345678', '1234567', '123456', '12345', '1234', '123', '12', '1'],
    '牛房': ['A001', 'A002', 'A003', 'B001', 'B002', 'C001', 'C002', 'D001', 'D002', 'E001'],
    '性別': ['メス', '去勢', 'メス', '去勢', 'メス', 'メス', '去勢', 'メス', '去勢', 'メス']
}

df = pd.DataFrame(test_data)

print("=== ゼロ埋めテスト ===")
print("元のデータ:")
for i, row in df.iterrows():
    original = str(row['個体識別番号'])
    padded = original.zfill(10)
    print(f"行{i+1}: {original} -> {padded}")

print("\n=== 処理後のデータ例 ===")
for i, row in df.iterrows():
    cow_number = str(row['個体識別番号']).strip()
    if cow_number.isdigit():
        cow_number = cow_number.zfill(10)
        print(f"個体識別番号: {cow_number}, 牛房: {row['牛房']}, 性別: {row['性別']}")
    else:
        print(f"エラー: {cow_number} は数字ではありません") 