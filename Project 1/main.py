from json import JSONDecodeError
from pathlib import Path

from data_manager import NumberManager


DATA_FILE = Path(__file__).with_name("numbers.json")


#This is the basic menu being shown to the user while in the loop of the menu
def display_menu():
    print("\n========================================")
    print("          NUMBER DATA MANAGER")
    print("========================================")
    print("1. View Numbers")
    print("2. Add Number")
    print("3. Remove Number")
    print("4. Calculate Statistics")
    print("5. Sort Numbers")
    print("6. Save Data")
    print("7. Reload Data")
    print("8. Exit")
    print("========================================")

#This is the function being used to display and handle the main menu loop
def main():
    #This just gives the methods from the number manager and puts them under a shorter name
    manager = NumberManager()

    print("Welcome to the Number Data Manager!")

    #Loads the saved numbers when the program starts
    try:
        manager.load_data(DATA_FILE)
        print("Saved data loaded!")
    except FileNotFoundError:
        print("No saved data file was found. Starting with an empty list.")
    except JSONDecodeError:
        print("The saved JSON file is not formatted correctly. Starting with an empty list.")
    except ValueError as error:
        print("The saved data is not valid:", error)

    #This is the actual loop being used for the menu
    while True:
        display_menu()

        #Takes user input to cycle through the loop
        choice = input("Enter your choice: ")

        #Viewing method
        if choice == "1":
            print(manager.display())

        #Adding method
        elif choice == "2":
            try:
                number = int(input("Enter a number: "))
                manager.add_number(number)
                print("Number added!")
            except ValueError:
                print("Please enter a valid whole number.")

        #Remove method
        elif choice == "3":
            try:
                number = int(input("Enter the number to remove: "))
                manager.remove_number(number)
                print("Number removed!")
            except ValueError:
                print("Please enter a number that is currently in the list.")

        #Gives general statistics for the numbers loaded into the manager's list
        elif choice == "4":
            total, average, minimum, maximum = manager.calculate_statistics()

            print("\nStatistics")
            print("--------------------")
            print("Total:", total)
            print("Average:", average)
            print("Minimum:", minimum)
            print("Maximum:", maximum)

        #Sort method
        elif choice == "5":
            manager.sort_numbers()
            print("Numbers sorted!")

        #Save method
        elif choice == "6":
            manager.save_data(DATA_FILE)
            print("Data saved!")

        #Reload method
        elif choice == "7":
            try:
                manager.load_data(DATA_FILE)
                print("Data reloaded!")
            except FileNotFoundError:
                print("No saved data file was found. Save the data first.")
            except JSONDecodeError:
                print("The saved JSON file is not formatted correctly.")
            except ValueError as error:
                print("The saved data is not valid:", error)

        #This is what ends the loop and the program
        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from 1-8.")


if __name__ == "__main__":
    main()
