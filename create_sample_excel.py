import pandas as pd
import os

# サンプルデータ（実際のケースを想定）
data = {
    '個体識別番号': ['1234567890', '123456789', '12345678', '1234567', '123456'],  # 先頭ゼロが削除されたケース
    '牛房': ['A001', 'A002', 'A003', 'B001', 'B002'],
    '導入日': ['2024/01/15', '2024/01/16', '2024/01/17', '2024/01/18', '2024/01/19'],
    '性別': ['オス', 'メス', '去勢', 'オス', 'メス'],
    '購入先': ['関家畜流通センター', '曽於中央家畜市場', '自家産', '南北海道家畜市場', '飛騨家畜流通センター'],
    'ステータス': ['active', 'active', 'active', 'active', 'active']
}

# DataFrameを作成
df = pd.DataFrame(data)

# ディレクトリを作成
os.makedirs('excel_imports', exist_ok=True)

# Excelファイルを保存
output_file = 'excel_imports/飼養牛一覧.xlsx'
df.to_excel(output_file, index=False)

print(f'サンプルファイルを作成しました: {output_file}')
print(f'データ件数: {len(df)}件')
print('列名:', list(df.columns))
print('個体識別番号の例:', df['個体識別番号'].tolist())
print('注意: 先頭のゼロが削除された個体識別番号も含まれています') 