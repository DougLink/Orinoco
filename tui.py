def shopper_id():
    id_number = input("Please enter your Shopper ID: ")
    return id_number


def welcome(shopper_name):
    if shopper_name is not None:
        message = f"Welcome to Orinoco's Shopping System, {shopper_name}"
        print("-" * len(message))
        print(message)
        print("-" * len(message))
    else:
        return None


def menu():
    mn_header = "ORINOCO-SHOPPER MAIN MENU"
    print(mn_header)
    print("-" * len(mn_header))
    mn_opts = {1: "Display your order history", 2: "Add an item to your basket", 3: "View your basket",
               4: "Change the quantity of an item in your basket", 5: "Remove an item from your basket",
               6: "Checkout", 7: "Exit"}

    for key, value in mn_opts.items():
        print(f"{key}.  {value}")  # printing the keys and values so the user can replicate the option number

    a = int(input("Type the number of the option:"))  # making sure the user input an integer and is saved as so

    if a in mn_opts:  # handling user mistake
        return a
    else:
        error("Invalid Entry")  # calling the error message
        return None


def no_orders():
    message = "No orders placed by this customer"
    print("-" * len(message))
    print(message)
    print("-" * len(message))


def error(error_msg):
    message = f"Error! {error_msg}."  # printing error message
    print("-" * len(message))
    print(message)
    print("-" * len(message))
