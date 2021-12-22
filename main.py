import sqlite3
import tui
from abc import ABC, abstractmethod
import pandas as pd


def id_checker():
    db = sqlite3.connect("database\Orinoco_db")  # connect to database
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
    db = sqlite3.connect("database\Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    i = shopper_id[0]
    c.execute("""SELECT basket_id
                FROM shopper_baskets
                WHERE shopper_id = (?)
                AND DATE(basket_created_date_time) = DATE('now')
                ORDER BY basket_created_date_time DESC
                LIMIT 1""", (i,))
    basket = c.fetchone()
    if basket is None:
        c.execute("""INSERT INTO shopper_baskets (shopper_id, basket_created_date_time)
                    VALUES ((?), DATE('now'))""", (i,))
        db.commit()
        db.close()
    else:
        db.commit()
        db.close()
        return basket


def order_history():
    db = sqlite3.connect("database/Orinoco_db")  # connect to database
    c = db.cursor()  # creating cursor
    i = shopper_id
    pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.width', 2000, "display.max_colwidth", 150)
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
    if history.empty:
        tui.no_orders()
    else:
        history.set_index('OrderID', inplace=True)
        print(history)


#def retrieve_entity():
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


#def retrieve_entity_det():
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


#def categorisation_type():
#    type_category = {"Planets": [], "Non-planets": []}  # creating the dictionary
#    for element in records:
#        if element[1] == "TRUE":  # checking the condition
#            type_category["Planets"].append(element[0])  # populating the dictionary
#        if element[1] == "FALSE":
#            type_category["Non-planets"].append(element[0])
#    return type_category


#def categorisation_gravity():
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


#def summarise():
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


#class AbstractWriter(ABC):  # abstract class
#    def __init__(self, data):  # initializing class
#        self.data = data  # creating parameter

#    def sorting_data(self):  # method to sort out planets and non-planets in alphabetical order
#        planets = []
#        non_planets = []
#        for element in self.data:
#            if element[1] == "TRUE":
#                planets.append(element)
#            if element[1] == "FALSE":
#                non_planets.append(element)
#        planets.sort()  # sorting in alphabetical order
#        non_planets.sort()
#        sorted_entities = {"Planets": planets, "Non-planets": non_planets}
#        return sorted_entities

#    @abstractmethod  # abstract method to return the sorted data
#    def saving_data(self):
#        return self.sorting_data()


#class ConcreteWriter(AbstractWriter):  # concrete class
#    def __init__(self, data):  # initializing class
#        super().__init__(data)  # calling out the parent class
#
#    def saving_data(self):  # method that overwrites the parent and uses the return
#        file = super().saving_data()
#        with open("records.txt", 'w') as outfile:  # creating a txt file
#            json.dump(file, outfile)  # writing the data in JSON format


shopper_id = []


def run():
    id_number = id_checker()
    while True:
        if id_number is None:
            tui.error("Shopper ID not found")  # calling error function
            break
        else:
            tui.welcome(id_number)
            while basket_selector() is None:
                basket_selector()
            basket_id = basket_selector()[0]
            menu_selection = tui.menu()
            if menu_selection == 1:
                order_history()

        # Task 22: Check if the user selected the option for processing data.  If so, then do the following:
        # - Use the appropriate function in the module tui to display a message to indicate that the data processing
        # operation has started.
        # - Process the data (see below).
        # - Use the appropriate function in the module tui to display a message to indicate that the data processing
        # operation has completed.
        #
        # To process the data, it is recommended that you create and call one or more separate functions that do the
        # following:
        # - Use the appropriate function in the module tui to display a menu of options for processing the data.
        # - Check what option has been selected
        #
        #   - If the user selected the option to retrieve an entity then
        #       - Use the appropriate function in the module tui to indicate that the entity retrieval process
        #       has started.
        #       - Use the appropriate function in the module tui to retrieve the entity name
        #       - Find the record for the specified entity in records.  You should appropriately handle the case
        #       where the entity cannot be found.
        #       - Use the appropriate function in the module tui to list the entity
        #       - Use the appropriate function in the module tui to indicate that the entity retrieval process has
        #       completed.
        #
        #   - If the user selected the option to retrieve an entity's details then
        #       - Use the appropriate function in the module tui to indicate that the entity details retrieval
        #       process has started.
        #       - Use the appropriate function in the module tui to retrieve the entity details
        #       - Find the record for the specified entity details in records.  You should appropriately handle the
        #       case where the entity cannot be found.
        #       - Use the appropriate function in the module tui to list the entity
        #       - Use the appropriate function in the module tui to indicate that the entity details retrieval
        #       process has completed.
        #
        #   - If the user selected the option to categorise entities by their type then
        #       - Use the appropriate function in the module tui to indicate that the entity type categorisation
        #       process has started.
        #       - Iterate through each record in records and assemble a dictionary containing a list of planets
        #       and a list of non-planets.
        #       - Use the appropriate function in the module tui to list the categories.
        #       - Use the appropriate function in the module tui to indicate that the entity type categorisation
        #       process has completed.
        #
        #   - If the user selected the option to categorise entities by their gravity then
        #       - Use the appropriate function in the module tui to indicate that the categorisation by entity gravity
        #       process has started.
        #       - Use the appropriate function in the module tui to retrieve a gravity range
        #       - Iterate through each record in records and assemble a dictionary containing lists of entities
        #       grouped into low (below lower limit), medium and high (above upper limit) gravity categories.
        #       - Use the appropriate function in the module tui to list the categories.
        #       - Use the appropriate function in the module tui to indicate that the categorisation by entity gravity
        #       process has completed.
        #
        #   - If the user selected the option to generate an orbit summary then
        #       - Use the appropriate function in the module tui to indicate that the orbit summary process has
        #       started.
        #       - Use the appropriate function in the module tui to retrieve a list of orbited planets.
        #       - Iterate through each record in records and find entities that orbit a planet in the list of
        #       orbited planets.  Assemble the found entities into a nested dictionary such that each entity can be
        #       accessed as follows:
        #           name_of_dict[planet_orbited][category]
        #       where category is "small" if the mean radius of the entity is below 100 and "large" otherwise.
        #       - Use the appropriate function in the module tui to list the categories.
        #       - Use the appropriate function in the module tui to indicate that the orbit summary process has
        #       completed.
        # TODO: Your code here

            elif menu_selection == 2:
                tui.started("Data processing")
                process_selection = tui.process_type()
                if process_selection == 1:
                    tui.started("Retrieve entity")
                    retrieve_entity()
                    tui.completed("Retrieve entity")

                elif process_selection == 2:
                    tui.started("Retrieve entity's details")
                    retrieve_entity_det()
                    tui.completed("Retrieve entity details")

                elif process_selection == 3:
                    tui.started("Categorise entities by type")
                    tui.list_categories(categorisation_type())
                    tui.completed("Categorise entities by type")

                elif process_selection == 4:
                    tui.started("Categorise entities by gravity")
                    tui.list_categories(categorisation_gravity())
                    tui.completed("Categorise entities by gravity")

                elif process_selection == 5:
                    tui.started("Summarise entities by orbit")
                    tui.list_categories(summarise())
                    tui.completed("Summarise entities by orbit")

                tui.completed("Data processing")

        # Task 23: Check if the user selected the option for visualising data.  If so, then do the following:
        # - Use the appropriate function in the module tui to indicate that the data visualisation operation
        # has started.
        # - Visualise the data (see below).
        # - Use the appropriate function in the module tui to display a message to indicate that the data visualisation
        # operation has completed.
        #
        # To visualise the data, it is recommended that you create and call one or more separate functions that do the
        # following:
        # - Use the appropriate function in the module tui to retrieve the type of visualisation to display.
        # - Check what option has been selected
        #
        #   - if the user selected the option to visualise the entity type then
        #       - Use the appropriate function in the module tui to indicate that the entity type visualisation
        #       process has started.
        #       - Use your code from earlier to assemble a dictionary containing a list of planets and a list of
        #       non-planets.
        #       - Use the appropriate function in the module visual to display a pie chart for the number of planets
        #       and non-planets
        #       - Use the appropriate function in the module tui to indicate that the entity type visualisation
        #       process has completed.
        #
        #   - if the user selected the option to visualise the entity gravity then
        #       - Use the appropriate function in the module tui to indicate that the entity gravity visualisation
        #       process has started.
        #       - Use your code from earlier to assemble a dictionary containing lists of entities grouped into
        #       low (below lower limit), medium and high (above upper limit) gravity categories.
        #       - Use the appropriate function in the module visual to display a bar chart for the gravities
        #       - Use the appropriate function in the module tui to indicate that the entity gravity visualisation
        #       process has completed.
        #
        #   - if the user selected the option to visualise the orbit summary then
        #       - Use the appropriate function in the module tui to indicate that the orbit summary visualisation
        #       process has started.
        #       - Use your code from earlier to assemble a nested dictionary of orbiting planets.
        #       - Use the appropriate function in the module visual to display subplots for the orbits
        #       - Use the appropriate function in the module tui to indicate that the orbit summary visualisation
        #       process has completed.
        #
        #   - if the user selected the option to animate the planet gravities then
        #       - Use the appropriate function in the module tui to indicate that the gravity animation visualisation
        #       process has started.
        #       - Use your code from earlier to assemble a dictionary containing lists of entities grouped into
        #       low (below lower limit), medium and high (above upper limit) gravity categories.
        #       - Use the appropriate function in the module visual to animate the gravity.
        #       - Use the appropriate function in the module tui to indicate that the gravity animation visualisation
        #       process has completed.
        # TODO: Your code here

            elif menu_selection == 3:
                tui.started("Data visualising")
                visualisation_selection = tui.visualise()
                if visualisation_selection == 1:
                    tui.started("Visualising entities by type")
                    visualisation_type = categorisation_type()
                    vi.entities_pie(visualisation_type)
                    tui.completed("Visualising entities by type")

                elif visualisation_selection == 2:
                    tui.started("Visualising entities by gravity")
                    visualisation_gravity = categorisation_gravity()
                    vi.entities_bar(visualisation_gravity)
                    tui.completed("Visualising entities by gravity")

                elif visualisation_selection == 3:
                    tui.started("Visualising summary of orbits")
                    visualisation_orbits = summarise()
                    vi.orbits(visualisation_orbits)
                    tui.completed("Visualising summary of orbits")

                elif visualisation_selection == 4:
                    tui.started("Visualising animate gravities")
                    animation_gravity = categorisation_gravity()
                    vi.gravity_animation(animation_gravity)
                    tui.completed("Visualising animate gravities")

                tui.completed("Data visualising")

        # Task 28: Check if the user selected the option for saving data.  If so, then do the following:
        # - Use the appropriate function in the module tui to indicate that the save data operation has started.
        # - Save the data (see below)
        # - Use the appropriate function in the module tui to indicate that the save data operation has completed.
        #
        # To save the data, you should demonstrate the application of OOP principles including the concepts of
        # abstraction and inheritance.  You should create an AbstractWriter class with abstract methods and a concrete
        # Writer class that inherits from the AbstractWriter class.  You should then use this to write the records to
        # a JSON file using in the following order: all the planets in alphabetical order followed by non-planets
        # in alphabetical order.
        # TODO: Your code here

            elif menu_selection == 4:
                tui.started("Data saving")
                ConcreteWriter(records).saving_data()
                tui.completed("Data saving")

        # Task 29: Check if the user selected the option for exiting.  If so, then do the following:
        # break out of the loop
        # TODO: Your code here

            elif menu_selection == 7:
                break

        # Task 30: If the user selected an invalid option then use the appropriate function of the module tui to
        # display an error message
        # TODO: Your code here
            else:
                tui.error("Invalid Entry")


if __name__ == "__main__":
    run()
