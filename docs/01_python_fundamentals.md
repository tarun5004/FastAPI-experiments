# 01 — Python Fundamentals & OOP (Complete In-Depth Guide - Hinglish)

> 🎯 **Goal**: Is guide ko padhne ke baad tumhe Python ka complete foundation mil jayega - variables se leke advanced OOP tak. Industry mein kaise use hota hai wo bhi cover karenge.

---

## 📚 Table of Contents
1. [Python Kya Hai?](#python-kya-hai)
2. [Variables & Data Types](#variables--data-types)
3. [Operators](#operators)
4. [Control Flow (if/else/loops)](#control-flow)
5. [Functions - Basic to Advanced](#functions)
6. [Data Structures (List, Dict, Set, Tuple)](#data-structures)
7. [List/Dict Comprehensions](#comprehensions)
8. [File Handling](#file-handling)
9. [Exception Handling](#exception-handling)
10. [OOP - Classes & Objects](#oop-classes--objects)
11. [OOP - Inheritance & Polymorphism](#inheritance--polymorphism)
12. [Dunder/Magic Methods](#dunder-methods)
13. [Decorators](#decorators)
14. [Type Hints](#type-hints)
15. [Industry Best Practices](#industry-best-practices)
16. [Practice Exercises](#practice-exercises)

---

## Python Kya Hai?

Python ek **high-level, interpreted** programming language hai jo:
- **Easy to read** - English jaise syntax
- **Versatile** - Web dev, ML, automation, scripting sab ho sakta hai
- **Large ecosystem** - Packages har cheez ke liye available hain

```python
# Python ka pehla program
print("Hello, Duniya!")  # Ye console pe print karega
```

### Python Install Karna
```bash
# Windows pe python.org se download karo
# Ya chocolatey use karo:
choco install python

# Check version
python --version  # Python 3.11.x
```

---

## Variables & Data Types

### Variable Kya Hai?
Variable ek **container** hai jisme data store hota hai. Python mein tum directly value assign karte ho - type declare nahi karna padta.

```python
# Variable banane ka tarika
name = "Tarun"      # String (text)
age = 25            # Integer (whole number)
salary = 50000.50   # Float (decimal number)
is_active = True    # Boolean (True/False)
nothing = None      # NoneType (empty/null value)

# Python automatically type detect karta hai
print(type(name))   # <class 'str'>
print(type(age))    # <class 'int'>
```

### Data Types in Detail

#### 1. String (str) - Text Data
```python
# String banane ke 3 tarike
name = "Tarun"           # Double quotes
city = 'Mumbai'          # Single quotes
bio = """Ye ek
multiline string hai"""  # Triple quotes (multiline)

# String Operations
full_name = "Tarun" + " " + "Kumar"  # Concatenation: "Tarun Kumar"
repeated = "Ha" * 3                   # Repeat: "HaHaHa"

# String Methods (bahut important!)
text = "  Hello World  "
print(text.strip())       # "Hello World" - spaces remove
print(text.lower())       # "  hello world  " - lowercase
print(text.upper())       # "  HELLO WORLD  " - uppercase
print(text.replace("World", "Python"))  # "  Hello Python  "
print(text.split())       # ['Hello', 'World'] - list ban gaya

# String Formatting (Industry Standard - f-strings)
name = "Tarun"
age = 25
# OLD way (don't use):
print("Name is " + name + " age is " + str(age))
# NEW way (use this!):
print(f"Name is {name} and age is {age}")  # f-string
print(f"Next year age: {age + 1}")         # Expression bhi chal jata hai

# String Indexing & Slicing
text = "Python"
print(text[0])      # 'P' - first character
print(text[-1])     # 'n' - last character
print(text[0:3])    # 'Pyt' - slice (start:end, end exclusive)
print(text[::2])    # 'Pto' - every 2nd character
print(text[::-1])   # 'nohtyP' - reverse string
```

#### 2. Numbers (int, float)
```python
# Integer - whole numbers
count = 100
negative = -50
big_number = 1_000_000  # Underscore for readability (1 million)

# Float - decimal numbers
price = 99.99
pi = 3.14159

# Type Conversion
num_str = "42"
num_int = int(num_str)   # String to int: 42
num_float = float("3.14")  # String to float: 3.14
back_to_str = str(100)   # Int to string: "100"

# Math Operations
a, b = 10, 3
print(a + b)   # 13 - Addition
print(a - b)   # 7 - Subtraction
print(a * b)   # 30 - Multiplication
print(a / b)   # 3.333... - Division (returns float)
print(a // b)  # 3 - Floor division (integer result)
print(a % b)   # 1 - Modulo (remainder)
print(a ** b)  # 1000 - Power (10^3)

# Useful math functions
import math
print(abs(-5))        # 5 - Absolute value
print(round(3.7))     # 4 - Round
print(math.ceil(3.2)) # 4 - Ceiling (upar wala integer)
print(math.floor(3.8))# 3 - Floor (neeche wala integer)
```

#### 3. Boolean (bool)
```python
is_active = True
is_deleted = False

# Boolean results from comparisons
print(5 > 3)      # True
print(5 == 3)     # False
print(5 != 3)     # True
print("a" in "abc")  # True

# Truthy and Falsy values (bahut important!)
# Falsy values: False, 0, 0.0, "", [], {}, None
# Baaki sab Truthy hai

if "":       # Empty string is Falsy
    print("Yes")
else:
    print("No")  # Ye print hoga

if [1, 2]:   # Non-empty list is Truthy
    print("Yes")  # Ye print hoga
```

---

## Operators

### Comparison Operators
```python
a, b = 10, 5

print(a == b)  # False - Equal
print(a != b)  # True - Not equal
print(a > b)   # True - Greater than
print(a < b)   # False - Less than
print(a >= b)  # True - Greater or equal
print(a <= b)  # False - Less or equal
```

### Logical Operators
```python
x, y = True, False

print(x and y)  # False - Dono True hone chahiye
print(x or y)   # True - Ek bhi True ho toh True
print(not x)    # False - Opposite

# Real example
age = 25
has_license = True
can_drive = age >= 18 and has_license  # True
```

### Identity & Membership Operators
```python
# Identity (is) - Same object check
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)   # True - Values same hain
print(a is b)   # False - Different objects hain
print(a is c)   # True - Same object hai

# Membership (in)
fruits = ["apple", "banana", "mango"]
print("apple" in fruits)     # True
print("grape" not in fruits) # True
```

---

## Control Flow

### If-Else Statements
```python
age = 18

# Simple if-else
if age >= 18:
    print("Adult hai")
else:
    print("Minor hai")

# Multiple conditions (elif)
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
print(f"Grade: {grade}")  # Grade: B

# Ternary operator (one-line if-else)
status = "Adult" if age >= 18 else "Minor"

# Multiple conditions combine karna
age = 25
has_id = True
has_ticket = True

if age >= 18 and has_id and has_ticket:
    print("Entry allowed")
```

### Loops

#### For Loop
```python
# List iterate karna
fruits = ["apple", "banana", "mango"]
for fruit in fruits:
    print(fruit)

# Range use karna
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 6):    # 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # 0, 2, 4, 6, 8 (step=2)
    print(i)

# Enumerate - index + value dono chahiye
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
# 0: apple
# 1: banana
# 2: mango

# Dictionary iterate
user = {"name": "Tarun", "age": 25}
for key, value in user.items():
    print(f"{key} = {value}")
```

#### While Loop
```python
count = 0
while count < 5:
    print(count)
    count += 1  # count = count + 1

# Infinite loop with break
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input == "quit":
        break  # Loop se bahar aa jao
    print(f"You entered: {user_input}")
```

#### Break, Continue, Pass
```python
# Break - Loop se turant bahar
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# Continue - Current iteration skip karo
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4 (2 skip ho gaya)

# Pass - Kuch mat karo (placeholder)
for i in range(5):
    if i == 2:
        pass  # TODO: baad mein implement karna hai
    print(i)  # 0, 1, 2, 3, 4
```

---

## Functions

### Basic Function
```python
# Function define karna
def greet():
    print("Hello!")

# Function call karna
greet()  # Hello!

# Parameters ke saath
def greet_user(name):
    print(f"Hello, {name}!")

greet_user("Tarun")  # Hello, Tarun!

# Return value
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # 8
```

### Default Arguments
```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Tarun"))              # Hello, Tarun!
print(greet("Tarun", "Namaste"))   # Namaste, Tarun!
```

### *args and **kwargs (Very Important!)
```python
# *args - Multiple positional arguments (tuple ban jata hai)
def add_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(add_all(1, 2, 3, 4, 5))  # 15

# **kwargs - Multiple keyword arguments (dict ban jata hai)
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Tarun", age=25, city="Mumbai")
# name: Tarun
# age: 25
# city: Mumbai

# Dono saath mein
def super_function(required, *args, **kwargs):
    print(f"Required: {required}")
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")

super_function("first", 1, 2, 3, name="Tarun", age=25)
# Required: first
# Args: (1, 2, 3)
# Kwargs: {'name': 'Tarun', 'age': 25}
```

### Lambda Functions (Anonymous Functions)
```python
# Normal function
def square(x):
    return x ** 2

# Lambda version
square = lambda x: x ** 2

print(square(5))  # 25

# Lambda mostly higher-order functions mein use hota hai
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))  # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x%2==0, numbers))  # [2, 4]
```

---

## Data Structures

### 1. List (Mutable, Ordered)
```python
# List create karna
fruits = ["apple", "banana", "mango"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]  # Different types allowed

# Accessing elements
print(fruits[0])    # "apple" - First element
print(fruits[-1])   # "mango" - Last element
print(fruits[1:3])  # ["banana", "mango"] - Slicing

# List Methods
fruits.append("orange")     # End mein add
fruits.insert(0, "grape")   # Specific index pe add
fruits.remove("banana")     # Value se remove
popped = fruits.pop()       # Last element remove and return
fruits.extend(["kiwi", "papaya"])  # Dusri list merge

# Other useful methods
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
numbers.sort()              # [1, 1, 2, 3, 4, 5, 6, 9] - In-place sort
numbers.reverse()           # Reverse in-place
print(len(numbers))         # 8 - Length
print(numbers.count(1))     # 2 - Count occurrences
print(numbers.index(5))     # Index of element

# List copy - Be careful!
a = [1, 2, 3]
b = a           # Same reference - changes affect both!
c = a.copy()    # New copy - independent
d = a[:]        # Another way to copy
```

### 2. Dictionary (Mutable, Key-Value Pairs)
```python
# Dict create karna
user = {
    "name": "Tarun",
    "age": 25,
    "email": "tarun@example.com"
}

# Accessing values
print(user["name"])          # "Tarun"
print(user.get("name"))      # "Tarun" - Same thing
print(user.get("phone", "N/A"))  # "N/A" - Default if key not found

# Adding/Updating
user["phone"] = "9876543210"  # Add new key
user["age"] = 26              # Update existing

# Dict Methods
print(user.keys())    # dict_keys(['name', 'age', 'email', 'phone'])
print(user.values())  # dict_values(['Tarun', 26, 'tarun@example.com', '9876543210'])
print(user.items())   # Key-value pairs as tuples

# Check if key exists
if "email" in user:
    print("Email hai")

# Remove
del user["phone"]       # Key delete
email = user.pop("email", None)  # Remove and return

# Iterate
for key, value in user.items():
    print(f"{key}: {value}")

# Nested Dict
company = {
    "name": "TechCorp",
    "employees": [
        {"name": "Alice", "role": "Dev"},
        {"name": "Bob", "role": "Manager"}
    ]
}
print(company["employees"][0]["name"])  # "Alice"
```

### 3. Set (Mutable, Unique Elements, Unordered)
```python
# Set create karna
numbers = {1, 2, 3, 4, 5}
unique = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3} - Duplicates remove

# Set Operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)  # {1, 2, 3, 4, 5, 6} - Union
print(a & b)  # {3, 4} - Intersection
print(a - b)  # {1, 2} - Difference
print(a ^ b)  # {1, 2, 5, 6} - Symmetric difference

# Set Methods
numbers.add(6)        # Add element
numbers.remove(6)     # Remove (error if not found)
numbers.discard(10)   # Remove (no error if not found)

# Membership check - O(1) very fast!
if 3 in numbers:
    print("Found!")
```

### 4. Tuple (Immutable, Ordered)
```python
# Tuple create karna
point = (10, 20)
rgb = (255, 128, 0)

# Accessing
print(point[0])  # 10
x, y = point     # Unpacking: x=10, y=20

# Tuple is immutable - can't change after creation
# point[0] = 15  # ERROR!

# Use cases:
# 1. Return multiple values from function
def get_user():
    return ("Tarun", 25, "Mumbai")

name, age, city = get_user()

# 2. Dictionary keys (list can't be key, but tuple can)
locations = {
    (28.6, 77.2): "Delhi",
    (19.0, 72.8): "Mumbai"
}
```

---

## Comprehensions

### List Comprehension
```python
# Traditional way
squares = []
for i in range(10):
    squares.append(i ** 2)

# List comprehension (one-liner) - Pythonic way!
squares = [i ** 2 for i in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
evens = [i for i in range(20) if i % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Nested loop in comprehension
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# If-else in comprehension
numbers = [1, 2, 3, 4, 5]
result = ["even" if x % 2 == 0 else "odd" for x in numbers]
# ['odd', 'even', 'odd', 'even', 'odd']
```

### Dict Comprehension
```python
# Square dict
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Swap keys and values
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}
```

### Set Comprehension
```python
unique_lengths = {len(word) for word in ["hello", "world", "python", "code"]}
# {5, 6, 4}
```

---

## File Handling

```python
# Writing to file
with open("data.txt", "w") as file:
    file.write("Hello, World!\n")
    file.write("This is line 2")

# Reading file
with open("data.txt", "r") as file:
    content = file.read()       # Pura file ek string mein
    # OR
    lines = file.readlines()    # List of lines
    # OR
    for line in file:           # Line by line iterate
        print(line.strip())

# Append to file
with open("data.txt", "a") as file:
    file.write("\nNew line added")

# JSON file handling (very important for APIs!)
import json

# Write JSON
data = {"name": "Tarun", "age": 25, "skills": ["Python", "FastAPI"]}
with open("user.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON
with open("user.json", "r") as f:
    loaded = json.load(f)
    print(loaded["name"])  # "Tarun"

# JSON string conversion
json_string = json.dumps(data)  # Dict to JSON string
back_to_dict = json.loads(json_string)  # JSON string to dict
```

---

## Exception Handling

```python
# Basic try-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

# Multiple exceptions
try:
    value = int("hello")
except ValueError:
    print("Invalid number")
except TypeError:
    print("Type error")

# Catch all exceptions (use carefully)
try:
    risky_operation()
except Exception as e:
    print(f"Error: {e}")

# Finally - Always runs
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found")
finally:
    file.close()  # Cleanup - always runs

# Better way with context manager
try:
    with open("data.txt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("File not found")

# Raising exceptions
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age too high")
    return age

# Custom Exception
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw {amount}. Balance: {balance}")

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount
```

---

## OOP - Classes & Objects

### Basic Class
```python
class User:
    # Class variable (shared by all instances)
    platform = "FastAPI App"
    
    # Constructor - object create hote waqt call hota hai
    def __init__(self, name, email):
        # Instance variables (har object ke apne)
        self.name = name
        self.email = email
        self.is_active = True  # Default value
    
    # Instance method
    def greet(self):
        return f"Hello, I am {self.name}"
    
    # Another instance method
    def deactivate(self):
        self.is_active = False
        return f"{self.name} deactivated"

# Object create karna
user1 = User("Tarun", "tarun@example.com")
user2 = User("Alice", "alice@example.com")

print(user1.name)       # "Tarun"
print(user1.greet())    # "Hello, I am Tarun"
print(User.platform)    # "FastAPI App" - Class variable
```

### Instance vs Class vs Static Methods
```python
class Calculator:
    # Class variable
    history = []
    
    def __init__(self, name):
        self.name = name  # Instance variable
    
    # Instance method - self use karta hai
    def add(self, a, b):
        result = a + b
        Calculator.history.append(f"{self.name}: {a}+{b}={result}")
        return result
    
    # Class method - cls use karta hai, class pe kaam karta hai
    @classmethod
    def get_history(cls):
        return cls.history
    
    @classmethod
    def from_string(cls, name_string):
        # Factory method - alternative constructor
        name = name_string.strip().upper()
        return cls(name)
    
    # Static method - na self na cls, utility function jaisa
    @staticmethod
    def is_valid_number(value):
        return isinstance(value, (int, float))

# Usage
calc = Calculator("Main")
print(calc.add(5, 3))  # 8

# Class method
print(Calculator.get_history())  # ["Main: 5+3=8"]

# Factory method
calc2 = Calculator.from_string("  secondary  ")
print(calc2.name)  # "SECONDARY"

# Static method
print(Calculator.is_valid_number(5))    # True
print(Calculator.is_valid_number("5"))  # False
```

---

## Inheritance & Polymorphism

### Basic Inheritance
```python
# Parent class (Base class)
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "Some sound"
    
    def info(self):
        return f"I am {self.name}"

# Child class (Derived class)
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # Parent ka __init__ call karo
        self.breed = breed
    
    # Method override
    def speak(self):
        return "Woof!"
    
    # New method
    def fetch(self):
        return f"{self.name} is fetching!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

# Usage
dog = Dog("Buddy", "Labrador")
cat = Cat("Whiskers")

print(dog.info())    # "I am Buddy" - Inherited method
print(dog.speak())   # "Woof!" - Overridden method
print(dog.fetch())   # "Buddy is fetching!" - New method
print(cat.speak())   # "Meow!"

# Polymorphism - Same interface, different behavior
animals = [dog, cat]
for animal in animals:
    print(animal.speak())  # Different output for each
```

### Multiple Inheritance
```python
class Flyable:
    def fly(self):
        return "Flying!"

class Swimmable:
    def swim(self):
        return "Swimming!"

class Duck(Animal, Flyable, Swimmable):
    def speak(self):
        return "Quack!"

duck = Duck("Donald")
print(duck.speak())  # "Quack!"
print(duck.fly())    # "Flying!"
print(duck.swim())   # "Swimming!"
```

### Abstract Classes (Industry Pattern)
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass  # Subclass must implement
    
    @abstractmethod
    def refund(self, amount):
        pass

class StripePayment(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via Stripe"
    
    def refund(self, amount):
        return f"Refunding ${amount} via Stripe"

class PayPalPayment(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${amount} via PayPal"
    
    def refund(self, amount):
        return f"Refunding ${amount} via PayPal"

# Usage
processor = StripePayment()
print(processor.process_payment(100))
```

---

## Dunder Methods

Dunder = Double Underscore methods. Ye special methods hain jo Python internally use karta hai.

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    # String representation (print ke liye)
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    # Developer representation (debugging ke liye)
    def __repr__(self):
        return f"Product(name='{self.name}', price={self.price})"
    
    # Comparison operators
    def __eq__(self, other):
        return self.price == other.price
    
    def __lt__(self, other):
        return self.price < other.price
    
    def __le__(self, other):
        return self.price <= other.price
    
    # Arithmetic operators
    def __add__(self, other):
        return self.price + other.price
    
    # Length
    def __len__(self):
        return len(self.name)
    
    # Make object callable like function
    def __call__(self, discount):
        return self.price * (1 - discount/100)
    
    # Dictionary-like access
    def __getitem__(self, key):
        return getattr(self, key)
    
    # Context manager (with statement)
    def __enter__(self):
        print("Entering context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context")

# Usage
p1 = Product("Laptop", 1000)
p2 = Product("Phone", 500)

print(p1)           # "Laptop - $1000" (__str__)
print(repr(p1))     # "Product(name='Laptop', price=1000)" (__repr__)
print(p1 == p2)     # False (__eq__)
print(p1 > p2)      # True (__lt__ se derive)
print(p1 + p2)      # 1500 (__add__)
print(len(p1))      # 6 (__len__)
print(p1(10))       # 900.0 - 10% discount (__call__)
print(p1["name"])   # "Laptop" (__getitem__)

with p1 as product:  # Context manager
    print(product.name)
```

---

## Decorators

Decorator ek function hai jo dusre function ko modify karta hai bina uska code change kiye.

```python
# Basic decorator
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("Tarun")
# Before function call
# Hello, Tarun!
# After function call

# Practical example: Timing decorator
import time
from functools import wraps

def timer(func):
    @wraps(func)  # Preserve function metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end-start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()  # slow_function took 1.0012 seconds

# Decorator with arguments
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hello!")

greet()  # Prints "Hello!" 3 times

# Class-based decorator
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()  # Call #1 \n Hi!
say_hi()  # Call #2 \n Hi!
```

---

## Type Hints

Type hints code ko readable aur maintainable banate hain. IDE mein better autocomplete milta hai.

```python
from typing import List, Dict, Optional, Union, Tuple, Any, Callable

# Basic type hints
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

# Complex types
def process_users(users: List[str]) -> Dict[str, int]:
    return {user: len(user) for user in users}

# Optional - value ya None ho sakta hai
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Tarun"
    return None  # None bhi valid hai

# Union - multiple types allowed
def process(value: Union[int, str]) -> str:
    return str(value)

# Tuple with specific types
def get_coordinates() -> Tuple[float, float]:
    return (28.6, 77.2)

# Callable (function as parameter)
def apply_operation(x: int, operation: Callable[[int], int]) -> int:
    return operation(x)

# Type aliases (cleaner code)
UserId = int
UserDict = Dict[str, Union[str, int, bool]]

def get_user(user_id: UserId) -> UserDict:
    return {"id": user_id, "name": "Tarun", "active": True}

# Class type hints
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
    
    def greet(self) -> str:
        return f"Hi, I'm {self.name}"

def create_user(name: str, age: int) -> User:
    return User(name, age)
```

---

## Industry Best Practices

### 1. Code Organization
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── routers/          # API routes
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── tests/
├── requirements.txt
└── README.md
```

### 2. Naming Conventions
```python
# Variables & functions: snake_case
user_name = "Tarun"
def get_user_by_id():
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_CASE
MAX_RETRIES = 3
DATABASE_URL = "postgresql://..."

# Private (convention): _prefix
class User:
    def __init__(self):
        self._internal_state = {}  # Private-ish
        self.__very_private = {}   # Name mangling
```

### 3. SOLID Principles (Brief)
```python
# S - Single Responsibility: Ek class ek kaam kare
class UserRepository:   # Only DB operations
    def save(self, user): pass
    def find(self, id): pass

class EmailService:     # Only email operations
    def send(self, to, subject, body): pass

# O - Open/Closed: Extend karo, modify mat karo
# (Use inheritance/composition)

# L - Liskov Substitution: Subclass parent ki jagah use ho sake

# I - Interface Segregation: Small focused interfaces

# D - Dependency Injection: Dependencies bahar se inject karo
class UserService:
    def __init__(self, repository, email_service):  # Injected
        self.repository = repository
        self.email_service = email_service
```

### 4. Error Handling Patterns
```python
# Always be specific with exceptions
try:
    user = get_user(user_id)
except UserNotFoundError:
    return None
except DatabaseError as e:
    logger.error(f"DB error: {e}")
    raise

# Use custom exceptions
class AppError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)

class UserNotFoundError(AppError):
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} not found", "USER_NOT_FOUND")
```

### 5. Documentation
```python
def create_order(user_id: int, items: List[dict], discount: float = 0.0) -> Order:
    """
    Create a new order for a user.
    
    Args:
        user_id: The ID of the user placing the order.
        items: List of items, each with 'product_id' and 'quantity'.
        discount: Optional discount percentage (0-100).
    
    Returns:
        The created Order object.
    
    Raises:
        UserNotFoundError: If user doesn't exist.
        InsufficientStockError: If any item is out of stock.
    
    Example:
        >>> order = create_order(1, [{"product_id": 10, "quantity": 2}])
        >>> order.total
        199.98
    """
    pass
```

---

## Practice Exercises

### Exercise 1: User Class (Basic)
```python
# Create a User class with:
# - Attributes: name, email, age, is_active
# - Methods: greet(), to_dict(), validate_email()
# - Use type hints
# - Add __str__ and __repr__
```

### Exercise 2: Product Inventory (Intermediate)
```python
# Create:
# 1. Product class with name, price, stock
# 2. Inventory class that manages products
# 3. Methods: add_product, remove_product, get_total_value
# 4. Handle edge cases (negative stock, duplicate products)
```

### Exercise 3: Payment System (Advanced)
```python
# Create:
# 1. Abstract PaymentProcessor class
# 2. CreditCardPayment, UPIPayment, WalletPayment implementations
# 3. PaymentFactory to create appropriate processor
# 4. Transaction logging decorator
# 5. Custom exceptions for payment failures
```

### Exercise 4: File-based Todo App
```python
# Create a CLI todo app that:
# 1. Stores todos in JSON file
# 2. CRUD operations: add, list, complete, delete
# 3. Priority and due dates
# 4. Use classes for Todo and TodoManager
```

---

## Quick Reference Card

```python
# Data Types
str, int, float, bool, None, list, dict, set, tuple

# String formatting
f"Hello {name}"

# List operations
lst.append(x), lst.pop(), lst.sort(), lst.reverse()

# Dict operations  
d.get(key, default), d.keys(), d.values(), d.items()

# Comprehensions
[x**2 for x in range(10) if x % 2 == 0]
{k: v for k, v in items}

# Functions
def func(required, default="val", *args, **kwargs): pass
lambda x: x**2

# Classes
class Child(Parent):
    def __init__(self):
        super().__init__()

# Decorators
@decorator
def func(): pass

# Type hints
def func(x: int, items: List[str]) -> Dict[str, int]: pass

# Exception handling
try:
    risky()
except SpecificError as e:
    handle(e)
finally:
    cleanup()

# File handling
with open("file.txt", "r") as f:
    content = f.read()
```

---

## Next Steps

1. **Practice karo** - Exercises complete karo
2. **Projects banao** - Small CLI apps, file processors
3. **Next doc padho** - `02_fastapi_basics.md`

---

> **Note**: Is doc ko bookmark karo. Jab bhi Python ka koi concept bhool jaye, yahan wapis aao!
