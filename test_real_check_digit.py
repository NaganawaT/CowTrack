#!/usr/bin/env python
"""
実際の牛個体識別番号を使って正しいチェックデジット計算方式を特定するテストスクリプト
"""

def test_modulus_10_weight_1_3(cattle_id):
    """
    モジュラス10、重み1,3方式でチェックデジットを計算
    """
    body_number = cattle_id[:9]
    actual_check_digit = int(cattle_id[9])
    
    # 重み配列（右から順番、1, 3, 1, 3, 1, 3, 1, 3, 1）
    weights = [1, 3, 1, 3, 1, 3, 1, 3, 1]
    
    # 各桁 × 重み の合計を計算
    total = 0
    for i, digit in enumerate(body_number):
        total += int(digit) * weights[i]
    
    # 10で割った余りを計算
    remainder = total % 10
    
    # チェックデジットを計算
    if remainder == 0:
        calculated_check_digit = 0
    else:
        calculated_check_digit = 10 - remainder
    
    return calculated_check_digit, actual_check_digit

def test_modulus_11_weight_1_3(cattle_id):
    """
    モジュラス11、重み1,3方式でチェックデジットを計算
    """
    body_number = cattle_id[:9]
    actual_check_digit = int(cattle_id[9])
    
    # 重み配列（右から順番、1, 3, 1, 3, 1, 3, 1, 3, 1）
    weights = [1, 3, 1, 3, 1, 3, 1, 3, 1]
    
    # 各桁 × 重み の合計を計算
    total = 0
    for i, digit in enumerate(body_number):
        total += int(digit) * weights[i]
    
    # 11で割った余りを計算
    remainder = total % 11
    
    # チェックデジットを計算
    if remainder == 0:
        calculated_check_digit = 0
    elif remainder == 1:
        calculated_check_digit = 0  # 1の場合は0
    else:
        calculated_check_digit = 11 - remainder
    
    return calculated_check_digit, actual_check_digit

def test_modulus_10_weight_3_1(cattle_id):
    """
    モジュラス10、重み3,1方式でチェックデジットを計算
    """
    body_number = cattle_id[:9]
    actual_check_digit = int(cattle_id[9])
    
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
        calculated_check_digit = 0
    else:
        calculated_check_digit = 10 - remainder
    
    return calculated_check_digit, actual_check_digit

def test_modulus_11_weight_3_1(cattle_id):
    """
    モジュラス11、重み3,1方式でチェックデジットを計算
    """
    body_number = cattle_id[:9]
    actual_check_digit = int(cattle_id[9])
    
    # 重み配列（右から順番、3, 1, 3, 1, 3, 1, 3, 1, 3）
    weights = [3, 1, 3, 1, 3, 1, 3, 1, 3]
    
    # 各桁 × 重み の合計を計算
    total = 0
    for i, digit in enumerate(body_number):
        total += int(digit) * weights[i]
    
    # 11で割った余りを計算
    remainder = total % 11
    
    # チェックデジットを計算
    if remainder == 0:
        calculated_check_digit = 0
    elif remainder == 1:
        calculated_check_digit = 0  # 1の場合は0
    else:
        calculated_check_digit = 11 - remainder
    
    return calculated_check_digit, actual_check_digit

def test_modulus_10_weight_1_3_reverse(cattle_id):
    """
    モジュラス10、重み1,3方式（左から順番）でチェックデジットを計算
    """
    body_number = cattle_id[:9]
    actual_check_digit = int(cattle_id[9])
    
    # 重み配列（左から順番、1, 3, 1, 3, 1, 3, 1, 3, 1）
    weights = [1, 3, 1, 3, 1, 3, 1, 3, 1]
    
    # 各桁 × 重み の合計を計算
    total = 0
    for i, digit in enumerate(body_number):
        total += int(digit) * weights[i]
    
    # 10で割った余りを計算
    remainder = total % 10
    
    # チェックデジットを計算
    if remainder == 0:
        calculated_check_digit = 0
    else:
        calculated_check_digit = 10 - remainder
    
    return calculated_check_digit, actual_check_digit

def test_modulus_10_weight_3_1_reverse(cattle_id):
    """
    モジュラス10、重み3,1方式（左から順番）でチェックデジットを計算
    """
    body_number = cattle_id[:9]
    actual_check_digit = int(cattle_id[9])
    
    # 重み配列（左から順番、3, 1, 3, 1, 3, 1, 3, 1, 3）
    weights = [3, 1, 3, 1, 3, 1, 3, 1, 3]
    
    # 各桁 × 重み の合計を計算
    total = 0
    for i, digit in enumerate(body_number):
        total += int(digit) * weights[i]
    
    # 10で割った余りを計算
    remainder = total % 10
    
    # チェックデジットを計算
    if remainder == 0:
        calculated_check_digit = 0
    else:
        calculated_check_digit = 10 - remainder
    
    return calculated_check_digit, actual_check_digit

# 実際の牛個体識別番号
real_cattle_ids = [
    '1499801864',
    '1672116808', 
    '1583519477',
    '0873831725',
    '0873831862',
    '1375633374'
]

print("実際の牛個体識別番号でのチェックデジット計算テスト")
print("=" * 60)

for cattle_id in real_cattle_ids:
    print(f"\n個体識別番号: {cattle_id}")
    print(f"本体番号: {cattle_id[:9]}")
    print(f"実際のチェックデジット: {cattle_id[9]}")
    
    # 各種計算方式をテスト
    methods = [
        ("モジュラス10、重み1,3（右から）", test_modulus_10_weight_1_3),
        ("モジュラス11、重み1,3（右から）", test_modulus_11_weight_1_3),
        ("モジュラス10、重み3,1（右から）", test_modulus_10_weight_3_1),
        ("モジュラス11、重み3,1（右から）", test_modulus_11_weight_3_1),
        ("モジュラス10、重み1,3（左から）", test_modulus_10_weight_1_3_reverse),
        ("モジュラス10、重み3,1（左から）", test_modulus_10_weight_3_1_reverse),
    ]
    
    for method_name, method_func in methods:
        try:
            calculated, actual = method_func(cattle_id)
            match = "✓" if calculated == actual else "✗"
            print(f"  {method_name}: {calculated} {match}")
        except Exception as e:
            print(f"  {method_name}: エラー - {e}")

print("\n" + "=" * 60)
print("正しい計算方式を特定してください") 