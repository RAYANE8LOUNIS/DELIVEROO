import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json
import os
# from Pillow import image, ImageTk
# File to store orders
ORDERS_FILE = "rayane.order"

def TAke_orders():
    """Load orders from a file, and creating it if it doesn't exist for more help."""
    try:
        if not os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'w') as file:
                json.dump([], file)  #this should create an empty list if file doesn't exist for more efficasity 
        with open(ORDERS_FILE, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        messagebox.showerror("Error", f"Failed to load or initialize {ORDERS_FILE}.")
        return []
    
# create a function to save orders to the file
def savee_orderss():
    try:
        with open(ORDERS_FILE, 'w') as file:
            json.dump(orders, file, indent=4)
    except IOError:
        messagebox.showerror("Error", "Failed to save orders.")
        
 # give a name to the orders list
orders = TAke_orders()        

# parameters to choose and configure the style of my app backround 
STYLE = {
    "bg": "#1e3a5f",
    "fg": "white",
    "font": ("Arial", 12)
}

# create a window wich will be display on the screen
def centerr_windoww(window, width=600, height=400):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    

# Bubble sort to sort orders by price as required always when we press the view order button the result will be sorted 
def bubble_sort_orders():
    n = len(orders)
    for i in range(n):
        for j in range(0, n - i - 1):
            if orders[j]['price'] < orders[j + 1]['price']:
                orders[j], orders[j + 1] = orders[j + 1], orders[j] 

# Calculate price if it is national or international or if it is in england the price will be dubble 
def calculate_price(region, is_fast, is_international):
    base_price = 25
    region_prices = {"England": 2, "Scotland": 1.5, "Wales": 1.15, "Northern Ireland": 1} # high taxes in england 
    price = base_price * region_prices.get(region, 1)
    if is_fast:
        price *= 2 
    if is_international:
        price += 50
    return price

 # a function to add an order to the list 
def add_order():
    name = name_entry.get().strip()
    address = address_entry.get().strip()
    item = item_entry.get().strip()
    delivery_person = delivery_person_combobox.get().strip()
    delivery_method = delivery_method_combobox.get().strip()
    region = region_combobox.get().strip()
    is_fast = fast_delivery_var.get()
    is_international = international_delivery_var.get()

    if not (name and address and item and delivery_person and delivery_method and region):
        messagebox.showerror("Error", "All fields are required! Please renter and put all information for batter service ")
        return

    final_price = calculate_price(region, is_fast, is_international)

  # option to open the payment window to valididat the order 
    open_payment_window(final_price, name, address, item, delivery_person, delivery_method, region, is_fast, is_international)

# I have create a function to show and view orders on the app 

def view_orders():
    # all the orders will be sorted and displayed because i had creat before a bubble sort for this perpus 
    bubble_sort_orders()

    orders_text.delete(1.0, tk.END)
    if not orders:
        orders_text.insert(tk.END, "No orders available.\n")
    else:
        for i, order in enumerate(orders):
            status = "Delivered" if order.get("delivered", False) else "Pending"
            orders_text.insert(
                tk.END,
                f"{i + 1}. {order['name']} - {order['address']} - {order['item']} - "
                f"{status} - Price: £{order['price']:.2f}\n"
            )        
   # function to clear input to restrat another order 
def clear_inputs():
    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    item_entry.delete(0, tk.END)
    delivery_person_combobox.set("")
    delivery_method_combobox.set("")
    region_combobox.set("")
    fast_delivery_var.set(False)
    international_delivery_var.set(False)

 # this is to creat the payment window function
def open_payment_window(price, name, address, item, delivery_person, delivery_method, region, is_fast, is_international):
    """Open a payment window where the user confirms the payment."""
    def confirm_payment(): # function to confirm the payment 
        """Handle the payment confirmation and add the order."""
        payment_method = payment_method_combobox.get().strip()
        card_number = card_number_entry.get().strip()
        card_expiry = card_expiry_entry.get().strip()
        card_cvc = card_cvc_entry.get().strip()   
    
        if not payment_method: # error handaling of payment methode 
            messagebox.showerror("Error", "Please select a payment method!")
            return
    
        if payment_method in ["Credit Card", "Debit Card"]:
            # must be a validate card number to validate the payment 
            if len(card_number) != 16 or not card_number.isdigit():
                messagebox.showerror("Error", "Card number must be 16 digits!")
                return
            
            # validate card details expiration date should be (MM/YY format)
            try:
                expiry_month, expiry_year = map(int, card_expiry.split('/'))
                current_year = datetime.now().year % 100  # Last two digits of current year
                current_month = datetime.now().month
                if expiry_month < 1 or expiry_month > 12 or expiry_year < current_year or (expiry_year == current_year and expiry_month < current_month):
                    messagebox.showerror("Error", "Card expiration date is invalid!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid expiration date format! Use MM/YY.")
                return
            
             # and also chek validate CVV for the card 
            if len(card_cvc) not in [3, 4] or not card_cvc.isdigit():
                messagebox.showerror("Error", "CVV must be 3 or 4 digits!")
                return
              #for the payple methode we don't need any information
        elif payment_method == "PayPal":
            # PayPal is always valide (no card details needed)
            if card_number or card_expiry or card_cvc:
                messagebox.showerror("Error", "Card details are not required for PayPal! please leave it emty")
                return 

        # After payment is confirmed,than we can add the order to the list 
        orders.append({
            'name': name,
            'address': address,
            'item': item,
            'delivered': False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'delivery_person': delivery_person,
            'delivery_method': delivery_method,
            'region': region,
            'fast_delivery': is_fast,
            'international': is_international,
            'price': price
        })
        save_orders()
        messagebox.showinfo("Success", f"Order added successfully! Final Price: £{price:.2f}")
        payment_window.destroy()
        clear_inputs()  # this will clear all the inputs after successful addition  it means that after when we will finish every thing it will be emty 

    # this is to Create a payment window
    payment_window = tk.Toplevel(root)
    payment_window.title("Payment Confirmation")
    payment_window.config(bg=STYLE["bg"])
    center_window(payment_window, 600, 400)    

     # show and display the final price 
    tk.Label(payment_window, text=f"Total Amount: £{price:.2f}", **STYLE).pack(pady=10) 

    # show the Payment method in payment window 
    tk.Label(payment_window, text="Payment Method:", **STYLE).pack(pady=5)
    payment_method_combobox = ttk.Combobox(payment_window, values=["Credit Card", "Debit Card", "PayPal"], width=47)
    payment_method_combobox.pack()  

    # insert the card details 
    tk.Label(payment_window, text="Card Number (16 digits):", **STYLE).pack(pady=5)
    card_number_entry = tk.Entry(payment_window, width=40)
    card_number_entry.pack()

    #inser an expiry date 
    tk.Label(payment_window, text="Card Expiry (MM/YY):", **STYLE).pack(pady=5)
    card_expiry_entry = tk.Entry(payment_window, width=40)
    card_expiry_entry.pack()

    # inser the ccv code of cards and show it on the window
    tk.Label(payment_window, text="Card CVC (3 or 4 digits):", **STYLE).pack(pady=5)
    card_cvc_entry = tk.Entry(payment_window, width=40)
    card_cvc_entry.pack()

# the button of payment confirmation
    tk.Button(payment_window, text="Confirm Payment", command=confirm_payment, bg=STYLE["bg"], fg=STYLE["fg"]).pack(pady=20)

    # this is the function to create rider application window
def open_rider_application_window(): #main name of the function 
    """Open the Rider Application window to add more rider (toghether we can )."""
    def submit_rider_application():
        """Handle rider application submission (submit your application now )."""
        rider_name = rider_name_entry.get().strip()
        rider_address = rider_address_entry.get().strip()
        bank_details = bank_details_entry.get().strip()
        sort_code = sort_code_entry.get().strip()
        experience = experience_combobox.get().strip()
        terms_agreement = terms_agree_var.get()
        right_to_work = right_to_work_combobox.get().strip()

    # Validate fields and ckech if evry thing is good 
        if not (rider_name and rider_address and bank_details and sort_code and experience and right_to_work):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # see and check the valide of bank details
        if len(bank_details) != 8 or not bank_details.isdigit():
            messagebox.showerror("Error", "Bank account number must be 8 digits! please enter 8 digits!")
            return
        
        # see and check the valide of sort code
        if len(sort_code) != 6 or not sort_code.isdigit():
            messagebox.showerror("Error", "Sort code must be 6 digits! please enter 6 digits!")
            return
        
 # Check terms agreement you should agree with our terms and agreements 
        if not terms_agreement:
            messagebox.showerror("Error", "You must agree to the terms and conditions!")
            return
        
         # Right-to-work validation
        if right_to_work not in ["British Passport", "Valid Share Code (UKVI)", "Irish Passport" , "Settelment"]:
            messagebox.showerror("Error", "You must select a valid right to work option!")
            return
        
        # the final message which will be display on the window if every thing is done 
        messagebox.showinfo("Success", "Rider application submitted successfully! thank u for choosing Deliveroo! safe Ride ")
        rider_window.destroy() # destroy the rider application window to see the main window to make more orders 

    #this is to create a new window for rider application
    rider_window = tk.Toplevel(root)
    rider_window.title("Rider Application (thank u for chossing Deliveroo)")
    rider_window.config(bg=STYLE["bg"])
    center_window(rider_window, 700, 600)

    # Input fields
    # this is to create a place for name for the rider 
    tk.Label(rider_window, text="Name:", **STYLE).pack(pady=5)
    rider_name_entry = tk.Entry(rider_window, width=50)
    rider_name_entry.pack()

# this is to create a place for the rider adress 
    tk.Label(rider_window, text="Address:", **STYLE).pack(pady=5)
    rider_address_entry = tk.Entry(rider_window, width=50)
    rider_address_entry.pack()


# this is to create a place for the rider bank account number 
    tk.Label(rider_window, text="Bank Account Number:", **STYLE).pack(pady=5)
    bank_details_entry = tk.Entry(rider_window, width=50)
    bank_details_entry.pack()

#  this is to create a place for the rider sort code 
    tk.Label(rider_window, text="Sort Code:", **STYLE).pack(pady=5)
    sort_code_entry = tk.Entry(rider_window, width=50)
    sort_code_entry.pack()
