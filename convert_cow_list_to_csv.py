import pandas as pd
import os
from datetime import datetime
import numpy as np

def convert_cow_list_to_csv():
    """飼養牛一覧.xlsxをCowTrackアプリ用のCSV形式に変換する"""
    print("=== 飼養牛一覧.xlsxをCowTrackアプリ用CSVに変換 ===")
    
    try:
        input_file = "飼養牛一覧.xlsx"
        output_file = "cowtrack_import_data.csv"
        
        if not os.path.exists(input_file):
            print(f"ファイルが見つかりません: {input_file}")
            return
        
        # Excelファイルを読み込み
        df = pd.read_excel(input_file)
        print(f"元データ行数: {len(df)}")
        print(f"元データ列数: {len(df.columns)}")
        print("元データ列名:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col}")
        
        # データの最初の数行を表示して列の内容を確認
        print("\n元データの最初の5行:")
        print(df.head().to_string())
        
        # 列の内容を分析して適切なマッピングを決定
        print("\n=== 列の内容分析 ===")
        
        # 各列の最初の非NaN値を確認
        for i, col in enumerate(df.columns):
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                sample_values = non_null_values.head(3).tolist()
                print(f"列 {i} ({col}): {sample_values}")
        
        # ユーザーに列のマッピングを確認
        print("\n=== 列マッピングの確認 ===")
        print("CowTrackアプリで必要な列:")
        print("  - cow_number: 牛個体識別番号（10桁）")
        print("  - shed_code: 牛舎番号")
        print("  - intake_date: 導入日（YYYY-MM-DD形式）")
        print("  - gender: 性別（female/castrated）")
        print("  - origin_region: 導入元地域（北海道/曽於/関/飛騨/自家）")
        print("  - status: ステータス（active/moved/sold/dead）")
        
        # 手動で列マッピングを設定（分析結果に基づいて）
        column_mapping = {
            'cow_number': '個体識別番号',  # 列5
            'shed_code': '牛房',          # 列1
            'intake_date': '導入日',      # 列8
            'gender': '性別',             # 列6
            'origin_region': '購入先'     # 列9
        }
        
        print(f"\n設定された列マッピング: {column_mapping}")
        
        # 変換処理
        converted_data = []
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 必須フィールドのチェック
                cow_number = None
                shed_code = None
                intake_date = None
                
                # 牛番号の取得
                if 'cow_number' in column_mapping:
                    cow_number = str(row[column_mapping['cow_number']])
                    if pd.isna(cow_number) or cow_number == 'nan':
                        continue  # 牛番号が空の行はスキップ
                    # 10桁に調整（先頭に0を追加）
                    if len(cow_number) < 10:
                        cow_number = cow_number.zfill(10)
                    elif len(cow_number) > 10:
                        cow_number = cow_number[-10:]  # 後ろ10桁を取得
                else:
                    continue  # 牛番号が特定できない行はスキップ
                
                # 牛舎番号の取得
                if 'shed_code' in column_mapping:
                    shed_code = str(row[column_mapping['shed_code']])
                    if pd.isna(shed_code) or shed_code == 'nan':
                        shed_code = '0000'  # デフォルト値
                else:
                    shed_code = '0000'  # デフォルト値
                
                # 導入日の取得
                if 'intake_date' in column_mapping:
                    date_value = row[column_mapping['intake_date']]
                    if pd.notna(date_value):
                        if isinstance(date_value, str):
                            # 文字列の場合はパース
                            try:
                                intake_date = datetime.strptime(date_value, '%Y/%m/%d').strftime('%Y-%m-%d')
                            except:
                                intake_date = '2024-01-01'  # デフォルト値
                        else:
                            # datetime型の場合は直接変換
                            intake_date = date_value.strftime('%Y-%m-%d')
                    else:
                        intake_date = '2024-01-01'  # デフォルト値
                else:
                    intake_date = '2024-01-01'  # デフォルト値
                
                # 性別の取得
                gender = 'female'  # デフォルト
                if 'gender' in column_mapping:
                    gender_value = str(row[column_mapping['gender']]).lower()
                    if '去勢' in gender_value or 'castrated' in gender_value:
                        gender = 'castrated'
                    elif 'オス' in gender_value or 'male' in gender_value:
                        gender = 'castrated'  # オスは去勢として扱う
                    elif 'メス' in gender_value or 'female' in gender_value:
                        gender = 'female'
                
                # 導入元地域の取得
                origin_region = '自家'  # デフォルト
                if 'origin_region' in column_mapping:
                    origin_value = str(row[column_mapping['origin_region']])
                    if '北海道' in origin_value:
                        origin_region = '北海道'
                    elif '曽於' in origin_value:
                        origin_region = '曽於'
                    elif '関' in origin_value:
                        origin_region = '関'
                    elif '飛騨' in origin_value:
                        origin_region = '飛騨'
                    elif '自家' in origin_value:
                        origin_region = '自家'
                
                # ステータス（デフォルトでactive）
                status = 'active'
                
                # 変換されたデータを追加
                converted_data.append({
                    'cow_number': cow_number,
                    'shed_code': shed_code,
                    'intake_date': intake_date,
                    'gender': gender,
                    'origin_region': origin_region,
                    'status': status
                })
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"行 {index + 1} の変換エラー: {str(e)}")
        
        # 変換結果をCSVファイルに保存
        if converted_data:
            result_df = pd.DataFrame(converted_data)
            result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            print(f"\n=== 変換完了 ===")
            print(f"成功: {success_count}件")
            print(f"エラー: {error_count}件")
            print(f"出力ファイル: {output_file}")
            
            # 変換結果のサンプルを表示
            print(f"\n変換結果の最初の10行:")
            print(result_df.head(10).to_string(index=False))
            
            # 統計情報
            print(f"\n=== 統計情報 ===")
            print(f"性別分布:")
            print(result_df['gender'].value_counts())
            print(f"\n導入元地域分布:")
            print(result_df['origin_region'].value_counts())
            print(f"\n牛舎番号分布:")
            print(result_df['shed_code'].value_counts().head(10))
            
        else:
            print("変換可能なデータが見つかりませんでした。")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    convert_cow_list_to_csv() 