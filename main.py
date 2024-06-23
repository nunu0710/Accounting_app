from flask import Flask, render_template, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# File path for saving data
data_file = 'data.json'

# Sample inventory and initial account balance
inventory = {}
account_balance = 25000
sales_history = []
purchase_history = []

# Function to save data to JSON file
def save_data():
    data = {
        'inventory': inventory,
        'account_balance': account_balance,
        'sales_history': sales_history,
        'purchase_history': purchase_history
    }
    with open(data_file, 'w') as file:
        json.dump(data, file)

# Function to load data from JSON file
def load_data():
    global inventory, account_balance, sales_history, purchase_history
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            data = json.load(file)
            inventory = data.get('inventory', {})
            account_balance = data.get('account_balance', 25000)
            sales_history = data.get('sales_history', [])
            purchase_history = data.get('purchase_history', [])

# Load initial data when the application starts
load_data()

# Route for home page (index.html)
@app.route('/')
def index():
    return render_template('index.html', inventory=inventory)

# Route for balance page
@app.route('/balance', methods=['GET', 'POST'])
def balance():
    global account_balance
    if request.method == 'POST':
        command = request.form['command'].lower()
        amount = request.form.get('amount', type=int, default=0)
        if command == 'add':
            account_balance += amount
        elif command == 'subtract':
            account_balance -= amount
        save_data()  # Save data after each balance update
    return render_template('balance.html', balance=account_balance)

# Route for sales page
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    global account_balance
    error_message = None
    if request.method == 'POST':
        item_name = request.form['item_name'].lower()
        price = request.form.get('price', type=float)
        quantity = request.form.get('quantity', type=int)
        
        if item_name not in inventory:
            error_message = f"{item_name.capitalize()} is not available in the store"
        elif quantity > inventory[item_name]["quantity"]:
            error_message = f"Not enough {item_name} available in the store"
        else:
            inventory[item_name]["quantity"] -= quantity
            account_balance += quantity * price
            sales_history.append({
                'item': item_name,
                'price': price,
                'quantity': quantity,
                'total': quantity * price,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Check if quantity becomes zero and delete item from inventory
            if inventory[item_name]["quantity"] == 0:
                del inventory[item_name]
            
            save_data()  # Save data after each successful sale
    
    return render_template('sales.html', error_message=error_message)

# Route for purchase page
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    global account_balance
    error_message = None
    if request.method == 'POST':
        item_name = request.form['item_name'].lower()
        price = request.form.get('price', type=float)
        quantity = request.form.get('quantity', type=int)
        total_cost = price * quantity

        if total_cost > account_balance:
            error_message = f"Not enough money to purchase {item_name}"
        else:
            if item_name in inventory:
                inventory[item_name]["quantity"] += quantity
            else:
                inventory[item_name] = {"price": price, "quantity": quantity}
            account_balance -= total_cost
            purchase_history.append({
                'item': item_name,
                'price': price,
                'quantity': quantity,
                'total': total_cost,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_data()  # Save data after each successful purchase
    
    return render_template('purchase.html', error_message=error_message)

# Route for history page
@app.route('/history')
def transaction_history():
    return render_template('history.html', 
                           sales_history=sales_history, 
                           purchase_history=purchase_history)

if __name__ == '__main__':
    app.run(debug=True)
