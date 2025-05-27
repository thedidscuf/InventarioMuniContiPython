import sqlite3
import datetime

DATABASE_NAME = "inventory.db"

def create_connection():
    """Creates a database connection to the SQLite database specified by DATABASE_NAME."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON;")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_inventory_table():
    """Creates the inventory table if it doesn't exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    description TEXT,
                    date_added TEXT,
                    last_modified TEXT
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating inventory table: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection for inventory table.")

def create_product_outflows_table():
    """Creates the product_outflows table if it doesn't exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_outflows (
                    outflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    quantity_dispatched INTEGER NOT NULL,
                    department_name TEXT NOT NULL,
                    date_dispatched TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (item_id) REFERENCES inventory (id) ON DELETE CASCADE
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating product_outflows table: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection for product_outflows table.")

def initialize_database_tables():
    """Initializes all necessary tables in the database."""
    create_inventory_table()
    create_product_outflows_table()

# Call initialize_database_tables() once when the module is imported.
initialize_database_tables()

def add_item(name, quantity, description):
    """Adds a new item to the inventory."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            current_timestamp = datetime.datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO inventory (name, quantity, description, date_added, last_modified)
                VALUES (?, ?, ?, ?, ?)
            """, (name, quantity, description, current_timestamp, current_timestamp))
            conn.commit()
            return cursor.lastrowid 
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            return None
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")
        return None

def get_item_by_id(item_id):
    """Retrieves a single item from the inventory by its ID."""
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create the database connection.")
        return None
    
    item = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, quantity, description, date_added, last_modified FROM inventory WHERE id = ?", (item_id,))
        item = cursor.fetchone() # Returns a tuple or None
    except sqlite3.Error as e:
        print(f"Error getting item by ID {item_id}: {e}")
    finally:
        if conn:
            conn.close()
    return item

def get_all_items():
    """Retrieves all items from the inventory, ordered by id."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, quantity, description, date_added, last_modified FROM inventory ORDER BY id")
            items = cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error getting all items: {e}")
            return []
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")
        return []

def update_item(id, name, quantity, description):
    """Updates an existing item in the inventory."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            current_timestamp = datetime.datetime.now().isoformat()
            cursor.execute("""
                UPDATE inventory
                SET name = ?, quantity = ?, description = ?, last_modified = ?
                WHERE id = ?
            """, (name, quantity, description, current_timestamp, id))
            conn.commit()
            return cursor.rowcount > 0 
        except sqlite3.Error as e:
            print(f"Error updating item {id}: {e}")
            return False
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")
        return False

def delete_item(id):
    """Deletes an item from the inventory by id."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting item {id}: {e}")
            return False
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")
        return False

def search_items(query):
    """Searches for items by name (case-insensitive)."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, quantity, description, date_added, last_modified
                FROM inventory
                WHERE LOWER(name) LIKE LOWER(?)
                ORDER BY id
            """, ('%' + query + '%',))
            items = cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error searching items: {e}")
            return []
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")
        return []

# --- Product Outflow Functions ---

def add_product_outflow(item_id, quantity_dispatched, department_name, notes):
    """
    Adds a product outflow record and updates inventory quantity in a transaction.
    Returns the outflow_id if successful, None otherwise.
    """
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create the database connection for product outflow.")
        return None

    new_outflow_id = None
    try:
        conn.execute("BEGIN TRANSACTION;")
        cursor = conn.cursor()

        # Operation 1: Check and Update Inventory
        # Using get_item_by_id to fetch current item details
        item_row = get_item_by_id(item_id) # Note: This opens a new connection. For transactions, it's better to use the same cursor.
                                           # However, get_item_by_id as a separate function will close its own connection.
                                           # For robust transaction, the SELECT should use the 'cursor' from this function.
        
        # Re-fetching item data using the transaction's cursor for atomicity
        cursor.execute("SELECT id, name, quantity, description, date_added, last_modified FROM inventory WHERE id = ?", (item_id,))
        item_row_for_transaction = cursor.fetchone()


        if item_row_for_transaction is None:
            print(f"Error: Item with ID {item_id} not found in inventory.")
            conn.execute("ROLLBACK;")
            return None
        
        current_quantity = item_row_for_transaction[2] # quantity is at index 2
        if current_quantity < quantity_dispatched:
            print(f"Error: Insufficient stock for item ID {item_id}. Available: {current_quantity}, Required: {quantity_dispatched}")
            conn.execute("ROLLBACK;")
            return None

        new_inventory_quantity = current_quantity - quantity_dispatched
        current_timestamp_inventory = datetime.datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE inventory
            SET quantity = ?, last_modified = ?
            WHERE id = ?
        """, (new_inventory_quantity, current_timestamp_inventory, item_id))

        # Operation 2: Insert into product_outflows
        date_dispatched_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO product_outflows (item_id, quantity_dispatched, department_name, date_dispatched, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (item_id, quantity_dispatched, department_name, date_dispatched_str, notes))
        
        new_outflow_id = cursor.lastrowid
        conn.execute("COMMIT;")

    except sqlite3.Error as e:
        print(f"Database error in add_product_outflow: {e}")
        if conn:
            conn.execute("ROLLBACK;")
        new_outflow_id = None 
    finally:
        if conn:
            conn.close()
            
    return new_outflow_id

def get_outflows_for_item(item_id):
    """Retrieves all outflow records for a specific item_id, ordered by date_dispatched descending."""
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create the database connection.")
        return []
    
    items = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT outflow_id, item_id, quantity_dispatched, department_name, date_dispatched, notes 
            FROM product_outflows 
            WHERE item_id = ? 
            ORDER BY date_dispatched DESC
        """, (item_id,))
        items = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting outflows for item {item_id}: {e}")
    finally:
        if conn:
            conn.close()
    return items

def get_outflows_by_department(department_name):
    """Retrieves all outflow records for a specific department_name, ordered by date_dispatched descending."""
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create the database connection.")
        return []
        
    items = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT outflow_id, item_id, quantity_dispatched, department_name, date_dispatched, notes 
            FROM product_outflows 
            WHERE department_name = ? 
            ORDER BY date_dispatched DESC
        """, (department_name,))
        items = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting outflows for department {department_name}: {e}")
    finally:
        if conn:
            conn.close()
    return items

def get_all_outflows():
    """Retrieves all records from the product_outflows table, ordered by date_dispatched descending."""
    conn = create_connection()
    if conn is None:
        print("Error! Cannot create the database connection.")
        return []
        
    items = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT outflow_id, item_id, quantity_dispatched, department_name, date_dispatched, notes 
            FROM product_outflows 
            ORDER BY date_dispatched DESC
        """)
        items = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error getting all outflows: {e}")
    finally:
        if conn:
            conn.close()
    return items

if __name__ == '__main__':
    print(f"Database '{DATABASE_NAME}' and tables ('inventory', 'product_outflows') created/ensured.")
    
    # Example usage:
    # item1 = add_item("Test Item A", 100, "Item A for testing outflows")
    # item2 = add_item("Test Item B", 50, "Item B for testing outflows")

    # if item1:
    #    print(f"Item A (ID: {item1}) stock: {get_item_by_id(item1)[2]}")
    #    outflow_a1 = add_product_outflow(item1, 10, "R&D", "Project X materials")
    #    print(f"Outflow A1 ID: {outflow_a1}, Item A stock: {get_item_by_id(item1)[2]}")
    #    outflow_a2 = add_product_outflow(item1, 200, "R&D", "This should fail - insufficient")
    #    print(f"Outflow A2 ID: {outflow_a2}, Item A stock: {get_item_by_id(item1)[2]}")
    
    # if item2:
    #    print(f"Item B (ID: {item2}) stock: {get_item_by_id(item2)[2]}")
    #    outflow_b1 = add_product_outflow(item2, 5, "Marketing", "Promo event")
    #    print(f"Outflow B1 ID: {outflow_b1}, Item B stock: {get_item_by_id(item2)[2]}")

    # print("\nAll Outflows:")
    # for r in get_all_outflows(): print(r)
    # print("\nOutflows for Item A:")
    # if item1: print(get_outflows_for_item(item1))
    # print("\nOutflows for R&D:")
    # print(get_outflows_by_department("R&D"))
