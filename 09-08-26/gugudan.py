# -*- coding: utf-8 -*-
"""
구구단 프로그램 (Multiplication Table Program)
작성일: 2026-09-08
"""

def print_all_horizontal():
    """구구단 전체를 가로 방향(단별 컬럼)으로 정렬하여 출력합니다."""
    print("\n[구구단 전체 출력 (가로형)]")
    # 타이틀 행 출력 (2단 ~ 9단)
    headers = [f"=== {dan}단 ===" for dan in range(2, 10)]
    print("  ".join(headers))
    
    # 1부터 9까지 곱하는 행 출력
    for num in range(1, 10):
        row = []
        for dan in range(2, 10):
            row.append(f"{dan} x {num} = {dan * num:2d}")
        print("  |  ".join(row))
    print()

def print_all_vertical():
    """구구단 전체를 세로 방향(2단부터 순서대로)으로 출력합니다."""
    print("\n[구구단 전체 출력 (세로형)]")
    for dan in range(2, 10):
        print(f"--- {dan}단 ---")
        for num in range(1, 10):
            print(f"{dan} x {num} = {dan * num:2d}")
        print()

def print_specific_dan():
    """사용자가 입력한 특정 단을 출력합니다."""
    while True:
        try:
            user_input = input("\n출력할 단을 입력하세요 (2~9) [이전 메뉴로 가려면 Enter]: ").strip()
            if not user_input:
                return
            
            dan = int(user_input)
            if 2 <= dan <= 9:
                print(f"\n=== {dan}단 ===")
                for num in range(1, 10):
                    print(f"{dan} x {num} = {dan * num:2d}")
                print()
                break
            else:
                print("⚠️ 2에서 9 사이의 숫자만 입력 가능합니다.")
        except ValueError:
            print("⚠️ 올바른 숫자를 입력해주세요.")

def main():
    while True:
        print("=" * 40)
        print("             구구단 프로그램             ")
        print("=" * 40)
        print("1. 전체 구구단 출력 (가로 정렬)")
        print("2. 전체 구구단 출력 (세로 정렬)")
        print("3. 특정 단 출력")
        print("4. 프로그램 종료")
        print("=" * 40)
        
        choice = input("원하는 메뉴 번호를 선택하세요 (1~4): ").strip()
        
        if choice == '1':
            print_all_horizontal()
        elif choice == '2':
            print_all_vertical()
        elif choice == '3':
            print_specific_dan()
        elif choice == '4':
            print("프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
            break
        else:
            print("⚠️ 잘못된 선택입니다. 1~4 사이의 번호를 입력해주세요.\n")

if __name__ == "__main__":
    main()
