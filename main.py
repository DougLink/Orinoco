import sqlite3
import tui
import pandas as pd


def id_checker():
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    id_number = tui.shopper_id()  # assigning the return to a variable
    c.execute("""SELECT shopper_first_name, shopper_surname 
                FROM shoppers 
                WHERE shopper_id = (?)""", (id_number,))  # Query that search for the shopper_id and return their name
    item = c.fetchone()
    db.commit()
    db.close()
    if item is not None:
        name = f"{item[0]} {item[1]}"
        shopper_id.append(id_number)
        return name
    else:

        return None


def basket_selector():
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    i = shopper_id[0]
    c.execute("""SELECT basket_id
                FROM shopper_baskets
                WHERE shopper_id = (?)
                AND DATE(basket_created_date_time) = DATE('now')
                ORDER BY basket_created_date_time DESC
                LIMIT 1""", (i,))
    basket_tuple = c.fetchone()
    if basket_tuple is None:
        db = sqlite3.connect("database/Orinoco_db")  # connect to database
        c = db.cursor()  # creating cursor
        i = shopper_id[0]
        c.execute("""SELECT seq FROM SQLITE_SEQUENCE WHERE name='shopper_baskets'""")
        basket_tuple = c.fetchone()
        basket = basket_tuple[0] + 1
        c.execute("""INSERT INTO shopper_baskets (basket_id, shopper_id, basket_created_date_time)
                    VALUES ((?), (?), DATETIME('now'))""", (basket, i,))
        db.commit()
        db.close()
        return basket
    else:
        db.commit()
        db.close()
        basket = basket_tuple[0]
        return basket


def order_history():
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    i = shopper_id
    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.width", 2000, "display.max_colwidth",
                  150)
    history = pd.read_sql_query("""SELECT so.order_id AS 'OrderID', order_date AS 'Order Date',
                                product_description AS 'Product Description', seller_name AS 'Seller',
                                PRINTF("£%.2f", op.price) AS 'Price', op.quantity AS 'Qty',
                                ordered_product_status AS 'Status'
                                FROM shopper_orders so
                                INNER JOIN ordered_products op ON so.order_id = op.order_id
                                INNER JOIN product_sellers ps ON op.product_id = ps.product_id AND op.seller_id = ps.seller_id
                                INNER JOIN products p ON ps.product_id = p.product_id
                                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                                WHERE so.shopper_id = (?)
                                ORDER BY order_date DESC""", db, params=i)
    db.commit()
    db.close()
    if history.empty:
        tui.no_orders()
    else:
        history.set_index('OrderID', inplace=True)
        print(history)


def fetch_product_categories():
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""SELECT category_id, category_description FROM categories ORDER BY category_description""")
    result = c.fetchall()
    db.commit()
    db.close()
    return result


def fetch_products(category):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""SELECT product_id, product_description
                FROM products p
                INNER JOIN categories c ON p.category_id = c.category_id
                WHERE p.category_id = (?) AND product_status = 'Available'
                ORDER BY product_description""", (category,))
    result = c.fetchall()
    db.commit()
    db.close()
    return result


def fetch_sellers(product):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""SELECT ps.seller_id, s.seller_name || ' (' || PRINTF("£%.2f", ps.price) || ')'
                FROM products p
                INNER JOIN product_sellers ps ON p.product_id = ps.product_id
                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                WHERE p.product_id = (?)
                ORDER BY s.seller_name""", (product,))
    result = c.fetchall()
    db.commit()
    db.close()
    return result


def fetch_price(product, seller):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""SELECT price FROM product_sellers WHERE product_id = (?) AND seller_id = (?)""", (product, seller,))
    result = c.fetchall()[0]
    db.commit()
    db.close()
    return result


def add_item(basket, prod, seller, qty, price):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price)
                VALUES ((?), (?), (?), (?), (?))""", (basket, prod, seller, qty, price,))
    db.commit()
    db.close()


def display_basket(basket_id):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.width", 2000, "display.max_colwidth",
                  150)
    result = pd.read_sql_query("""SELECT product_description AS 'Product Description',
                                seller_name AS 'Seller Name', SUM(bc.quantity) AS 'Qty',
                                PRINTF("£%.2f", bc.price) AS 'Price', PRINTF("£%.2f", (bc.price*SUM(bc.quantity))) AS 'Total'
                                FROM basket_contents bc
                                INNER JOIN product_sellers ps ON bc.product_id = ps.product_id AND bc.seller_id = ps.seller_id
                                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                                INNER JOIN products p ON ps.product_id = p.product_id
                                WHERE bc.basket_id = (?)
                                GROUP BY product_description, seller_name
                                ORDER BY product_description DESC""", db, params=basket_id)
    db.commit()
    db.close()
    if result.empty:
        tui.empty_basket()
        return None
    else:
        result.rename_axis('Basket Item', inplace=True)
        result.index = result.index + 1
        tui.basket_title()
        print(result)
        return result


def basket_data(basket_id):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""SELECT product_description, bc.product_id, bc.seller_id, seller_name
                FROM basket_contents bc
                INNER JOIN product_sellers ps ON bc.product_id = ps.product_id AND bc.seller_id = ps.seller_id
                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                INNER JOIN products p ON ps.product_id = p.product_id
                WHERE bc.basket_id = (?)
                GROUP BY product_description, seller_name
                ORDER BY product_description DESC""", (basket_id,))
    result = c.fetchall()
    db.commit()
    db.close()
    return result


def change_amount(item, basket):
    qty = item[0]
    product = item[1]
    seller = item[2]
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""UPDATE basket_contents
                SET quantity = (?)
                WHERE product_id = (?) AND seller_id = (?) AND basket_id = (?)""", (qty, product, seller, basket,))
    db.commit()
    db.close()


def delete_item(item, basket):
    product = item[0]
    seller = item[1]
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""DELETE FROM basket_contents
                WHERE product_id = (?) AND seller_id = (?) AND basket_id = (?)""",
              (product, seller, basket,))
    db.commit()
    db.close()


def delete_basket(basket):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""DELETE FROM shopper_baskets
                WHERE basket_id = (?)""", (basket,))
    db.commit()
    db.close()


def checkout(basket):
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    c.execute("""INSERT INTO shopper_orders (shopper_id, order_date, order_status)
                    VALUES ((?), DATE('now'), 'Placed')""", (shopper_id[0],))
    db.commit()
    c.execute("""SELECT seq FROM SQLITE_SEQUENCE WHERE name='shopper_orders'""")
    order = c.fetchone()[0]
    c.execute("""INSERT INTO ordered_products(order_id, product_id, seller_id, quantity, price, ordered_product_status)
                SELECT (?), product_id, seller_id, quantity, price, 'Placed'
                FROM basket_contents
                WHERE basket_id = (?)""", (order, basket,))
    c.execute("""DELETE FROM shopper_baskets WHERE basket_id = (?)""", (basket,))
    c.execute("""DELETE FROM basket_contents WHERE basket_id = (?)""", (basket,))
    db.commit()
    db.close()


# def retrieve_entity():
#    entity = tui.entity_name()
#    records_entities = []
#    for element in records:
#        records_entities.append(element[0])  # populating a list with all entities names for verification
#    while entity not in records_entities:
#        tui.error("Entity not found")
#        entity = tui.entity_name()
#    result = []
#    for element in records:
#        if element[0] == entity:  # populating list with all the details of matching entities
#            result.append(element)
#    while len(result[0]) == 0:
#        tui.error("Entity not found")
#        retrieve_entity()
#    tui.list_entity(result[0])  # handling the fact that was created a list of lists


# def retrieve_entity_det():
#    details = tui.entity_details()
#    records_entities = []
#    for element in records:
#        records_entities.append(element[0])
#    while details[0] not in records_entities:
#        tui.error("Entity not found")
#        details = tui.entity_details()
#    entity_name = details[0]
#    selected_rows = list(map(int, details[1]))  # assigning the string item to a integer variable
#    result = []
#    for element in records:
#        if element[0] == entity_name:
#            result.append(element)
#    data = result[0]
#    while len(result[0]) == 0:
#        tui.error("Entity not found")
#        retrieve_entity_det()
#    tui.list_entity(data, selected_rows)


# def categorisation_type():
#    type_category = {"Planets": [], "Non-planets": []}  # creating the dictionary
#    for element in records:
#        if element[1] == "TRUE":  # checking the condition
#            type_category["Planets"].append(element[0])  # populating the dictionary
#        if element[1] == "FALSE":
#            type_category["Non-planets"].append(element[0])
#    return type_category


# def categorisation_gravity():
#    gravity_category = {"Low": [], "Medium": [], "High": []}
#    ranges = tui.gravity_range()
#    for element in records:
#        if float(element[8]) < ranges[0]:
#            gravity_category["Low"].append(element[0])
#        elif float(element[8]) > ranges[1]:
#           gravity_category["High"].append(element[0])
#        else:
#            gravity_category["Medium"].append(element[0])
#   return gravity_category


# def summarise():
#    orbit_summary = {}
#    orbit_planets = tui.orbits()
#    for planet in orbit_planets:
#        orbit_summary[planet] = {"Small": [], "Large": []}
#    for element in records:
#        if element[21] in orbit_planets and float(element[10]) < 100:
#            orbit_summary[element[21]]["Small"].append(element[0])
#        if element[21] in orbit_planets and float(element[10]) >= 100:
#            orbit_summary[element[21]]["Large"].append(element[0])
#    return orbit_summary


shopper_id = []


def run():
    id_number = id_checker()
    while True:
        if id_number is None:
            tui.error("Shopper ID not found")  # calling error function
            break
        else:
            tui.welcome(id_number)
            basket_id = basket_selector()
            menu_selection = tui.menu()
            if menu_selection == 1:
                order_history()
            elif menu_selection == 2:
                categories = fetch_product_categories()
                cat_selected = tui.basket_menu(categories, "Product Categories", "product categories")
                products = fetch_products(cat_selected)
                prod_selected = tui.basket_menu(products, "Product", "product")
                sellers = fetch_sellers(prod_selected)
                seller_selected = tui.basket_menu(sellers, "Sellers who sell this product", "seller")
                quantity_selected = tui.prod_quantity()
                price = fetch_price(prod_selected, seller_selected)[0]
                basket_id = basket_selector()
                add_item(basket_id, prod_selected, seller_selected, quantity_selected, price)
            elif menu_selection == 3:
                display_basket((basket_id,))
            elif menu_selection == 4:
                basket = display_basket((basket_id,))
                if basket is not None:
                    changes = tui.change_quantity(basket_data(basket_id))
                    change_amount(changes, basket_id)
                    display_basket((basket_id,))
            elif menu_selection == 5:
                basket = display_basket((basket_id,))
                if basket is not None:
                    item_to_remove = tui.remove_item(basket_data(basket_id))
                    if item_to_remove is not None:
                        delete_item(item_to_remove, basket_id)
                        basket = display_basket((basket_id,))
                        if basket is None:
                            delete_basket(basket_id)
            elif menu_selection == 6:
                basket = display_basket((basket_id,))
                if basket is not None:
                    if tui.checkout_conf() is True:
                        checkout(basket_id)
                        tui.checkout_complete()
            elif menu_selection == 7:
                break
            else:
                tui.error("Invalid Entry")


if __name__ == "__main__":
    run()
