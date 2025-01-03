from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value.strip(): # Перевіряємо, чи не порожнє значення
            raise ValueError("Name cannot be empty or just whitespace.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError(f"Invalid phone number: {value}. It must contain exactly 10 digits.")
        self.value = value
    # Валідація номера телефону (10 цифр)
    def validate(self, value):
        return bool(re.match(r'^\d{10}$', value))

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    def add_phone(self, phone):
        # Додаємо телефон до списку
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        # Видаляємо телефон, якщо такий є
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
         # Заміна старого телефону на новий
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break

    def find_phone(self, phone):
         # Пошук телефону у списку
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj.value
        return None

    def add_birthday(self, birthday):
         # Додаємо ДР
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday else 'No birthday'
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming = []
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year).date()
                if today <= bday_this_year <= next_week:
                    upcoming.append(record.name.value)
        return upcoming

# Функції серіалізації та десеріалізації
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повертаємо нову адресну книгу, якщо файл не знайдено

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return inner

# Функція для дадавання телефонного номера
@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Please provide both name and phone number.")
    name, phone = args[0], args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

# Функція для обробки введення команд
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Функція для зміни телефонного номера
@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone updated."
    return "Contact not found."

# Функція для показу телефонного номера
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return '; '.join(p.value for p in record.phones)
    return "Contact not found."

# Функція для показу всіх контактів
@input_error
def show_all(args, book):
    result = []
    for record in book.data.values():
        name = record.name.value
        phones = ', '.join(p.value for p in record.phones)
        result.append(f"Name: {name}, Phones: {phones}")
    return '\n'.join(result)

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime('%d.%m.%Y')
    return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    return "Upcoming birthdays: " + ', '.join(upcoming) if upcoming else "No upcoming birthdays."

def main():
    book = load_data()  # Завантажуємо наявні дані або створіть нові
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  # Зберігаємо дані перед виходом
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

