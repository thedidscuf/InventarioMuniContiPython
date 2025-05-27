import sqlite3
import datetime

DATABASE_NAME = "inventory.db"

def create_connection():
    """Creates a database connection to the SQLite database specified by DATABASE_NAME."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table():
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
            print(e)
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")

# Call create_table() once when the module is imported to ensure the table exists.
create_table()

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
            return cursor.lastrowid # Return the id of the newly inserted item
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            return None
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")
        return None


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
            return cursor.rowcount > 0 # Return True if update was successful
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
            return cursor.rowcount > 0 # Return True if delete was successful
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
            # Using LOWER() for case-insensitive search
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

if __name__ == '__main__':
    # Initialize the database and table when this script is run directly
    # create_table() is called at module import level, no need to call it again here
    print(f"Database '{DATABASE_NAME}' and table 'inventory' created/ensured.")
    
    # Example usage (uncomment to test):
    # print("Adding items...")
    # item_id1 = add_item("Laptop", 10, "High-performance laptop")
    # item_id2 = add_item("Mouse", 50, "Wireless optical mouse")
    # item_id3 = add_item("Keyboard", 30, "Mechanical keyboard")
    # print(f"Added items with IDs: {item_id1}, {item_id2}, {item_id3}")

    # print("\nAll items:")
    # for item in get_all_items():
    #     print(item)

    # print("\nUpdating item with ID 1...")
    # if item_id1:
    #     update_item(item_id1, "Laptop Pro", 8, "Upgraded high-performance laptop")
    #     print(get_all_items())
    
    # print("\nSearching for 'laptop':")
    # for item in search_items("laptop"):
    #     print(item)

    # print("\nDeleting item with ID 2...")
    # if item_id2:
    #     delete_item(item_id2)
    #     print(get_all_items())
    
    # print("\nSearching for 'Key':") # Test case-insensitivity
    # for item in search_items("Key"):
    #     print(item)
