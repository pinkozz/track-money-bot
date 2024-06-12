import json

user_data = {}
with open("db.json", "r") as f:
    user_data = json.load(f)
    
class User:
    def __init__(self, id, bills=0, food=0, health=0, transport=0, shopping=0, communication=0, salary=0, savings=0):
        self.id = id
        self.bills = bills
        self.food = food
        self.health = health
        self.transport = transport
        self.shopping = shopping
        self.communication = communication
        self.salary = salary
        self.savings = savings

    def create_user(self):
        # Create a new dict item with new user's data
        new_data = {
            "expenses": {
                "bills": self.bills,
                "food": self.food,
                "health": self.health,
                "transport": self.transport,
                "shopping": self.shopping,
                "communication": self.communication,
            },
            "incomes": {
                "salary": self.salary,
                "savings": self.savings,
            },
            "state": {
                "type": "",      
                "category": "", 
                "amount": 0,
            },
        }
        # Write to the database
        with open("db.json", "w") as f:
            user_data[self.id] = new_data
            json.dump(user_data, f, indent=4)