import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

#Abstract class for defining how the classes can interact with the user
class UserA(ABC):
    @abstractmethod
    def choice(self):
        pass

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def goBack(self):
        pass

#Actual class being used for lab
class NumberManager(UserA):

    #Initializes the number list when a NumberManager object is created
    def __init__(self):
        self.init()

    def init(self):
        self.numbers = []

    def choice(self, choice):
        return choice

    def display(self):
        return pd.DataFrame({"Number": self.numbers})

    def goBack(self):
        return True

    def add_number(self, number):
        self.numbers.append(number)
        return self.numbers

    def remove_number(self, number):
        self.numbers.remove(number)
        return self.numbers

    def sort_numbers(self):
        self.numbers.sort()
        return self.numbers

    def calculate_statistics(self):
        total = sum(self.numbers)
        count = len(self.numbers)

        if count == 0:
            return 0, 0, 0, 0

        average = total / count
        minimum = min(self.numbers)
        maximum = max(self.numbers)

        return total, average, minimum, maximum

    #Saves the current list of numbers to the JSON file
    def save_data(self, filename):
        file_path = Path(filename)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump({"numbers": self.numbers}, file, indent=4)
        return self.numbers

    #Reloads the list of numbers from the JSON file
    def load_data(self, filename):
        file_path = Path(filename)
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict) or not isinstance(data.get("numbers"), list):
            raise ValueError("The JSON file must contain a 'numbers' list.")

        if any(
            isinstance(number, bool) or not isinstance(number, (int, float))
            for number in data["numbers"]
        ):
            raise ValueError("Every item in the 'numbers' list must be a number.")

        self.numbers = data["numbers"]
        return self.numbers

#test for the class alone
#manager = NumberManager()

#print(manager.add_number(10))
#print(manager.add_number(25))
#print(manager.add_number(50))

#print(manager.display())

#total, average, minimum, maximum = manager.calculate_statistics()

#print("Total:", total)
#print("Average:", average)
#print("Minimum:", minimum)
#print("Maximum:", maximum)

#print(manager.remove_number(25))
