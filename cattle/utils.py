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