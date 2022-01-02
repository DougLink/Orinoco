import sqlite3
import tui
import pandas as pd


def id_checker():
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    id_number = tui.shopper_id()
    c.execute("""SELECT shopper_first_name, shopper_surname 
                FROM shoppers 
                WHERE shopper_id = (?)""", (id_number,))
    item = c.fetchone()  # assigning the first result from the query to a variable
    db.close()
    if item is not None:
        name = f"{item[0]} {item[1]}"
        shopper_id.append(id_number)
        return name
    else:
        return None


def basket_selector():
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    shopper = shopper_id[0]
    c.execute("""SELECT basket_id
                FROM shopper_baskets
                WHERE shopper_id = (?)
                AND DATE(basket_created_date_time) = DATE('now')
                ORDER BY basket_created_date_time DESC
                LIMIT 1""", (shopper,))
    basket_tuple = c.fetchone()
    if basket_tuple is None:
        db = sqlite3.connect("database/Orinoco_db")
        c = db.cursor()
        shopper = shopper_id[0]
        c.execute("""SELECT seq FROM SQLITE_SEQUENCE WHERE name='shopper_baskets'""")
        basket_tuple = c.fetchone()
        basket = basket_tuple[0] + 1  # taking the int from the tuple to add one and use the next basket_id available
        c.execute("""INSERT INTO shopper_baskets (basket_id, shopper_id, basket_created_date_time)
                    VALUES ((?), (?), DATETIME('now'))""", (basket, shopper,))
        db.commit()
        db.close()
        return basket
    else:
        db.close()
        basket = basket_tuple[0]
        return basket


def order_history():
    db = sqlite3.connect("database/Orinoco_db")
    shopper = shopper_id
    # Expanding the amount of rows, columns and the width of the panda visualisation
    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.width", 2000, "display.max_colwidth", 150)
    # Used panda for this visualisation because the way it needed to be displayed
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
                                ORDER BY order_date DESC""", db, params=shopper)
    db.close()
    if history.empty:
        tui.no_orders()
    else:
        history.set_index('OrderID', inplace=True)  # changed the index to the OrderId, so it was displayed as required
        print(history)


def fetch_product_categories():
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""SELECT category_id, category_description FROM categories ORDER BY category_description""")
    result = c.fetchall()  # assigning the whole result from the query to a variable
    db.close()
    return result


def fetch_products(category):
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""SELECT product_id, product_description
                FROM products p
                INNER JOIN categories c ON p.category_id = c.category_id
                WHERE p.category_id = (?) AND product_status = 'Available'
                ORDER BY product_description""", (category,))
    result = c.fetchall()
    db.close()
    return result


def fetch_sellers(product):
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""SELECT ps.seller_id, s.seller_name || ' (' || PRINTF("£%.2f", ps.price) || ')'
                FROM products p
                INNER JOIN product_sellers ps ON p.product_id = ps.product_id
                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                WHERE p.product_id = (?)
                ORDER BY s.seller_name""", (product,))
    result = c.fetchall()
    db.close()
    return result


def fetch_price(product, seller):
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""SELECT price FROM product_sellers WHERE product_id = (?) AND seller_id = (?)""", (product, seller,))
    result = c.fetchall()[0]  # as the result from the function is a tuple used the index to store it as a float
    db.close()
    return result


def add_item(basket, prod, seller, qty, price):
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price)
                VALUES ((?), (?), (?), (?), (?))""", (basket, prod, seller, qty, price,))
    db.commit()
    db.close()
    tui.item_added()


def display_basket(basket_id):
    db = sqlite3.connect("database/Orinoco_db")
    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.width", 2000, "display.max_colwidth", 150)
    result = pd.read_sql_query("""SELECT product_description AS 'Product Description',
                                seller_name AS 'Seller Name', SUM(bc.quantity) AS 'Qty',
                                PRINTF("£%.2f",bc.price) AS 'Price', PRINTF("£%.2f",bc.price*SUM(bc.quantity)) AS 'Total'
                                FROM basket_contents bc
                                INNER JOIN product_sellers ps ON bc.product_id = ps.product_id AND bc.seller_id = ps.seller_id
                                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                                INNER JOIN products p ON ps.product_id = p.product_id
                                WHERE bc.basket_id = (?)
                                GROUP BY product_description, seller_name
                                ORDER BY product_description DESC""", db, params=basket_id)
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


def basket_data(basket_id):  # Similar do basket_display() this function stores important data from the basket
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""SELECT product_description, bc.product_id, bc.seller_id, seller_name
                FROM basket_contents bc
                INNER JOIN product_sellers ps ON bc.product_id = ps.product_id AND bc.seller_id = ps.seller_id
                INNER JOIN sellers s ON ps.seller_id = s.seller_id
                INNER JOIN products p ON ps.product_id = p.product_id
                WHERE bc.basket_id = (?)
                GROUP BY product_description, seller_name
                ORDER BY product_description DESC""", (basket_id,))
    result = c.fetchall()
    db.close()
    return result


def change_amount(item, basket):
    qty = item[0]  # separating the data in the list
    product = item[1]
    seller = item[2]
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""UPDATE basket_contents
                SET quantity = (?)
                WHERE product_id = (?) AND seller_id = (?) AND basket_id = (?)""", (qty, product, seller, basket,))
    db.commit()
    db.close()


def delete_item(item, basket):
    product = item[0]
    seller = item[1]
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""DELETE FROM basket_contents
                WHERE product_id = (?) AND seller_id = (?) AND basket_id = (?)""",
              (product, seller, basket,))
    db.commit()
    db.close()


def delete_basket(basket):
    db = sqlite3.connect("database/Orinoco_db")
    c = db.cursor()
    c.execute("""DELETE FROM shopper_baskets
                WHERE basket_id = (?)""", (basket,))
    db.commit()
    db.close()


def checkout(basket):  # this is the only "complex" query function, its has 4 stages. Creating a new shopper order,
    db = sqlite3.connect("database/Orinoco_db")   # finding the id that was created, creating order for every product,
    c = db.cursor()                               # and deleting the shopper basket(shopper_baskets and basket_contents)
    c.execute("""INSERT INTO shopper_orders (shopper_id, order_date, order_status)
                    VALUES ((?), DATE('now'), 'Placed')""", (shopper_id[0],))
    db.commit()  # the last 3 stages are dependant of the fist being committed, so the id is created and can be found
    c.execute("""SELECT seq FROM SQLITE_SEQUENCE WHERE name='shopper_orders'""")
    order = c.fetchone()[0]
    c.execute("""INSERT INTO ordered_products(order_id, product_id, seller_id, quantity, price, ordered_product_status)
                SELECT (?), product_id, seller_id, quantity, price, 'Placed'
                FROM basket_contents
                WHERE basket_id = (?)""", (order, basket,))
    c.execute("""INSERT OR IGNORE INTO seller_orders(order_id, seller_id)
                    SELECT (?), seller_id
                    FROM basket_contents
                    WHERE basket_id = (?)""", (order, basket,))
    c.execute("""DELETE FROM shopper_baskets WHERE basket_id = (?)""", (basket,))
    c.execute("""DELETE FROM basket_contents WHERE basket_id = (?)""", (basket,))
    db.commit()
    db.close()


shopper_id = []


def run():
    shopper = id_checker()
    if shopper is not None:
        tui.welcome(shopper)
        basket_id = basket_selector()
        while True:
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
        tui.error("Shopper ID not found")


if __name__ == "__main__":
    run()
