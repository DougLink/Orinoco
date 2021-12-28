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


def basket_menu(options, title, step):
    index = 1
    option_list = []
    print(f"\n{title}\n")
    for option in options:
        code = option[0]
        desc = option[1]
        print(f"{index}.\t{desc}")
        index += 1
        option_list.append(code)
    selected_option = 0
    while selected_option > len(options) or selected_option == 0:
        prompt = f"Enter the number against the {step} you want to choose: "
        selected_option = int(input(prompt))
    return option_list[selected_option - 1]


def prod_quantity():
    prompt = "Enter the quantity of the selected product you want to buy? "
    quantity = int(input(prompt))
    while quantity <= 0:
        print("The quantity must be greater than 0")
        quantity = int(input(prompt))
    return quantity


def empty_basket():
    empty = "Your basket is empty"
    print("-" * len(empty))
    print(empty)
    print("-" * len(empty))


def basket_title():
    title = "Basket Contents"
    print(title)
    print("-" * len(title))


def change_quantity(items):
    if len(items) == 1:
        prompt = "Enter the new quantity you want to buy: "
        print("-" * len(prompt))
        new_amount = int(input(prompt))
        while new_amount <= 0:
            print("The quantity must be greater than zero")
            new_amount = int(input(prompt))
        product = items[0][1]
        seller = items[0][2]
        changes = [new_amount, product, seller]
        return changes
    else:
        prompt = "Enter the basket item no. of the item you want to change: "
        print("-" * len(prompt))
        item = int(input(prompt))
        while item == 0 or item > len(items):
            print("The basket item no. you have entered is invalid")
            item = int(input(prompt))
        new_amount = int(input("Enter the new quantity of the selected product you want to buy: "))
        while new_amount <= 0:
            print("The quantity must be greater than zero")
            new_amount = int(input("Enter the new quantity you want to buy: "))
        selected_item = items[item-1]
        product = selected_item[1]
        seller = selected_item[2]
        changes = [new_amount, product, seller]
        return changes


def remove_item(items):
    if len(items) == 1:
        confirmation = "Do you definitely want to delete this product and empty your basket (Y/N)? "
        print("-" * len(confirmation))
        answer = str.lower(input(confirmation))
        answers = ["y", "n"]
        while answer not in answers:
            answer = str.lower(input(confirmation))
        if answer == "y":
            product = items[0][1]
            seller = items[0][2]
            return [product, seller]
        else:
            return None
    else:
        prompt = "Enter the basket item no. of the item you want to remove: "
        print("-" * len(prompt))
        item = int(input(prompt))
        while item == 0 or item > len(items):
            print("The basket item no. you have entered is not in your basket")
            item = int(input(prompt))
        confirmation = "Do you definitely want to delete this product and empty your basket (Y/N)? "
        print("-" * len(confirmation))
        answer = str.lower(input(confirmation))
        answers = ["y", "n"]
        while answer not in answers:
            answer = str.lower(input(confirmation))
        if answer == "y":
            selected_item = items[item - 1]
            product = selected_item[1]
            seller = selected_item[2]
            item = [product, seller]
            return item
        else:
            return None


def checkout_conf():
    prompt = "Do you wish to proceed with the checkout (Y or N)? "
    print("-" * len(prompt))
    confirmation = str.lower(input(prompt))
    answers = ["y", "n"]
    while confirmation not in answers:
        confirmation = str.lower(input("Do you wish to proceed with the checkout (Y or N)?? "))
    if confirmation == "y":
        return True
    else:
        return None


def checkout_complete():
    complete = "Checkout complete, your order has been placed"
    print("-" * len(complete))
    print(complete)
    print("-" * len(complete))