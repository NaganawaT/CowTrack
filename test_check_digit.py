#!/usr/bin/env python
"""
チェックデジット検証機能のテストスクリプト
"""

import sys
import os

# Djangoの設定を読み込む
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CowTrack.settings')

import django
django.setup()

from cattle.utils import calculate_check_digit, validate_cattle_id, generate_valid_cattle_id

def test_check_digit_calculation():
    """チェックデジット計算のテスト"""
    print("=== チェックデジット計算テスト ===")
    
    # テストケース（9桁の本体番号と期待されるチェックデジット）
    test_cases = [
        ('149980186', 4),  # 実際の例: 1499801864
        ('167211680', 8),  # 実際の例: 1672116808
        ('158351947', 7),  # 実際の例: 1583519477
        ('087383172', 5),  # 実際の例: 0873831725
        ('087383186', 2),  # 実際の例: 0873831862
        ('137563337', 4),  # 実際の例: 1375633374
    ]
    
    for body_number, expected_check_digit in test_cases:
        try:
            calculated_check_digit = calculate_check_digit(body_number)
            full_id = generate_valid_cattle_id(body_number)
            is_valid = validate_cattle_id(full_id)
            
            print(f"本体番号: {body_number}")
            print(f"  計算されたチェックデジット: {calculated_check_digit}")
            print(f"  期待されるチェックデジット: {expected_check_digit}")
            print(f"  完全な個体識別番号: {full_id}")
            print(f"  検証結果: {'有効' if is_valid else '無効'}")
            print(f"  テスト結果: {'✓' if calculated_check_digit == expected_check_digit else '✗'}")
            print()
            
        except Exception as e:
            print(f"エラー: {e}")
            print()

def test_validation():
    """検証機能のテスト"""
    print("=== 検証機能テスト ===")
    
    # 有効な個体識別番号のテスト
    valid_ids = [
        '1499801864',  # チェックデジット: 4
        '1672116808',  # チェックデジット: 8
        '1583519477',  # チェックデジット: 7
        '0873831725',  # チェックデジット: 5
        '0873831862',  # チェックデジット: 2
        '1375633374',  # チェックデジット: 4
    ]
    
    print("有効な個体識別番号のテスト:")
    for cattle_id in valid_ids:
        is_valid = validate_cattle_id(cattle_id)
        print(f"  {cattle_id}: {'✓ 有効' if is_valid else '✗ 無効'}")
    
    print()
    
    # 無効な個体識別番号のテスト
    invalid_ids = [
        '1499801865',  # チェックデジットが間違っている
        '1672116809',  # チェックデジットが間違っている
        '1583519478',  # チェックデジットが間違っている
        '12345678',    # 桁数が不足
        '12345678901', # 桁数が多すぎる
        'abcdefghij',  # 数字以外が含まれている
        '',            # 空文字
    ]
    
    print("無効な個体識別番号のテスト:")
    for cattle_id in invalid_ids:
        is_valid = validate_cattle_id(cattle_id)
        print(f"  {cattle_id}: {'✗ 有効（期待: 無効）' if is_valid else '✓ 無効'}")
    
    print()

def test_generation():
    """個体識別番号生成のテスト"""
    print("=== 個体識別番号生成テスト ===")
    
    test_body_numbers = [
        '123456789',
        '987654321',
        '111111111',
        '000000001',
        '999999999',
    ]
    
    for body_number in test_body_numbers:
        try:
            full_id = generate_valid_cattle_id(body_number)
            is_valid = validate_cattle_id(full_id)
            
            print(f"本体番号: {body_number}")
            print(f"  生成された個体識別番号: {full_id}")
            print(f"  検証結果: {'✓ 有効' if is_valid else '✗ 無効'}")
            print()
            
        except Exception as e:
            print(f"エラー: {e}")
            print()

def test_real_examples():
    """実際の例でのテスト"""
    print("=== 実際の例でのテスト ===")
    
    # 実際の牛個体識別番号の例
    real_examples = [
        '1499801864',  # 例1
        '1672116808',  # 例2
        '1583519477',  # 例3
        '0873831725',  # 例4
        '0873831862',  # 例5
        '1375633374',  # 例6
    ]
    
    for cattle_id in real_examples:
        body_number = cattle_id[:9]
        check_digit = cattle_id[9]
        
        try:
            calculated_check_digit = calculate_check_digit(body_number)
            is_valid = validate_cattle_id(cattle_id)
            
            print(f"個体識別番号: {cattle_id}")
            print(f"  本体番号: {body_number}")
            print(f"  実際のチェックデジット: {check_digit}")
            print(f"  計算されたチェックデジット: {calculated_check_digit}")
            print(f"  検証結果: {'✓ 有効' if is_valid else '✗ 無効'}")
            print()
            
        except Exception as e:
            print(f"エラー: {e}")
            print()

if __name__ == '__main__':
    print("牛個体識別番号チェックデジット検証機能テスト")
    print("=" * 50)
    print()
    
    test_check_digit_calculation()
    test_validation()
    test_generation()
    test_real_examples()
    
    print("テスト完了") 