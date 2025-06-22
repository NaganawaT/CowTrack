import pandas as pd
import os

def analyze_cow_list():
    """飼養牛一覧.xlsxの内容を詳細に分析する"""
    print("=== 飼養牛一覧.xlsxの詳細分析 ===")
    
    try:
        filename = "飼養牛一覧.xlsx"
        if not os.path.exists(filename):
            print(f"ファイルが見つかりません: {filename}")
            return
        
        # シート名を取得
        excel_file = pd.ExcelFile(filename)
        print(f"シート数: {len(excel_file.sheet_names)}")
        print("シート名:")
        for i, sheet_name in enumerate(excel_file.sheet_names, 1):
            print(f"  {i}. {sheet_name}")
        
        # 各シートの内容を詳細に確認
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- シート: {sheet_name} ---")
            df = pd.read_excel(filename, sheet_name=sheet_name)
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            print("列名:")
            for col in df.columns:
                print(f"  - {col}")
            
            # すべてのデータを表示
            if len(df) > 0:
                print("\n全データ:")
                print(df.to_string(index=False))
            else:
                print("データがありません")
                
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    analyze_cow_list() 