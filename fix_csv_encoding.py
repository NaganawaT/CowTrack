import pandas as pd

def fix_csv_encoding():
    """CSVファイルのエンコーディングを修正する"""
    print("=== CSVファイルのエンコーディング修正 ===")
    
    try:
        # 元のCSVファイルを読み込み
        df = pd.read_csv('cowtrack_import_data.csv', encoding='utf-8-sig')
        
        # BOMなしのUTF-8で保存し直し
        df.to_csv('cowtrack_import_data_fixed.csv', index=False, encoding='utf-8')
        
        print("エンコーディング修正完了: cowtrack_import_data_fixed.csv")
        
        # 修正後のファイルの最初の数行を確認
        print("\n修正後のファイルの最初の5行:")
        print(df.head().to_string(index=False))
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_csv_encoding() 