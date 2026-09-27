# Task 1: Simple Calculator 

def calculate(x, y, operator):
    """Perform the requested calculation."""
    
    if operator == "+":
        return x + y

    elif operator == "-":
        return x - y

    elif operator == "*":
        return x * y

    elif operator == "/":
        if y == 0:
            return "Error: Cannot divide by zero"
        return x / y

    else:
        return "Error: Invalid operator"


def get_number(prompt):
    """Get a valid number from the user."""
    
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    print("Welcome to the Python Calculator!")

    while True:
        print("\n--- Calculator Menu ---")
        print("1. Calculate")
        print("2. Clear")
        print("3. Exit")

        choice = input("Choose an option: ").strip().lower()

        if choice == "3" or choice == "exit":
            print("Program Ended.")
            break

        elif choice == "2" or choice == "clear":
            print("\nCalculator cleared.")
            continue

        elif choice == "1":
            x = get_number("Please enter the first number: ")
            y = get_number("Please enter the second number: ")

            operator = input(
                "Please enter an operator (+, -, *, /): "
            ).strip()

            result = calculate(x, y, operator)

            print("The answer is:", result)

        else:
            print("Invalid choice. Please choose 1, 2, or 3.")


main()