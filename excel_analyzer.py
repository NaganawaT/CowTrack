import pandas as pd
import os

def analyze_excel_file(filename):
    """Excelファイルの内容を分析する"""
    print(f"\n=== {filename} ===")
    try:
        # ファイルの存在確認
        if not os.path.exists(filename):
            print(f"ファイルが見つかりません: {filename}")
            return
        
        # シート名を取得
        excel_file = pd.ExcelFile(filename)
        print(f"シート数: {len(excel_file.sheet_names)}")
        print("シート名:")
        for i, sheet_name in enumerate(excel_file.sheet_names, 1):
            print(f"  {i}. {sheet_name}")
        
        # 各シートの内容を確認
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- シート: {sheet_name} ---")
            df = pd.read_excel(filename, sheet_name=sheet_name)
            print(f"行数: {len(df)}")
            print(f"列数: {len(df.columns)}")
            print("列名:")
            for col in df.columns:
                print(f"  - {col}")
            
            # 最初の5行を表示
            if len(df) > 0:
                print("\n最初の5行:")
                print(df.head().to_string())
            else:
                print("データがありません")
                
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def main():
    """メイン関数"""
    print("Excelファイルの内容を分析します...")
    
    # 分析対象のファイル
    files = [
        "要件定義書v0.1.xlsx",
        "基本設計書v0.1.xlsx", 
        "DB定義書v0.2.xlsx",
        "API設計書v0.2.xlsx"
    ]
    
    for filename in files:
        analyze_excel_file(filename)

if __name__ == "__main__":
    main()