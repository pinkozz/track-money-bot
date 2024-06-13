import telebot, json
from telebot import types

import user_data as user_data
from user_data import User

bot = telebot.TeleBot(token="API_TOKEN")

# User-specific database
user_data = user_data.user_data

# Function to initialize user data if not present
def initialize_user_data(user_id, user_data):
    if user_id not in user_data:
        new_user = User(user_id)
        new_user.create_user()
    
# Sync data with json file
def sync():
    with open("db.json", "w") as f:
        f.write(json.dumps(user_data, indent=4))

# Function to get expenses for a user
def get_expenses(user_id):
    user_expenses = user_data[user_id]["expenses"]
    return [[f"{i}: ${k}" for i, k in user_expenses.items()], sum(user_expenses.values())]

# Function to get incomes for a user
def get_incomes(user_id):
    user_incomes = user_data[user_id]["incomes"]
    return [[f"{i}: ${k}" for i, k in user_incomes.items()], sum(user_incomes.values())]

# Messages
greet_message = "Hey, {0.first_name}! 🖖\n\n\
I am here to help you with your finances. My main goal is to help you track your earnings and expenses.\n\n\
Type /add to add Income or Expense\n\n\
Type /info to get information about your activities\n\n\
Then click on \"Income\" or \"Expense\" button for further interactions."

add_message = "Choose what you want to add 👀"

categories_message = "Choose one of the categories ⬇️"

amount_message = "Enter your amount 📝"

# Commands
@bot.message_handler(commands=['start'])
def main(message):
    if message.chat.type == "private":
        user_id = str(message.from_user.id)
        initialize_user_data(user_id, user_data)

        commands = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        add = types.KeyboardButton("/add")
        info = types.KeyboardButton("/info")

        commands.add(add, info)
        bot.send_message(message.chat.id, greet_message.format(message.from_user, bot.get_me()), reply_markup=commands)

@bot.message_handler(commands=['add'])
def add(message):
    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup()

        income = types.InlineKeyboardButton("Income", callback_data="income")
        expense = types.InlineKeyboardButton("Expense", callback_data="expense")

        markup.add(income, expense)
        bot.send_message(message.chat.id, add_message, reply_markup=markup)

@bot.message_handler(commands=['info'])
def balance(message):
    user_id = str(message.from_user.id)

    expenses = get_expenses(user_id)
    incomes = get_incomes(user_id)

    expenses_feedback = f"\
ACCOUNT INFO\n\n\
⬆️Expenses:\n\
{'\n'.join(expenses[0])}\n\n\
TOTAL: ${expenses[1]}\n\n\
⬇️Incomes:\n\
{'\n'.join(incomes[0])}\n\n\
TOTAL: ${incomes[1]}\n\n\
\
💰Your $ balance: {incomes[1] - incomes[1]}\
"

    bot.send_message(message.chat.id, expenses_feedback)

# Callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.from_user.id)
    initialize_user_data(user_id, user_data)

    if call.data == "income":
        
        markup = types.InlineKeyboardMarkup(row_width=1)

        salary = types.InlineKeyboardButton("💸 Salary", callback_data="salary")
        savings = types.InlineKeyboardButton("👛 Savings", callback_data="savings")

        markup.add(salary, savings)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=categories_message,
            reply_markup=markup)
        user_data[user_id]["state"]["type"] = "income"

    elif call.data == "expense":
        markup = types.InlineKeyboardMarkup(row_width=1)

        bills = types.InlineKeyboardButton("💳 Bills", callback_data="bills")
        food = types.InlineKeyboardButton("🍟 Food", callback_data="food")
        health = types.InlineKeyboardButton("🏥 Health", callback_data="health")
        transport = types.InlineKeyboardButton("🚘 Transport", callback_data="transport")
        shopping = types.InlineKeyboardButton("🛒 Shopping", callback_data="shopping")
        communication = types.InlineKeyboardButton("☎️ Communication", callback_data="communication")

        markup.add(bills, food, health, transport, shopping, communication)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=categories_message,
            reply_markup=markup)
        user_data[user_id]["state"]["type"] = "expense"

    elif call.data in ["salary", "savings", "bills", "food", "health", "transport", "shopping", "communication"]:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=amount_message,
                              reply_markup=None)
        user_data[user_id]["state"]["category"] = call.data

    elif call.data == "confirm":
        state = user_data[user_id]["state"]
        if state:
            category = state["category"]
            amount = state["amount"]
            if state["type"] == "income":
                user_data[user_id]["incomes"][category] += amount
                bot.send_message(call.message.chat.id, f"Added ${amount} to {category}")
            elif state["type"] == "expense":
                user_data[user_id]["expenses"][category] += amount
                bot.send_message(call.message.chat.id, f"Added ${amount} to {category}")
            user_data[user_id]["state"] = {}
        sync()

    elif call.data == "cancel":
        bot.send_message(call.message.chat.id, "Operation cancelled.")
        user_data[user_id]["state"] = {}

# Confirmation ("yes" or "cancel") before adding an amount
@bot.message_handler(func=lambda message: True)
def handle_amount(message):
    user_id = str(message.from_user.id)
    initialize_user_data(user_id, user_data)

    if user_id in user_data and "category" in user_data[user_id]["state"]:
        try:
            amount = float(message.text)
            category = user_data[user_id]["state"]["category"]
            user_data[user_id]["state"]["amount"] = amount

            markup = types.InlineKeyboardMarkup(row_width=2)
            yes_button = types.InlineKeyboardButton("Yes", callback_data="confirm")
            cancel_button = types.InlineKeyboardButton("Cancel", callback_data="cancel")
            markup.add(yes_button, cancel_button)

            bot.send_message(message.chat.id, f"Do you really want to add ${amount} to {category}?", reply_markup=markup)
        except ValueError:
            bot.send_message(message.chat.id, "Please enter a valid number.")

if __name__ == "__main__":
    bot.polling(non_stop=True)
