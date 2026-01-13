import sys

def main():
    try:
        if len(sys.argv) > 1:
            number = float(sys.argv[1])
        else:
            number = float(input("Enter a number: "))
        
        result = number ** 2
        print(f"The square of {number} is {result}.")
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()
