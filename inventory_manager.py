import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import mysql.connector

class AuthenticationDialog(simpledialog.Dialog):
    def __init__(self, parent):
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        super().__init__(parent)

    def body(self, master):
        tk.Label(master, text="Username:").grid(row=0, column=0, sticky="e")
        tk.Entry(master, textvariable=self.username).grid(row=0, column=1)

        tk.Label(master, text="Password:").grid(row=1, column=0, sticky="e")
        tk.Entry(master, textvariable=self.password, show="*").grid(row=1, column=1)

    def apply(self):
        self.result = (self.username.get(), self.password.get())

class InventoryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inventory Management")

        # Load and set the logo
        self.set_logo("C:\\Users\\Administrator\\IMGS\\inventoryLogo.png")

        # Initialize data structure to store inventory
        self.inventory = {}
        self.load_inventory_from_database()

        # Authenticate user
        self.authenticate_user()

        # Create and set up the GUI
        self.create_gui()

    def set_logo(self, path):
        try:
            image = tk.PhotoImage(file=path)
            self.root.iconphoto(True, image)
        except tk.TclError as e:
            print(f"Error loading logo: {e}")

    def authenticate_user(self):
        auth_dialog = AuthenticationDialog(self.root)
        username, password = auth_dialog.result

        # Validate user credentials
        if self.validate_user(username, password):
            messagebox.showinfo("Authentication", f"Welcome, {username}!")
        else:
            messagebox.showerror("Authentication Error", "Invalid username or password.")
            self.root.destroy()

    def validate_user(self, username, password):
        # Will be changed to data from database
        return username == "admin" and password == "admin"

    def create_gui(self):
        # Create labels, entry widgets, and buttons
        label_name = tk.Label(self.root, text="Product Name:")
        label_quantity = tk.Label(self.root, text="Quantity:")

        self.entry_name = tk.Entry(self.root)
        self.entry_quantity = tk.Entry(self.root)

        add_button = tk.Button(self.root, text="Add to Inventory", command=self.add_to_inventory)
        view_button = tk.Button(self.root, text="View Inventory", command=self.view_inventory)

        update_button = tk.Button(self.root, text="Update Quantity", command=self.update_quantity)
        subtract_button = tk.Button(self.root, text="Subtract from Inventory", command=self.subtract_from_inventory)
        delete_button = tk.Button(self.root, text="Delete Product", command=self.delete_product)

        # Grid layout
        label_name.grid(row=0, column=0, padx=10, pady=5)
        label_quantity.grid(row=1, column=0, padx=10, pady=5)

        self.entry_name.grid(row=0, column=1, padx=10, pady=5)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=5)

        add_button.grid(row=2, column=0, columnspan=2, pady=10)
        view_button.grid(row=3, column=0, columnspan=2, pady=10)

        update_button.grid(row=4, column=0, pady=10)
        subtract_button.grid(row=5, column=0, pady=10)
        delete_button.grid(row=4, column=1, pady=10)

    def load_inventory_from_database(self):
        # Connect to MySQL database
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pillows143",
            database="businessdb"
        )

        cursor = self.conn.cursor()
        cursor.execute("SELECT product_name, quantity FROM inventory")
        self.inventory = dict(cursor.fetchall())
        cursor.close()

    def update_quantity(self):
        product_name = self.entry_name.get()
        quantity = self.entry_quantity.get()

        if product_name and quantity:
            if product_name in self.inventory:
                self.inventory[product_name] = int(quantity)
                self.update_database(product_name, int(quantity))
                messagebox.showinfo("Success", f"{product_name} quantity updated to {quantity}.")
            else:
                messagebox.showerror("Error", f"{product_name} not found in inventory.")
        else:
            messagebox.showerror("Error", "Please enter both product name and quantity.")

    def add_to_inventory(self):
        product_name = self.entry_name.get()
        quantity = self.entry_quantity.get()

        if product_name and quantity:
            if product_name in self.inventory:
                self.inventory[product_name] += int(quantity)
                self.update_database(product_name, self.inventory[product_name])
            else:
                self.inventory[product_name] = int(quantity)
                self.add_to_database(product_name, int(quantity))

            messagebox.showinfo("Success", f"{quantity} {product_name}(s) added to inventory.")
        else:
            messagebox.showerror("Error", "Please enter both product name and quantity.")

    def subtract_from_inventory(self):
        product_name = self.entry_name.get()
        quantity = self.entry_quantity.get()

        if product_name and quantity:
            if product_name in self.inventory:
                current_quantity = self.inventory[product_name]
                if current_quantity >= int(quantity):
                    self.inventory[product_name] -= int(quantity)
                    self.update_database(product_name, self.inventory[product_name])
                    messagebox.showinfo("Success", f"{quantity} {product_name}(s) subtracted from inventory.")
                else:
                    messagebox.showerror("Error", f"Not enough {product_name} in inventory.")
            else:
                messagebox.showerror("Error", f"{product_name} not found in inventory.")
        else:
            messagebox.showerror("Error", "Please enter both product name and quantity.")

    def delete_product(self):
        product_name = self.entry_name.get()

        if product_name:
            if product_name in self.inventory:
                del self.inventory[product_name]
                self.delete_from_database(product_name)
                messagebox.showinfo("Success", f"{product_name} deleted from inventory.")
            else:
                messagebox.showerror("Error", f"{product_name} not found in inventory.")
        else:
            messagebox.showerror("Error", "Please enter the product name.")

    def update_database(self, product_name, quantity):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE inventory SET quantity = %s WHERE product_name = %s", (quantity, product_name))
        self.conn.commit()
        cursor.close()

    def add_to_database(self, product_name, quantity):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s, %s)", (product_name, quantity))
        self.conn.commit()
        cursor.close()

    def delete_from_database(self, product_name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE product_name = %s", (product_name,))
        self.conn.commit()
        cursor.close()

    def view_inventory(self):
        if not self.inventory:
            messagebox.showinfo("Inventory", "Inventory is empty.")
        else:
            inventory_window = tk.Toplevel(self.root)
            inventory_window.title("View Inventory")

            tree = ttk.Treeview(inventory_window, columns=("Product Name", "Quantity"), show="headings")
            tree.heading("Product Name", text="Product Name")
            tree.heading("Quantity", text="Quantity")

            # Insert data into the Treeview widget
            for product, quantity in self.inventory.items():
                tree.insert("", "end", values=(product, quantity))

            tree.pack()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = InventoryApp()
    app.run()
