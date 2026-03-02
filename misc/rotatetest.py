from cpu import GameBoyCPU

def main():
    original_value = 0b11100111
    print(f"\nOriginal value: {bin(original_value)}\n")

    l8 = original_value
    for _ in range(8):
        l8 = GameBoyCPU._rotate_left_8(l8)[0]
    print(f"Rotate Left 8-bit: {"✅ PASSED" if l8 == original_value else f"🚫 FAILED ({bin(l8)})"}")

    r8 = original_value
    for _ in range(8):
        r8 = GameBoyCPU._rotate_right_8(r8)[0]
    print(f"Rotate Right 8-bit: {"✅ PASSED" if r8 == original_value else f"🚫 FAILED ({bin(r8)})"}")

    l9 = original_value
    for _ in range(9):
        l9 = GameBoyCPU._rotate_left_9(l9)[0]
    print(f"Rotate Left 9-bit: {"✅ PASSED" if l9 == original_value else f"🚫 FAILED ({bin(l9)})"}")

    r9 = original_value
    for _ in range(9):
        r9 = GameBoyCPU._rotate_right_9(r9)[0]
    print(f"Rotate Right 9-bit: {"✅ PASSED" if r9 == original_value else f"🚫 FAILED ({bin(r9)})"}")

if __name__ == "__main__":
    main()
