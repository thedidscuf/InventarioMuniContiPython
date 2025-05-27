import tkinter as tk
from tkinter import ttk, messagebox
import database

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventario de Bodega Municipal")
        self.geometry("800x600") # Increased size for more columns

        # database.create_table() is called on import in database.py

        self.create_widgets()
        self.load_inventory()

    def create_widgets(self):
        # Frame for input
        input_frame = ttk.LabelFrame(self, text="Agregar Nuevo Artículo")
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=50)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(input_frame, width=15)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Descripción:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)

        add_button = ttk.Button(input_frame, text="Agregar Artículo", command=self.add_new_item)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Frame for displaying items
        display_frame = ttk.LabelFrame(self, text="Artículos en Inventario")
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Define Treeview columns
        columns = ("id", "name", "quantity", "description", "date_added", "last_modified")
        self.items_tree = ttk.Treeview(display_frame, columns=columns, show="headings")

        self.items_tree.heading("id", text="ID")
        self.items_tree.heading("name", text="Nombre")
        self.items_tree.heading("quantity", text="Cantidad")
        self.items_tree.heading("description", text="Descripción")
        self.items_tree.heading("date_added", text="Fecha de Alta")
        self.items_tree.heading("last_modified", text="Última Modificación")

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

        self.edit_button = ttk.Button(action_frame, text="Editar Selección", command=self.edit_selected_item, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(action_frame, text="Eliminar Selección", command=self.delete_selected_item, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(action_frame, text="Actualizar Lista", command=self.load_inventory)
        refresh_button.pack(side=tk.LEFT, padx=5)

        # --- Search Frame ---
        search_outer_frame = ttk.LabelFrame(self, text="Buscar en Inventario")
        search_outer_frame.pack(fill="x", padx=10, pady=10)
        
        search_frame = ttk.Frame(search_outer_frame) # Inner frame for better padding control
        search_frame.pack(padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar por Nombre:").pack(side=tk.LEFT, padx=(0,5)) # "Search by Name:" -> "Buscar por Nombre:"
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0,5))
        
        self.search_button = ttk.Button(search_frame, text="Buscar", command=self.search_inventory)
        self.search_button.pack(side=tk.LEFT, padx=(0,5))
        
        self.clear_search_button = ttk.Button(search_frame, text="Limpiar Búsqueda", command=self.clear_search)
        self.clear_search_button.pack(side=tk.LEFT)

        # --- Product Outflow Frame ---
        outflow_main_frame = ttk.LabelFrame(self, text="Salida de Productos")
        outflow_main_frame.pack(fill="x", padx=10, pady=10)

        # Using a sub-frame for grid layout to ensure LabelFrame padding is respected
        outflow_frame = ttk.Frame(outflow_main_frame)
        outflow_frame.pack(padx=5, pady=5, fill="x")

        # Row 0: Item selection
        ttk.Label(outflow_frame, text="Artículo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.outflow_item_map = {}
        self.outflow_item_combobox = ttk.Combobox(outflow_frame, state="readonly", width=47) # width is char count
        self.outflow_item_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.refresh_outflow_items_button = ttk.Button(outflow_frame, text="Actualizar Lista de Artículos", command=self.load_items_to_outflow_combobox)
        self.refresh_outflow_items_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Row 1: Quantity
        ttk.Label(outflow_frame, text="Cantidad a Despachar:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.outflow_quantity_entry = ttk.Entry(outflow_frame, width=15)
        self.outflow_quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Row 2: Department
        ttk.Label(outflow_frame, text="Departamento Destino:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.outflow_department_entry = ttk.Entry(outflow_frame, width=50)
        self.outflow_department_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Row 3: Notes
        ttk.Label(outflow_frame, text="Notas:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.outflow_notes_text = tk.Text(outflow_frame, width=50, height=3)
        self.outflow_notes_text.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        notes_scrollbar = ttk.Scrollbar(outflow_frame, orient=tk.VERTICAL, command=self.outflow_notes_text.yview)
        self.outflow_notes_text.configure(yscrollcommand=notes_scrollbar.set)
        notes_scrollbar.grid(row=3, column=2, padx=(0,5), pady=5, sticky="ns")

        # Row 4: Register button
        register_outflow_button = ttk.Button(outflow_frame, text="Registrar Salida", command=self.registrar_salida)
        register_outflow_button.grid(row=4, column=0, columnspan=3, pady=10)

        # Configure column weights for responsiveness in outflow_frame
        outflow_frame.columnconfigure(1, weight=1)
        
        # Initial population of combobox
        self.load_items_to_outflow_combobox()


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
            messagebox.showerror("Error de Validación de Entrada", "El nombre no puede estar vacío.", parent=self) # "Name cannot be empty."
            return
        if not quantity_str:
            messagebox.showerror("Error de Validación de Entrada", "La cantidad no puede estar vacía.", parent=self) # "Quantity cannot be empty."
            return

        try:
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Error de Validación de Entrada", "La cantidad debe ser un número entero válido.", parent=self) # "Quantity must be a valid integer."
            return
        
        if quantity < 0:
            messagebox.showerror("Error de Validación de Entrada", "La cantidad no puede ser negativa.", parent=self) # "Quantity cannot be negative."
            return

        item_id = database.add_item(name, quantity, description)
        if item_id:
            messagebox.showinfo("Éxito", f"Artículo '{name}' (ID: {item_id}) agregado exitosamente.", parent=self) # "Item '{name}' (ID: {item_id}) added successfully."
            self.name_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.load_inventory()
        else:
            messagebox.showerror("Error de Base de Datos", "Falló al agregar el artículo a la base de datos. Revise los registros para más detalles.", parent=self) # "Failed to add item to the database. Check logs for details."

    def edit_selected_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Error de Selección", "No hay ningún artículo seleccionado para editar. Por favor, seleccione un artículo de la lista.", parent=self) # "No item selected to edit. Please select an item from the list."
            return

        try:
            # Ensure something is selected, then fetch its values
            selected_tree_item = self.items_tree.selection()[0] # This line might raise IndexError if selection is cleared rapidly
            item_values = self.items_tree.item(selected_tree_item)['values']
        except IndexError:
            messagebox.showwarning("Error de Selección", "No se pudieron recuperar los detalles del artículo seleccionado. La selección podría haberse borrado.", parent=self) # "Could not retrieve selected item details. The selection might have been cleared."
            return

        item_id, current_name, current_qty, current_desc, _, _ = item_values

        edit_window = tk.Toplevel(self)
        edit_window.title("Editar Artículo") # "Edit Item"
        edit_window.geometry("400x250") # Adjusted size
        edit_window.transient(self) # Keep window on top of main
        edit_window.grab_set() # Modal behavior

        ttk.Label(edit_window, text="Nombre:").grid(row=0, column=0, padx=10, pady=10, sticky="w") # "Name:"
        name_var = tk.StringVar(value=current_name)
        edit_name_entry = ttk.Entry(edit_window, textvariable=name_var, width=40)
        edit_name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(edit_window, text="Cantidad:").grid(row=1, column=0, padx=10, pady=10, sticky="w") # "Quantity:"
        qty_var = tk.StringVar(value=str(current_qty)) 
        edit_qty_entry = ttk.Entry(edit_window, textvariable=qty_var, width=15)
        edit_qty_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(edit_window, text="Descripción:").grid(row=2, column=0, padx=10, pady=10, sticky="w") # "Description:"
        desc_var = tk.StringVar(value=current_desc)
        edit_desc_entry = ttk.Entry(edit_window, textvariable=desc_var, width=40)
        edit_desc_entry.grid(row=2, column=1, padx=10, pady=10)

        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        save_button = ttk.Button(button_frame, text="Guardar Cambios", # "Save Changes"
                                 command=lambda: self.save_edited_item(edit_window, item_id, name_var, qty_var, desc_var))
        save_button.pack(side=tk.LEFT, padx=10)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=edit_window.destroy) # "Cancel"
        cancel_button.pack(side=tk.LEFT, padx=10)

    def save_edited_item(self, edit_window, item_id, name_var, qty_var, desc_var):
        new_name = name_var.get().strip()
        new_quantity_str = qty_var.get().strip()
        new_description = desc_var.get().strip()

        if not new_name:
            messagebox.showerror("Error de Validación de Entrada", "El nombre no puede estar vacío.", parent=edit_window) # "Name cannot be empty."
            return
        if not new_quantity_str:
            messagebox.showerror("Error de Validación de Entrada", "La cantidad no puede estar vacía.", parent=edit_window) # "Quantity cannot be empty."
            return
        try:
            new_quantity = int(new_quantity_str)
        except ValueError:
            messagebox.showerror("Error de Validación de Entrada", "La cantidad debe ser un número entero válido.", parent=edit_window) # "Quantity must be a valid integer."
            return
        if new_quantity < 0:
            messagebox.showerror("Error de Validación de Entrada", "La cantidad no puede ser negativa.", parent=edit_window) # "Quantity cannot be negative."
            return

        if database.update_item(item_id, new_name, new_quantity, new_description):
            messagebox.showinfo("Éxito", f"Artículo ID: {item_id} actualizado exitosamente.", parent=self) # "Item ID: {item_id} updated successfully."
            edit_window.destroy()
            self.load_inventory()
        else:
            messagebox.showerror("Error de Base de Datos", f"Falló al actualizar el artículo ID: {item_id}. Revise los registros para más detalles.", parent=edit_window) # "Failed to update item ID: {item_id}. Check logs for details."

    def delete_selected_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Error de Selección", "No hay ningún artículo seleccionado para eliminar. Por favor, seleccione un artículo de la lista.", parent=self) # "No item selected to delete. Please select an item from the list."
            return
        
        item_name = ""
        try:
            selected_tree_item = self.items_tree.selection()[0]
            item_values = self.items_tree.item(selected_tree_item)['values']
            item_name = f" '{item_values[1]}'" 
        except IndexError:
            pass

        confirm = messagebox.askyesno("Confirmar Eliminación", # "Confirm Delete"
                                      f"¿Está seguro de que desea eliminar el artículo{item_name} (ID: {self.selected_item_id})?", # "Are you sure you want to delete item{item_name} (ID: {self.selected_item_id})?"
                                      parent=self)
        if confirm:
            if database.delete_item(self.selected_item_id):
                messagebox.showinfo("Éxito", f"Artículo{item_name} (ID: {self.selected_item_id}) eliminado exitosamente.", parent=self) # "Item{item_name} (ID: {self.selected_item_id}) deleted successfully."
                self.load_inventory() 
            else:
                messagebox.showerror("Error de Base de Datos", f"Falló al eliminar el artículo ID: {self.selected_item_id}. Revise los registros para más detalles.", parent=self) # "Failed to delete item ID: {self.selected_item_id}. Check logs for details."
                self.clear_selection_and_disable_buttons() 
        else: 
             self.clear_selection_and_disable_buttons()


    def search_inventory(self):
        query = self.search_entry.get().strip()
        
        for i in self.items_tree.get_children():
            self.items_tree.delete(i)

        items = []
        if not query: 
            items = database.get_all_items()
            messagebox.showinfo("Resultados de Búsqueda", f"Mostrando todos los {len(items)} artículos.", parent=self) # "Displaying all {len(items)} items."
        else:
            items = database.search_items(query)
            if items:
                messagebox.showinfo("Resultados de Búsqueda", f"{len(items)} artículo(s) encontrado(s) que coincide(n) con '{query}'.", parent=self) # "{len(items)} item(s) found matching '{query}'."
            else:
                messagebox.showinfo("Resultados de Búsqueda", f"No se encontraron artículos que coincidan con '{query}'.", parent=self) # "No items found matching '{query}'."
        
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

    def load_items_to_outflow_combobox(self):
        self.outflow_item_map.clear()
        items = database.get_all_items()
        display_items = []
        if items:
            for item in items:
                # item: (id, name, quantity, description, date_added, last_modified)
                item_id, item_name, item_quantity = item[0], item[1], item[2]
                display_text = f"{item_name} (ID: {item_id}, Stock: {item_quantity})"
                display_items.append(display_text)
                self.outflow_item_map[display_text] = item_id
            self.outflow_item_combobox['values'] = display_items
            self.outflow_item_combobox.current(0) # Select the first item
        else:
            self.outflow_item_combobox['values'] = []
            self.outflow_item_combobox.set('') # Clear current selection if no items

    def registrar_salida(self):
        selected_display_text = self.outflow_item_combobox.get()
        if not selected_display_text:
            messagebox.showerror("Error de Validación", "Por favor, seleccione un artículo.", parent=self)
            return

        item_id = self.outflow_item_map.get(selected_display_text)
        if item_id is None: # Should not happen if combobox is populated correctly
            messagebox.showerror("Error Interno", "Artículo seleccionado no válido. Por favor, actualice la lista de artículos.", parent=self)
            return

        quantity_str = self.outflow_quantity_entry.get().strip()
        if not quantity_str:
            messagebox.showerror("Error de Validación", "Por favor, ingrese la cantidad a despachar.", parent=self)
            return

        try:
            quantity_dispatched = int(quantity_str)
            if quantity_dispatched <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error de Validación", "La cantidad a despachar debe ser un número entero positivo.", parent=self)
            return

        department_name = self.outflow_department_entry.get().strip()
        if not department_name:
            messagebox.showerror("Error de Validación", "Por favor, ingrese el nombre del departamento.", parent=self)
            return

        notes = self.outflow_notes_text.get("1.0", tk.END).strip()

        # Crucial: Fetch current stock again right before transaction
        item_details = database.get_item_by_id(item_id)
        if not item_details:
            messagebox.showerror("Error de Base de Datos", f"No se pudo encontrar el artículo ID: {item_id} en la base de datos.", parent=self)
            self.load_items_to_outflow_combobox() # Refresh combobox as item might be gone
            return
        
        available_stock = item_details[2] # quantity is at index 2
        if quantity_dispatched > available_stock:
            messagebox.showerror("Error de Stock", f"La cantidad a despachar ({quantity_dispatched}) no puede exceder el stock disponible (Stock actual: {available_stock}).", parent=self)
            return

        # Proceed with outflow
        outflow_id = database.add_product_outflow(item_id, quantity_dispatched, department_name, notes)

        if outflow_id:
            messagebox.showinfo("Éxito", f"Salida registrada exitosamente. ID de Salida: {outflow_id}.", parent=self)
            # Clear fields
            self.outflow_item_combobox.set('') # Clear selection, or set to first if desired
            self.outflow_quantity_entry.delete(0, tk.END)
            self.outflow_department_entry.delete(0, tk.END)
            self.outflow_notes_text.delete("1.0", tk.END)
            
            # Refresh main inventory and combobox
            self.load_inventory()
            self.load_items_to_outflow_combobox()
        else:
            # The database function add_product_outflow already prints specific errors to console (e.g. "insufficient stock" if race condition happened)
            messagebox.showerror("Error de Registro", "Error al registrar la salida. Verifique el stock o contacte al administrador.", parent=self)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
