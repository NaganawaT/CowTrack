import pandas as pd
from datetime import datetime
from django.core.exceptions import ValidationError
from .models import Cow
import os

def classify_shed_code(shed_code):
    """
    牛舎番号を分類する関数
    
    Args:
        shed_code (str): 牛舎番号
        
    Returns:
        str: 分類名（'導入牛舎', '肥育牛舎', 'その他'）
    """
    if not shed_code:
        return 'その他'
    
    # 導入牛舎: 41番台、42番台、4000台
    if shed_code.startswith('41') or shed_code.startswith('42') or shed_code == '4000':
        return '導入牛舎'
    
    # 肥育牛舎: 数字で始まる牛舎番号（導入牛舎以外）
    if shed_code[0].isdigit():
        return '肥育牛舎'
    
    # その他: 文字で始まる牛舎番号
    return 'その他'

def get_shed_subcategory(shed_code):
    """
    牛舎番号のサブカテゴリを取得する関数
    
    Args:
        shed_code (str): 牛舎番号
        
    Returns:
        str: サブカテゴリ名
    """
    if not shed_code:
        return 'その他'
    
    # 導入牛舎のサブカテゴリ
    if shed_code.startswith('41'):
        return '41番台'
    elif shed_code.startswith('42'):
        return '42番台'
    elif shed_code == '4000':
        return '4000台'
    
    # 肥育牛舎のサブカテゴリ（先頭2桁でグループ化）
    if shed_code[0].isdigit() and len(shed_code) >= 2:
        return f"{shed_code[:2]}番台"
    
    # その他
    return 'その他'

def get_shed_groups():
    """
    牛舎番号をグループ化して返す関数
    
    Returns:
        dict: グループ別の牛舎番号リスト
    """
    from .models import Cow
    
    sheds = Cow.objects.values_list('shed_code', flat=True).distinct()
    groups = {
        '導入牛舎': [],
        '肥育牛舎': [],
        'その他': []
    }
    
    for shed in sheds:
        if shed:
            category = classify_shed_code(shed)
            groups[category].append(shed)
    
    # 各グループ内でソート
    for category in groups:
        groups[category].sort()
    
    return groups

def get_shed_hierarchy():
    """
    牛舎番号を階層構造で返す関数（3段階選択用）
    
    Returns:
        dict: 階層構造の牛舎番号
    """
    from .models import Cow
    
    sheds = Cow.objects.values_list('shed_code', flat=True).distinct()
    hierarchy = {
        '導入牛舎': {
            '41番台': [],
            '42番台': [],
            '4000台': []
        },
        '肥育牛舎': {},
        'その他': []
    }
    
    for shed in sheds:
        if not shed:
            continue
            
        category = classify_shed_code(shed)
        subcategory = get_shed_subcategory(shed)
        
        if category == '導入牛舎':
            if subcategory in hierarchy['導入牛舎']:
                hierarchy['導入牛舎'][subcategory].append(shed)
        elif category == '肥育牛舎':
            if subcategory not in hierarchy['肥育牛舎']:
                hierarchy['肥育牛舎'][subcategory] = []
            hierarchy['肥育牛舎'][subcategory].append(shed)
        else:  # その他
            hierarchy['その他'].append(shed)
    
    # 各グループ内でソート
    for subcategory in hierarchy['導入牛舎']:
        hierarchy['導入牛舎'][subcategory].sort()
    
    for subcategory in hierarchy['肥育牛舎']:
        hierarchy['肥育牛舎'][subcategory].sort()
    
    hierarchy['その他'].sort()
    
    return hierarchy

def get_shed_display_name(shed_code):
    """
    牛舎番号の表示名を取得する関数
    
    Args:
        shed_code (str): 牛舎番号
        
    Returns:
        str: 表示名
    """
    if not shed_code:
        return ''
    
    category = classify_shed_code(shed_code)
    
    if category == '導入牛舎':
        if shed_code.startswith('41'):
            return f'導入牛舎（41番台）- {shed_code}'
        elif shed_code.startswith('42'):
            return f'導入牛舎（42番台）- {shed_code}'
        else:
            return f'導入牛舎（4000台）- {shed_code}'
    elif category == '肥育牛舎':
        return f'肥育牛舎 - {shed_code}'
    else:
        return f'その他 - {shed_code}'

def get_shed_hierarchy_combined():
    """
    牛舎番号を階層構造で返す関数（番台と牛舎番号を一つのプルダウンにまとめる用）
    
    Returns:
        dict: 階層構造の牛舎番号（番台と牛舎番号を結合）
    """
    from .models import Cow
    
    sheds = Cow.objects.values_list('shed_code', flat=True).distinct()
    hierarchy = {
        '導入牛舎': [],
        '肥育牛舎': [],
        'その他': []
    }
    
    for shed in sheds:
        if not shed:
            continue
            
        category = classify_shed_code(shed)
        subcategory = get_shed_subcategory(shed)
        
        # 番台と牛舎番号を結合した表示名を作成
        if category == '導入牛舎':
            if subcategory == '41番台':
                display_name = f'41番台 - {shed}'
            elif subcategory == '42番台':
                display_name = f'42番台 - {shed}'
            elif subcategory == '4000台':
                display_name = f'4000台 - {shed}'
            else:
                display_name = f'{subcategory} - {shed}'
            hierarchy['導入牛舎'].append({
                'shed_code': shed,
                'display_name': display_name,
                'subcategory': subcategory
            })
        elif category == '肥育牛舎':
            display_name = f'{subcategory} - {shed}'
            hierarchy['肥育牛舎'].append({
                'shed_code': shed,
                'display_name': display_name,
                'subcategory': subcategory
            })
        else:  # その他
            hierarchy['その他'].append({
                'shed_code': shed,
                'display_name': f'その他 - {shed}',
                'subcategory': 'その他'
            })
    
    # 各グループ内でソート
    for category in hierarchy:
        hierarchy[category].sort(key=lambda x: (x['subcategory'], x['shed_code']))
    
    return hierarchy

def convert_purchase_source_to_region(purchase_source):
    """
    購入先を導入元地域に変換する
    
    Args:
        purchase_source (str): 購入先の文字列
    
    Returns:
        str: 導入元地域
    """
    if not purchase_source or purchase_source == 'nan':
        return ''
    
    purchase_source = str(purchase_source).strip()
    
    # 購入先から導入元地域への変換マッピング
    conversion_map = {
        '関家畜流通センター': '関',
        '曽於中央家畜市場': '曽於',
        '自家産': '自家産',
        '南北海道家畜市場': '北海道',
        '飛騨家畜流通センター': '飛騨'
    }
    
    # 完全一致で検索
    if purchase_source in conversion_map:
        return conversion_map[purchase_source]
    
    # 部分一致で検索（より柔軟な対応）
    for key, value in conversion_map.items():
        if key in purchase_source or purchase_source in key:
            return value
    
    # 変換できない場合は元の値をそのまま返す
    return purchase_source

def process_excel_file(file, skip_duplicates=True, update_existing=False, skip_check_digit=False):
    """
    Excelファイルを処理して牛のデータを一括登録する
    
    Args:
        file: アップロードされたExcelファイル
        skip_duplicates: 重複データをスキップするかどうか
        update_existing: 既存データを更新するかどうか
        skip_check_digit: チェックデジット検証をスキップするかどうか
    
    Returns:
        dict: 処理結果の詳細
    """
    results = {
        'total_rows': 0,
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': [],
        'success_messages': []
    }
    
    try:
        # Excelファイルを読み込み
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl')
        elif file.name.endswith('.xls'):
            df = pd.read_excel(file, engine='xlrd')
        else:
            raise ValidationError('サポートされていないファイル形式です。.xlsxまたは.xlsファイルを使用してください。')
        
        results['total_rows'] = len(df)
        
        # 列名のマッピング
        column_mapping = {
            '個体識別番号': 'cow_number',
            '牛房': 'shed_code',
            '牛舎番号': 'shed_code',  # 牛房と牛舎番号の両方に対応
            '導入日': 'intake_date',
            '性別': 'gender',
            '導入元地域': 'origin_region',
            'ステータス': 'status'
        }
        
        # 実際の列名を確認
        actual_columns = list(df.columns)
        required_columns = ['個体識別番号']
        missing_columns = [col for col in required_columns if col not in actual_columns]
        
        # 牛房または牛舎番号のいずれかが必要
        shed_column_found = '牛房' in actual_columns or '牛舎番号' in actual_columns
        if not shed_column_found:
            missing_columns.append('牛房または牛舎番号')
        
        if missing_columns:
            raise ValidationError(f'必要な列が不足しています: {", ".join(missing_columns)}')
        
        # 各行を処理
        for index, row in df.iterrows():
            try:
                # データの取得と検証
                cow_number = str(row['個体識別番号']).strip()
                
                # 牛房または牛舎番号から値を取得
                if '牛舎番号' in df.columns and pd.notna(row['牛舎番号']):
                    shed_code = str(row['牛舎番号']).strip()
                elif '牛房' in df.columns and pd.notna(row['牛房']):
                    shed_code = str(row['牛房']).strip()
                else:
                    shed_code = ''
                
                # 必須項目の検証
                if not cow_number or cow_number == 'nan':
                    results['errors'].append(f'行{index + 2}: 個体識別番号が空です')
                    continue
                
                if not shed_code or shed_code == 'nan':
                    results['errors'].append(f'行{index + 2}: 牛舎番号が空です')
                    continue
                
                # 個体識別番号を10桁にゼロ埋め
                if cow_number.isdigit():
                    cow_number = cow_number.zfill(10)  # 10桁にゼロ埋め
                else:
                    results['errors'].append(f'行{index + 2}: 個体識別番号は数字である必要があります: {cow_number}')
                    continue
                
                # 個体識別番号の形式チェック（10桁の数字）
                if len(cow_number) != 10:
                    results['errors'].append(f'行{index + 2}: 個体識別番号は10桁である必要があります（ゼロ埋め後）: {cow_number}')
                    continue
                
                # チェックデジット検証
                if not skip_check_digit and not validate_cattle_id(cow_number):
                    # チェックデジットの詳細計算
                    body_number = cow_number[:9]
                    actual_check_digit = int(cow_number[9])
                    calculated_check_digit = calculate_check_digit(body_number)
                    
                    # 詳細なエラーメッセージを作成
                    error_detail = f'行{index + 2}: 個体識別番号のチェックデジットが無効です\n'
                    error_detail += f'  個体識別番号: {cow_number}\n'
                    error_detail += f'  本体番号: {body_number}\n'
                    error_detail += f'  実際のチェックデジット: {actual_check_digit}\n'
                    error_detail += f'  計算されたチェックデジット: {calculated_check_digit}\n'
                    error_detail += f'  牛舎番号: {shed_code}\n'
                    if '導入日' in df.columns and pd.notna(row['導入日']):
                        error_detail += f'  導入日: {row["導入日"]}\n'
                    if '性別' in df.columns and pd.notna(row['性別']):
                        error_detail += f'  性別: {row["性別"]}\n'
                    if '導入元地域' in df.columns and pd.notna(row['導入元地域']):
                        error_detail += f'  導入元地域: {row["導入元地域"]}\n'
                    error_detail += f'  → 個体識別番号が正しいか確認してください。\n'
                    error_detail += f'  → チェックデジット検証をスキップする場合は、オプションを有効にしてください。'
                    
                    results['errors'].append(error_detail)
                    continue
                
                # オプション項目の取得
                intake_date = None
                if '導入日' in df.columns and pd.notna(row['導入日']):
                    try:
                        if isinstance(row['導入日'], str):
                            intake_date = datetime.strptime(row['導入日'], '%Y/%m/%d').date()
                        else:
                            intake_date = row['導入日'].date()
                    except:
                        results['errors'].append(f'行{index + 2}: 導入日の形式が正しくありません')
                
                # 性別の変換
                gender = 'female'  # デフォルト
                if '性別' in df.columns and pd.notna(row['性別']):
                    gender_text = str(row['性別']).strip()
                    if gender_text in ['オス', 'male']:
                        gender = 'male'
                    elif gender_text in ['メス', 'female']:
                        gender = 'female'
                    elif gender_text in ['去勢', 'castrated']:
                        gender = 'castrated'
                    else:
                        results['errors'].append(f'行{index + 2}: 性別の値が正しくありません: {gender_text} (オス、メス、去勢のいずれかを入力してください)')
                        continue
                
                # 導入元地域の処理（購入先から変換）
                origin_region = ''
                if '購入先' in df.columns and pd.notna(row['購入先']):
                    # 購入先から導入元地域に変換
                    origin_region = convert_purchase_source_to_region(row['購入先'])
                elif '導入元地域' in df.columns and pd.notna(row['導入元地域']):
                    # 直接導入元地域が指定されている場合
                    origin_region = str(row['導入元地域']).strip()
                else:
                    origin_region = ''
                
                # ステータスの自動設定
                status = row.get('ステータス', '')
                filename = os.path.basename(getattr(file, 'name', ''))
                if (not status or str(status).strip() == '' or str(status).lower() == 'nan') and filename.endswith('飼養牛一覧.xlsx'):
                    status = 'active'
                if status not in ['active', 'inactive']:
                    status = 'active'
                
                # 既存データの確認
                existing_cow = Cow.objects.filter(cow_number=cow_number).first()
                
                if existing_cow:
                    if skip_duplicates and not update_existing:
                        results['skipped'] += 1
                        results['success_messages'].append(f'個体識別番号 {cow_number}: 既に登録されているためスキップしました')
                        continue
                    elif update_existing:
                        # 既存データを更新
                        existing_cow.shed_code = shed_code
                        if intake_date:
                            existing_cow.intake_date = intake_date
                        existing_cow.gender = gender
                        existing_cow.origin_region = origin_region
                        existing_cow.status = status
                        existing_cow.save()
                        results['updated'] += 1
                        results['success_messages'].append(f'個体識別番号 {cow_number}: 更新しました')
                    else:
                        results['errors'].append(f'行{index + 2}: 個体識別番号 {cow_number} は既に登録されています')
                        continue
                else:
                    # 新規データを作成
                    Cow.objects.create(
                        cow_number=cow_number,
                        shed_code=shed_code,
                        intake_date=intake_date,
                        gender=gender,
                        origin_region=origin_region,
                        status=status
                    )
                    results['created'] += 1
                    results['success_messages'].append(f'個体識別番号 {cow_number}: 登録しました')
                
            except Exception as e:
                results['errors'].append(f'行{index + 2}: {str(e)}')
        
        return results
        
    except Exception as e:
        results['errors'].append(f'ファイル処理エラー: {str(e)}')
        return results

def get_shed_groups():
    """牛舎別の牛の数を取得"""
    from django.db.models import Count
    return Cow.objects.values('shed_code').annotate(count=Count('id')).order_by('shed_code')

def calculate_check_digit(body_number):
    """
    牛個体識別番号のチェックデジットを計算する（モジュラス10、重み3,1方式）
    
    Args:
        body_number: 9桁の本体番号（文字列）
    
    Returns:
        int: チェックデジット（0-9）
    """
    if len(body_number) != 9 or not body_number.isdigit():
        raise ValueError("本体番号は9桁の数字である必要があります")
    
    # 重み配列（右から順番、3, 1, 3, 1, 3, 1, 3, 1, 3）
    weights = [3, 1, 3, 1, 3, 1, 3, 1, 3]
    
    # 各桁 × 重み の合計を計算
    total = 0
    for i, digit in enumerate(body_number):
        total += int(digit) * weights[i]
    
    # 10で割った余りを計算
    remainder = total % 10
    
    # チェックデジットを計算
    if remainder == 0:
        check_digit = 0
    else:
        check_digit = 10 - remainder
    
    return check_digit

def validate_cattle_id(cattle_id):
    """
    牛個体識別番号のチェックデジットを検証する
    
    Args:
        cattle_id: 10桁の個体識別番号（文字列）
    
    Returns:
        bool: 有効な場合はTrue、無効な場合はFalse
    """
    if len(cattle_id) != 10 or not cattle_id.isdigit():
        return False
    
    body_number = cattle_id[:9]  # 最初の9桁
    expected_check_digit = int(cattle_id[9])  # 最後の1桁
    
    try:
        calculated_check_digit = calculate_check_digit(body_number)
        return calculated_check_digit == expected_check_digit
    except ValueError:
        return False

def generate_valid_cattle_id(body_number):
    """
    9桁の本体番号から有効な10桁の個体識別番号を生成する
    
    Args:
        body_number: 9桁の本体番号（文字列）
    
    Returns:
        str: 10桁の有効な個体識別番号
    """
    check_digit = calculate_check_digit(body_number)
    return body_number + str(check_digit)

def preview_excel_file(file):
    """
    Excelファイルをプレビューし、チェックデジット不一致牛の詳細リストを返す
    Returns:
        dict: {'valid': [正常牛リスト], 'invalid': [不一致牛詳細リスト], 'total_rows': int}
    """
    results = {
        'valid': [],
        'invalid': [],
        'total_rows': 0
    }
    if file.name.endswith('.xlsx'):
        df = pd.read_excel(file, engine='openpyxl')
    elif file.name.endswith('.xls'):
        df = pd.read_excel(file, engine='xlrd')
    else:
        raise ValidationError('サポートされていないファイル形式です。.xlsxまたは.xlsファイルを使用してください。')
    results['total_rows'] = len(df)
    for index, row in df.iterrows():
        cow_number = str(row['個体識別番号']).strip()
        
        # 牛房または牛舎番号から値を取得
        if '牛舎番号' in df.columns and pd.notna(row['牛舎番号']):
            shed_code = str(row['牛舎番号']).strip()
        elif '牛房' in df.columns and pd.notna(row['牛房']):
            shed_code = str(row['牛房']).strip()
        else:
            shed_code = ''
        if cow_number.isdigit():
            cow_number = cow_number.zfill(10)
        else:
            continue
        if len(cow_number) != 10:
            continue
        # 詳細情報取得
        detail = {
            'row': index + 2,
            'cow_number': cow_number,
            'body_number': cow_number[:9],
            'actual_check_digit': cow_number[9],
            'calculated_check_digit': str(calculate_check_digit(cow_number[:9])),
            'shed_code': shed_code,
            'intake_date': str(row['導入日']) if '導入日' in df.columns and pd.notna(row['導入日']) else '',
            'gender': str(row['性別']) if '性別' in df.columns and pd.notna(row['性別']) else '',
            'origin_region': convert_purchase_source_to_region(row['購入先']) if '購入先' in df.columns and pd.notna(row['購入先']) else (str(row['導入元地域']) if '導入元地域' in df.columns and pd.notna(row['導入元地域']) else ''),
            'status': str(row['ステータス']) if 'ステータス' in df.columns and pd.notna(row['ステータス']) else '',
        }
        if validate_cattle_id(cow_number):
            results['valid'].append(detail)
        else:
            results['invalid'].append(detail)
    return results

def register_cows_from_preview(cow_details):
    """
    プレビュー画面で選択された牛のみ登録する
    Args:
        cow_details: [{...}]  # preview_excel_fileで得た辞書のリスト
    Returns:
        dict: {'created': int, 'errors': [str]}
    """
    from .models import Cow
    from datetime import datetime
    results = {'created': 0, 'errors': []}
    for detail in cow_details:
        try:
            cow_number = detail['cow_number']
            shed_code = detail['shed_code']
            intake_date = None
            if detail.get('intake_date'):
                try:
                    intake_date = datetime.strptime(detail['intake_date'], '%Y/%m/%d').date()
                except:
                    pass
            gender = detail.get('gender', 'female')
            origin_region = detail.get('origin_region', '')
            status = detail.get('status', 'active')
            if not Cow.objects.filter(cow_number=cow_number).exists():
                Cow.objects.create(
                    cow_number=cow_number,
                    shed_code=shed_code,
                    intake_date=intake_date,
                    gender=gender,
                    origin_region=origin_region,
                    status=status
                )
                results['created'] += 1
            else:
                results['errors'].append(f'{cow_number} は既に登録されています')
        except Exception as e:
            results['errors'].append(f'{detail.get("cow_number", "")}: {str(e)}')
    return results 