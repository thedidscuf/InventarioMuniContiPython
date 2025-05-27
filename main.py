import tkinter as tk
from tkinter import ttk, messagebox
import database

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Municipal Warehouse Inventory")
        self.geometry("800x600") # Increased size for more columns

        # database.create_table() is called on import in database.py

        self.create_widgets()
        self.load_inventory()

    def create_widgets(self):
        # Frame for input
        input_frame = ttk.LabelFrame(self, text="Add New Item")
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=50)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(input_frame, width=15)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)

        add_button = ttk.Button(input_frame, text="Add Item", command=self.add_new_item)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame for displaying items
        display_frame = ttk.LabelFrame(self, text="Inventory Items")
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Define Treeview columns
        columns = ("id", "name", "quantity", "description", "date_added", "last_modified")
        self.items_tree = ttk.Treeview(display_frame, columns=columns, show="headings")

        self.items_tree.heading("id", text="ID")
        self.items_tree.heading("name", text="Name")
        self.items_tree.heading("quantity", text="Quantity")
        self.items_tree.heading("description", text="Description")
        self.items_tree.heading("date_added", text="Date Added")
        self.items_tree.heading("last_modified", text="Last Modified")

        self.items_tree.column("id", width=40, anchor="center")
        self.items_tree.column("name", width=150)
        self.items_tree.column("quantity", width=70, anchor="center")
        self.items_tree.column("description", width=250)
        self.items_tree.column("date_added", width=130, anchor="center")
        self.items_tree.column("last_modified", width=130, anchor="center")
        
        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.items_tree.pack(fill="both", expand=True, side=tk.LEFT)
        
        # Bind selection event
        self.items_tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.selected_item_id = None

        # --- Action Buttons Frame ---
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=5)

        self.edit_button = ttk.Button(action_frame, text="Edit Selected", command=self.edit_selected_item, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(action_frame, text="Delete Selected", command=self.delete_selected_item, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(action_frame, text="Refresh List", command=self.load_inventory)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # --- Search Frame ---
        search_outer_frame = ttk.LabelFrame(self, text="Search Inventory")
        search_outer_frame.pack(fill="x", padx=10, pady=10)
        
        search_frame = ttk.Frame(search_outer_frame) # Inner frame for better padding control
        search_frame.pack(padx=5, pady=5)

        ttk.Label(search_frame, text="Search by Name:").pack(side=tk.LEFT, padx=(0,5))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0,5))
        
        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_inventory)
        self.search_button.pack(side=tk.LEFT, padx=(0,5))
        
        self.clear_search_button = ttk.Button(search_frame, text="Clear Search", command=self.clear_search)
        self.clear_search_button.pack(side=tk.LEFT)


    def on_item_select(self, event):
        selected_items = self.items_tree.selection()
        if selected_items:
            # Get the actual item ID from the first column of the selected row
            self.selected_item_id = self.items_tree.item(selected_items[0])['values'][0]
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.selected_item_id = None
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)

    def clear_selection_and_disable_buttons(self):
        if self.items_tree.selection(): # Check if there is any selection
             self.items_tree.selection_remove(self.items_tree.selection())
        self.selected_item_id = None
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)


    def add_new_item(self):
        name = self.name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        description = self.desc_entry.get().strip()

        if not name:
            messagebox.showerror("Input Validation Error", "Name cannot be empty.", parent=self)
            return
        if not quantity_str:
            messagebox.showerror("Input Validation Error", "Quantity cannot be empty.", parent=self)
            return

        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Input Validation Error", "Quantity must be a valid integer.", parent=self)
            return
        
        if quantity < 0:
            messagebox.showerror("Input Validation Error", "Quantity cannot be negative.", parent=self)
            return

        item_id = database.add_item(name, quantity, description)
        if item_id:
            messagebox.showinfo("Success", f"Item '{name}' (ID: {item_id}) added successfully.", parent=self)
            self.name_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.load_inventory()
        else:
            messagebox.showerror("Database Error", "Failed to add item to the database. Check logs for details.", parent=self)

    def edit_selected_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection Error", "No item selected to edit. Please select an item from the list.", parent=self)
            return

        try:
            # Ensure something is selected, then fetch its values
            selected_tree_item = self.items_tree.selection()[0] # This line might raise IndexError if selection is cleared rapidly
            item_values = self.items_tree.item(selected_tree_item)['values']
        except IndexError:
            messagebox.showwarning("Selection Error", "Could not retrieve selected item details. The selection might have been cleared.", parent=self)
            return

        item_id, current_name, current_qty, current_desc, _, _ = item_values

        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Item")
        edit_window.geometry("400x250") # Adjusted size
        edit_window.transient(self) # Keep window on top of main
        edit_window.grab_set() # Modal behavior

        ttk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar(value=current_name)
        edit_name_entry = ttk.Entry(edit_window, textvariable=name_var, width=40)
        edit_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(edit_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        qty_var = tk.StringVar(value=str(current_qty)) # Ensure quantity is string for Entry
        edit_qty_entry = ttk.Entry(edit_window, textvariable=qty_var, width=15)
        edit_qty_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(edit_window, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        desc_var = tk.StringVar(value=current_desc)
        edit_desc_entry = ttk.Entry(edit_window, textvariable=desc_var, width=40)
        edit_desc_entry.grid(row=2, column=1, padx=10, pady=10)

        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        save_button = ttk.Button(button_frame, text="Save Changes", 
                                 command=lambda: self.save_edited_item(edit_window, item_id, name_var, qty_var, desc_var))
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=edit_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def save_edited_item(self, edit_window, item_id, name_var, qty_var, desc_var):
        new_name = name_var.get().strip()
        new_quantity_str = qty_var.get().strip()
        new_description = desc_var.get().strip()

        if not new_name:
            messagebox.showerror("Input Validation Error", "Name cannot be empty.", parent=edit_window)
            return
        if not new_quantity_str:
            messagebox.showerror("Input Validation Error", "Quantity cannot be empty.", parent=edit_window)
            return
        try:
            new_quantity = int(new_quantity_str)
        except ValueError:
            messagebox.showerror("Input Validation Error", "Quantity must be a valid integer.", parent=edit_window)
            return
        if new_quantity < 0:
            messagebox.showerror("Input Validation Error", "Quantity cannot be negative.", parent=edit_window)
            return

        if database.update_item(item_id, new_name, new_quantity, new_description):
            messagebox.showinfo("Success", f"Item ID: {item_id} updated successfully.", parent=self)
            edit_window.destroy()
            self.load_inventory()
        else:
            messagebox.showerror("Database Error", f"Failed to update item ID: {item_id}. Check logs for details.", parent=edit_window)

    def delete_selected_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection Error", "No item selected to delete. Please select an item from the list.", parent=self)
            return
        
        # Fetch name for a more user-friendly confirmation
        item_name = ""
        try:
            selected_tree_item = self.items_tree.selection()[0]
            item_values = self.items_tree.item(selected_tree_item)['values']
            item_name = f" '{item_values[1]}'" # Name is the second value
        except IndexError:
            # If somehow item details can't be fetched, proceed with just ID
            pass

        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete item{item_name} (ID: {self.selected_item_id})?",
                                      parent=self)
        if confirm:
            if database.delete_item(self.selected_item_id):
                messagebox.showinfo("Success", f"Item{item_name} (ID: {self.selected_item_id}) deleted successfully.", parent=self)
                self.load_inventory() # This calls clear_selection_and_disable_buttons()
            else:
                messagebox.showerror("Database Error", f"Failed to delete item ID: {self.selected_item_id}. Check logs for details.", parent=self)
                self.clear_selection_and_disable_buttons() # Explicitly call if deletion fails
        else: # User clicked "No"
             self.clear_selection_and_disable_buttons()


    def search_inventory(self):
        query = self.search_entry.get().strip()
        
        # Clear previous search results from tree
        for i in self.items_tree.get_children():
            self.items_tree.delete(i)

        items = []
        if not query: # If search query is empty, load all items
            items = database.get_all_items()
            messagebox.showinfo("Search Results", f"Displaying all {len(items)} items.", parent=self)
        else:
            items = database.search_items(query)
            if items:
                messagebox.showinfo("Search Results", f"{len(items)} item(s) found matching '{query}'.", parent=self)
            else:
                messagebox.showinfo("Search Results", f"No items found matching '{query}'.", parent=self)
        
        for item in items:
            self.items_tree.insert("", tk.END, values=item)
        
        self.clear_selection_and_disable_buttons()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_inventory() # This will repopulate and also clear selection/buttons

    def load_inventory(self):
        # Clear existing items
        for i in self.items_tree.get_children():
            self.items_tree.delete(i)

        # Load new items
        items = database.get_all_items()
        for item in items:
            self.items_tree.insert("", tk.END, values=item)
        self.clear_selection_and_disable_buttons() # Important to reset selection state

if __name__ == "__main__":
    app = Application()
    app.mainloop()
