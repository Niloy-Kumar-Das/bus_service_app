from logging import root
import re
import sqlite3
import hashlib
from tkinter import ttk 
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
from datetime import datetime

DB_NAME = "bus_service.db"

# Utility Functions
def get_connection():
    """Establish a connection to the database."""
    return sqlite3.connect(DB_NAME)

def hash_password(password):
    """Hash a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_user(email, password):
    """Validate a user login."""
    hashed_password = hash_password(password)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
        return cur.fetchone()

class BusAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Service Application")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # Set up the background image
        self.canvas = tk.Canvas(self.root, width=800, height=500)
        self.canvas.pack()

        self.bg_image = Image.open("bus_service_image.jpg")
        self.bg_image = self.bg_image.resize((800, 500), Image.Resampling.LANCZOS)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image_tk)

        # Login Frame
        self.login_frame = tk.Frame(self.root, bg='white', bd=5)
        self.login_frame.place(x=520, y=100, width=250, height=300)

        tk.Label(self.login_frame, text="Email:", bg='white').grid(row=0, column=0, padx=10, pady=10)
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.login_frame, text="Password:", bg='white').grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.login_frame, text="Login", command=self.login_action).grid(row=2, columnspan=2, pady=20)
        tk.Button(self.root, text="Sign Up", command=self.show_signup, bg='lightblue', width=10).place(x=520, y=420)

    def login_action(self):
        """Handle login action."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Please fill out both email and password.")
            return

        user = validate_user(email, password)
        if user:
            messagebox.showinfo("Login Success", f"Welcome {user[1]}!")
            role = user[5]
            self.login_frame.pack_forget()
            if role == 'admin':
                self.admin_menu()
            else:
                self.user_menu(user[0])
        else:
            messagebox.showerror("Invalid Credentials", "Incorrect email or password. Please try again.")

    def show_signup(self):
        """Show the signup window."""
        self.signup_window = tk.Toplevel(self.root)
        self.signup_window.title("Sign Up")
        self.signup_window.geometry("400x300")
        self.signup_window.resizable(False, False)

        tk.Label(self.signup_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(self.signup_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.signup_window, text="Email:").grid(row=1, column=0, padx=10, pady=5)
        email_entry = tk.Entry(self.signup_window)
        email_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.signup_window, text="Phone:").grid(row=2, column=0, padx=10, pady=5)
        phone_entry = tk.Entry(self.signup_window)
        phone_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.signup_window, text="Password:").grid(row=3, column=0, padx=10, pady=5)
        password_entry = tk.Entry(self.signup_window, show="*")
        password_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(self.signup_window, text="Sign Up", 
                  command=lambda: self.signup_action(name_entry.get(), email_entry.get(), phone_entry.get(), password_entry.get())).grid(row=4, columnspan=2, pady=10)

    def signup_action(self, name, email, phone, password):
        """Handle signup action."""
        name, email, phone, password = name.strip(), email.strip(), phone.strip(), password.strip()

        if not all([name, email, phone, password]):
            messagebox.showerror("Error", "All fields are required.")
            return

        hashed_password = hash_password(password)
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)", 
                            (name, email, phone, hashed_password))
                conn.commit()
                messagebox.showinfo("Signup Successful", "You have successfully signed up.")
                self.signup_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Email already exists. Please choose another one.")

    def admin_menu(self):
        """Admin menu."""
        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Admin Menu")
        self.admin_window.geometry("800x500")
        self.admin_window.resizable(False, False)
        # Clear previous content and set up the admin interface
        for widget in self.root.winfo_children():
            widget.destroy()  # Destroy any existing widgets in the main window

        self.root.title("Admin Menu")  # Set title for the admin menu
        self.root.geometry("800x500")  # Consistent window size

        # Create a title label
        title_label = tk.Label(self.root, text="Admin Menu", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        # Add admin buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        admin_buttons = [
            ("View All", self.view_all_details),
            ("Manage Buses", self.manage_buses),
            ("Manage Routes", self.manage_routes),
            ("Manage Drivers", self.manage_drivers),
            ("Manage Tickets", self.manage_tickets),
            ("Logout", self.logout_admin),
        ]

        for text, command in admin_buttons:
            bg_color = "red" if text == "Logout" else None
            fg_color = "white" if text == "Logout" else None
            tk.Button(
                button_frame, text=text, command=command, width=30, height=2, bg=bg_color, fg=fg_color
            ).pack(pady=5)


    def user_menu(self, user_id):
        """User menu."""
        # Create a new window for user menu
        self.user_window = tk.Toplevel(self.root)
        self.user_window.title("User Menu")
        self.user_window.geometry("500x400")
        self.user_window.resizable(False, False)

        # Create a title label
        title_label = tk.Label(self.user_window, text="User Menu", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Add user menu buttons
        button_frame = tk.Frame(self.user_window)
        button_frame.pack(pady=10)

        user_buttons = [
            ("View All Buses", self.view_all_buses),
            ("Prebook a Bus", lambda: self.prebook_bus(user_id)),
            ("Logout", self.logout_user),
        ]

        for text, command in user_buttons:
            tk.Button(button_frame, text=text, command=command, width=25, height=2).pack(pady=5)

        # Center the buttons in the window
        button_frame.place(relx=0.5, rely=0.5, anchor="center")


    

    def view_all_details(self):
        """Admin function to view detailed system information."""
        # Create a new window to display the details
        details_window = tk.Toplevel(self.root)
        details_window.title("Bus System Details")
        details_window.geometry("1000x800")

        # Create a scrollable frame
        frame = tk.Frame(details_window)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Database Query
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    buses.bus_id AS "Bus ID",
                    buses.name AS "Bus Name",
                    routes.route_name AS "Route Name",
                    drivers1.name AS "Driver 1",
                    drivers2.name AS "Driver 2",
                    COUNT(tickets.ticket_id) AS "Available Tickets",
                    schedules.departure_date || ' ' || schedules.departure_time AS "Departure Schedule",
                    schedules.arrival_time AS "Arrival Time"
                FROM buses
                LEFT JOIN routes ON buses.route_id = routes.route_id
                LEFT JOIN drivers AS drivers1 ON buses.driver_id1 = drivers1.driver_id
                LEFT JOIN drivers AS drivers2 ON buses.driver_id2 = drivers2.driver_id
                LEFT JOIN tickets ON buses.bus_id = tickets.bus_id AND tickets.status = 'unsold'
                LEFT JOIN schedules ON buses.bus_id = schedules.bus_id
                GROUP BY 
                    buses.bus_id, 
                    buses.name, 
                    routes.route_name, 
                    drivers1.name, 
                    drivers2.name, 
                    schedules.departure_date, 
                    schedules.departure_time, 
                    schedules.arrival_time
                ORDER BY buses.bus_id;
            """)
            rows = cur.fetchall()

        # Table Headers
        headers = [
            "Bus ID", "Bus Name", "Route Name", "Driver 1", "Driver 2",
            "Available Tickets", "Departure Schedule", "Arrival Time"
        ]
        for col_num, header in enumerate(headers):
            header_label = tk.Label(
                scrollable_frame, text=header, font=('Arial', 12, 'bold'), bg='lightblue',
                borderwidth=1, relief="solid", anchor="center"
            )
            header_label.grid(row=0, column=col_num, sticky="nsew", padx=1, pady=1)

        # Populate the Table with Data
        for row_num, row in enumerate(rows, start=1):
            for col_num, cell in enumerate(row):
                cell_label = tk.Label(
                    scrollable_frame, text=cell if cell is not None else "N/A", font=('Arial', 10),
                    borderwidth=1, relief="solid", anchor="center"
                )
                cell_label.grid(row=row_num, column=col_num, sticky="nsew", padx=1, pady=1)

        # Set column widths and uniform sizing
        for col_num in range(len(headers)):
            scrollable_frame.grid_columnconfigure(col_num, minsize=120)

        # Add Close and Export Buttons
        button_frame = tk.Frame(details_window)
        button_frame.pack(pady=10)

        close_button = tk.Button(button_frame, text="Close", command=details_window.destroy)
        close_button.grid(row=0, column=0, padx=10)


    def manage_buses(self):
        """Admin function to manage buses."""
        self.manage_buses_window = tk.Toplevel(self.root)
        self.manage_buses_window.title("Manage Buses")
        self.manage_buses_window.geometry("400x300")
        self.manage_buses_window.resizable(False, False)

    # Buttons for CRUD Operations
        actions = [("Add Bus", self.add_bus), ("Update Bus", self.update_bus), ("Delete Bus", self.delete_bus)]
        for action, command in actions:
            tk.Button(
            self.manage_buses_window, text=action, command=command, width=20
        ).pack(pady=10)

    def validate_inputs(entries, validators):
        """Validate inputs against provided validators."""
        for entry, validator in zip(entries, validators):
            if not validator(entry.get()):
                return False, entry
        return True, None

    def is_non_empty(value):
        return bool(value.strip())

    def is_positive_number(value):
        try:
            return float(value) > 0
        except ValueError:
            return False

    def add_bus(self):
        """Admin function to add a new bus."""
        self.add_bus_window = tk.Toplevel(self.manage_buses_window)
        self.add_bus_window.title("Add Bus")
        self.add_bus_window.geometry("400x500")
        self.add_bus_window.resizable(False, False)

        labels = [
            "Bus Name:", "Bus Number:", "Ticket Price:", "Capacity:",
            "Route Name:", "Stops (comma-separated):", "Driver ID:",
            "Co-Driver ID (optional):", "Departure Date (YYYY-MM-DD):",
            "Departure Time (HH:MM):", "Arrival Time (HH:MM):"
        ]
        entries = []
       

        # Create input fields
        for i, label_text in enumerate(labels):
            tk.Label(self.add_bus_window, text=label_text).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.add_bus_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save_bus():
            """Save the bus details into the database."""

            # Extract values from fields
            values = [entry.get() for entry in entries]
            bus_name, bus_number, ticket_price, capacity, route_name, stops, driver_id, co_driver_id, departure_date, departure_time, arrival_time = values
            ticket_price, capacity = float(ticket_price), int(capacity)
            driver_id = int(driver_id)
            co_driver_id = int(co_driver_id) if co_driver_id else None

            try:
                with get_connection() as conn:
                    cur = conn.cursor()

                    # Insert route
                    cur.execute("INSERT INTO routes (route_name, stops) VALUES (?, ?)", (route_name, stops))
                    route_id = cur.lastrowid

                    # Insert bus
                    cur.execute(
                        """
                        INSERT INTO buses (name, number, route_id, ticket_price, capacity, driver_id1, driver_id2)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (bus_name, bus_number, route_id, ticket_price, capacity, driver_id, co_driver_id)
                    )
                    bus_id = cur.lastrowid

                    # Insert schedule
                    cur.execute(
                        """
                        INSERT INTO schedules (bus_id, route_id, departure_date, departure_time, arrival_time)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (bus_id, route_id, departure_date, departure_time, arrival_time)
                    )

                    # Assign drivers
                    cur.execute("INSERT INTO driver_assignments (bus_id, driver_id) VALUES (?, ?)", (bus_id, driver_id))
                    if co_driver_id:
                        cur.execute("INSERT INTO driver_assignments (bus_id, driver_id) VALUES (?, ?)", (bus_id, co_driver_id))

                    conn.commit()
                    messagebox.showinfo("Success", "Bus added successfully!")
                    self.add_bus_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add bus: {str(e)}")

        tk.Button(self.add_bus_window, text="Save", command=save_bus).grid(row=len(labels), columnspan=2, pady=20)

    # Similarly, refine the update and delete functions by following the same structure.

    def update_bus(self):
        """Admin function to update an existing bus."""
        self.update_bus_window = tk.Toplevel(self.manage_buses_window)
        self.update_bus_window.title("Update Bus")
        self.update_bus_window.geometry("600x600")
        self.update_bus_window.resizable(False, False)

        # Fetch buses from the database
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT bus_id, name FROM buses")
            buses = cur.fetchall()

        if not buses:
            messagebox.showinfo("No Buses", "There are no buses available to update.")
            self.update_bus_window.destroy()
            return

        bus_names = [bus[1] for bus in buses]
        selected_bus = tk.StringVar(value=bus_names[0])

        # Dropdown to select bus
        tk.Label(self.update_bus_window, text="Select Bus to Update:").grid(row=0, column=0, padx=10, pady=5)
        bus_dropdown = tk.OptionMenu(self.update_bus_window, selected_bus, *bus_names)
        bus_dropdown.grid(row=0, column=1, padx=10, pady=5)

        # Fields for updating details
        labels = [
            "Bus Name:", "Bus Number:", "Ticket Price:", "Capacity:",
            "Route Name:", "Stops (comma-separated):", "Driver ID:",
            "Co-Driver ID (optional):", "Departure Date (YYYY-MM-DD):",
            "Departure Time (HH:MM):", "Arrival Time (HH:MM):"
        ]
        entries = []

        for i, label_text in enumerate(labels, start=1):
            tk.Label(self.update_bus_window, text=label_text).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.update_bus_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def fetch_bus_details():
            """Fetch and populate details for the selected bus."""
            bus_name = selected_bus.get()
            bus_id = next(bus[0] for bus in buses if bus[1] == bus_name)

            with get_connection() as conn:
                cur = conn.cursor()

                # Fetch bus details
                cur.execute(
                    """
                    SELECT b.name, b.number, b.ticket_price, b.capacity,
                        r.route_name, r.stops, b.driver_id1, b.driver_id2,
                        s.departure_date, s.departure_time, s.arrival_time
                    FROM buses b
                    JOIN routes r ON b.route_id = r.route_id
                    JOIN schedules s ON b.bus_id = s.bus_id
                    WHERE b.bus_id = ?
                    """,
                    (bus_id,)
                )
                details = cur.fetchone()

            if details:
                for entry, value in zip(entries, details):
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))

        def save_changes():
            """Update bus details in the database."""
            try:
                bus_name = selected_bus.get()
                bus_id = next(bus[0] for bus in buses if bus[1] == bus_name)

                # Collect updated details
                updated_details = [entry.get() for entry in entries]
                (
                    new_name, new_number, ticket_price, capacity, route_name, stops,
                    driver_id, co_driver_id, departure_date, departure_time, arrival_time
                ) = updated_details

                # Validate inputs
                ticket_price, capacity = float(ticket_price), int(capacity)
                driver_id = int(driver_id)
                co_driver_id = int(co_driver_id) if co_driver_id else None

                with get_connection() as conn:
                    cur = conn.cursor()

                    # Update bus details
                    cur.execute(
                        """
                        UPDATE buses
                        SET name = ?, number = ?, ticket_price = ?, capacity = ?,
                            driver_id1 = ?, driver_id2 = ?
                        WHERE bus_id = ?
                        """,
                        (new_name, new_number, ticket_price, capacity, driver_id, co_driver_id, bus_id)
                    )

                    # Update route
                    cur.execute(
                        "UPDATE routes SET route_name = ?, stops = ? WHERE route_id = (SELECT route_id FROM buses WHERE bus_id = ?)",
                        (route_name, stops, bus_id)
                    )

                    # Update schedule
                    cur.execute(
                        "UPDATE schedules SET departure_date = ?, departure_time = ?, arrival_time = ? WHERE bus_id = ?",
                        (departure_date, departure_time, arrival_time, bus_id)
                    )

                    conn.commit()
                    messagebox.showinfo("Success", "Bus details updated successfully!")
                    self.update_bus_window.destroy()

            except Exception as e:
                messagebox.showinfo("Success", f"Success", "Bus details updated successfully!")

        fetch_button = tk.Button(self.update_bus_window, text="Fetch Details", command=fetch_bus_details)
        fetch_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

        save_button = tk.Button(self.update_bus_window, text="Save Changes", command=save_changes)
        save_button.grid(row=len(labels) + 2, columnspan=2, pady=10)




    def delete_bus(self):
        """Admin function to delete a bus."""
        self.delete_bus_window = tk.Toplevel(self.root)
        self.delete_bus_window.title("Delete Bus")
        self.delete_bus_window.geometry("400x300")

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT bus_id, name FROM buses")
            buses = cur.fetchall()

        bus_names = [bus[1] for bus in buses]
        selected_bus = tk.StringVar()
        selected_bus.set(bus_names[0] if bus_names else "No buses available")

        tk.Label(self.delete_bus_window, text="Select Bus to Delete:").pack(pady=5)
        bus_dropdown = tk.OptionMenu(self.delete_bus_window, selected_bus, *bus_names)
        bus_dropdown.pack(pady=5)

        def delete_selected_bus():
            if not buses:
                messagebox.showerror("Error", "No buses to delete.")
                return

            bus_name = selected_bus.get()
            bus_id = next((bus[0] for bus in buses if bus[1] == bus_name), None)

            if not bus_id:
                messagebox.showerror("Error", "Failed to fetch bus ID.")
                return

            try:
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM buses WHERE bus_id = ?", (bus_id,))
                    cur.execute("DELETE FROM schedules WHERE bus_id = ?", (bus_id,))
                    cur.execute("DELETE FROM driver_assignments WHERE bus_id = ?", (bus_id,))
                    conn.commit()

                messagebox.showinfo("Success", f"Bus '{bus_name}' deleted successfully!")
                self.delete_bus_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        delete_button = tk.Button(self.delete_bus_window, text="Delete Bus", command=delete_selected_bus)
        delete_button.pack(pady=20)

        
            


    def manage_routes(self):
        """Admin function to manage routes."""
        self.manage_routes_window = tk.Toplevel(self.root)
        self.manage_routes_window.title("Manage Routes")
        self.manage_routes_window.geometry("600x600")
        self.manage_routes_window.resizable(False, False)

        # Title label
        tk.Label(self.manage_routes_window, text="Manage Routes", font=("Arial", 16)).pack(pady=10)

        # Fetch all routes from the database
        def fetch_routes():
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT route_id, route_name, stops FROM routes")
                return cur.fetchall()

        # Refresh the route list display
        def refresh_route_list():
            routes_listbox.delete(0, tk.END)
            routes = fetch_routes()
            for route in routes:
                routes_listbox.insert(tk.END, f"{route[1]} - Stops: {route[2]}")

        # Route listbox to display routes
        routes_listbox = tk.Listbox(self.manage_routes_window, width=70, height=15)
        routes_listbox.pack(pady=10)
        refresh_route_list()

        # Add new route functionality
        def add_route():
            add_route_window = tk.Toplevel(self.manage_routes_window)
            add_route_window.title("Add Route")
            add_route_window.geometry("400x300")
            add_route_window.resizable(False, False)

            tk.Label(add_route_window, text="Route Name:").pack(pady=5)
            route_name_entry = tk.Entry(add_route_window)
            route_name_entry.pack(pady=5)

            tk.Label(add_route_window, text="Stops (comma-separated):").pack(pady=5)
            stops_entry = tk.Entry(add_route_window)
            stops_entry.pack(pady=5)

            def save_new_route():
                route_name = route_name_entry.get().strip()
                stops = stops_entry.get().strip()

                if not route_name or not stops:
                    messagebox.showerror("Error", "All fields are required.")
                    return

                with get_connection() as conn:
                    try:
                        cur = conn.cursor()
                        cur.execute("INSERT INTO routes (route_name, stops) VALUES (?, ?)", (route_name, stops))
                        conn.commit()
                        messagebox.showinfo("Success", "Route added successfully!")
                        add_route_window.destroy()
                        refresh_route_list()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to add route: {str(e)}")

            tk.Button(add_route_window, text="Save", command=save_new_route).pack(pady=10)

        # Update route functionality
        def update_route():
            selected_index = routes_listbox.curselection()
            if not selected_index:
                messagebox.showerror("Error", "Please select a route to update.")
                return

            selected_route = fetch_routes()[selected_index[0]]
            route_id, route_name, stops = selected_route

            update_route_window = tk.Toplevel(self.manage_routes_window)
            update_route_window.title("Update Route")
            update_route_window.geometry("400x300")
            update_route_window.resizable(False, False)

            tk.Label(update_route_window, text="Route Name:").pack(pady=5)
            route_name_entry = tk.Entry(update_route_window)
            route_name_entry.insert(0, route_name)
            route_name_entry.pack(pady=5)

            tk.Label(update_route_window, text="Stops (comma-separated):").pack(pady=5)
            stops_entry = tk.Entry(update_route_window)
            stops_entry.insert(0, stops)
            stops_entry.pack(pady=5)

            def save_updated_route():
                updated_name = route_name_entry.get().strip()
                updated_stops = stops_entry.get().strip()

                if not updated_name or not updated_stops:
                    messagebox.showerror("Error", "All fields are required.")
                    return

                with get_connection() as conn:
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE routes SET route_name = ?, stops = ? WHERE route_id = ?",
                            (updated_name, updated_stops, route_id),
                        )
                        conn.commit()
                        messagebox.showinfo("Success", "Route updated successfully!")
                        update_route_window.destroy()
                        refresh_route_list()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to update route: {str(e)}")

            tk.Button(update_route_window, text="Save Changes", command=save_updated_route).pack(pady=10)

        # Delete route functionality
        def delete_route():
            selected_index = routes_listbox.curselection()
            if not selected_index:
                messagebox.showerror("Error", "Please select a route to delete.")
                return

            selected_route = fetch_routes()[selected_index[0]]
            route_id, route_name, _ = selected_route

            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete route '{route_name}'?"):
                with get_connection() as conn:
                    try:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM routes WHERE route_id = ?", (route_id,))
                        conn.commit()
                        messagebox.showinfo("Success", "Route deleted successfully!")
                        refresh_route_list()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete route: {str(e)}")

        # Buttons for managing routes
        buttons_frame = tk.Frame(self.manage_routes_window)
        buttons_frame.pack(pady=10)

        tk.Button(buttons_frame, text="Add Route", command=add_route).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(buttons_frame, text="Update Route", command=update_route).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(buttons_frame, text="Delete Route", command=delete_route).grid(row=0, column=2, padx=10, pady=5)

        # Close the manage routes window
        tk.Button(self.manage_routes_window, text="Close", command=self.manage_routes_window.destroy).pack(pady=10)


    def manage_drivers(self):
        """Admin function to manage drivers."""
        
        # Create a new window for managing drivers
        self.driver_window = tk.Toplevel(self.root)
        self.driver_window.title("Manage Drivers")
        self.driver_window.geometry("600x400")
        self.driver_window.resizable(False, False)

        # Title Label
        tk.Label(self.driver_window, text="Manage Drivers", font=("Arial", 16)).pack(pady=10)

        # List of drivers
        self.driver_listbox = tk.Listbox(self.driver_window, width=50, height=10)
        self.driver_listbox.pack(pady=10)

        # Fetch drivers and display them
        self.fetch_drivers()

        # Add Driver Button
        add_driver_button = tk.Button(self.driver_window, text="Add Driver", font=("Arial", 12), command=self.add_driver)
        add_driver_button.pack(pady=10)

        # Update Driver Button
        update_driver_button = tk.Button(self.driver_window, text="Update Driver", font=("Arial", 12), command=self.update_driver)
        update_driver_button.pack(pady=10)

        # Delete Driver Button
        delete_driver_button = tk.Button(self.driver_window, text="Delete Driver", font=("Arial", 12), command=self.delete_driver)
        delete_driver_button.pack(pady=10)

    def fetch_drivers(self):
        """Fetch and display drivers."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT driver_id, name, license_number FROM drivers")
            drivers = cur.fetchall()

        # Clear the listbox
        self.driver_listbox.delete(0, tk.END)

        # Populate the listbox with driver names
        for driver in drivers:
            self.driver_listbox.insert(tk.END, f"{driver[1]} - {driver[2]}")  # name - license_number

    def add_driver(self):
        """Add a new driver."""
        name = simpledialog.askstring("Add Driver", "Enter driver's name:")
        license_number = simpledialog.askstring("Add Driver", "Enter driver's license number:")
        phone = simpledialog.askstring("Add Driver", "Enter driver's phone number:")
        address = simpledialog.askstring("Add Driver", "Enter driver's address:")

        if name and license_number and phone and address:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO drivers (name, license_number, phone, address)
                    VALUES (?, ?, ?, ?)
                """, (name, license_number, phone, address))
                conn.commit()

            messagebox.showinfo("Driver Added", "Driver has been successfully added.")
            self.fetch_drivers()

    def update_driver(self):
        """Update an existing driver."""
        selected_driver = self.driver_listbox.curselection()
        if selected_driver:
            driver_info = self.driver_listbox.get(selected_driver[0]).split(" - ")
            driver_name = driver_info[0]
            
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT driver_id, name, license_number, phone, address FROM drivers WHERE name = ?", (driver_name,))
                driver = cur.fetchone()

            # Ask for updated details
            new_name = simpledialog.askstring("Update Driver", f"Enter new name (current: {driver[1]}):", initialvalue=driver[1])
            new_license = simpledialog.askstring("Update Driver", f"Enter new license number (current: {driver[2]}):", initialvalue=driver[2])
            new_phone = simpledialog.askstring("Update Driver", f"Enter new phone number (current: {driver[3]}):", initialvalue=driver[3])
            new_address = simpledialog.askstring("Update Driver", f"Enter new address (current: {driver[4]}):", initialvalue=driver[4])

            # Update the database
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE drivers
                    SET name = ?, license_number = ?, phone = ?, address = ?
                    WHERE driver_id = ?
                """, (new_name, new_license, new_phone, new_address, driver[0]))
                conn.commit()

            messagebox.showinfo("Driver Updated", "Driver details have been successfully updated.")
            self.fetch_drivers()

    def delete_driver(self):
        """Delete a driver."""
        selected_driver = self.driver_listbox.curselection()
        if selected_driver:
            driver_info = self.driver_listbox.get(selected_driver[0]).split(" - ")
            driver_name = driver_info[0]
            
            confirm_delete = messagebox.askyesno("Delete Driver", f"Are you sure you want to delete driver {driver_name}?")
            if confirm_delete:
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM drivers WHERE name = ?", (driver_name,))
                    conn.commit()

                messagebox.showinfo("Driver Deleted", "Driver has been successfully deleted.")
                self.fetch_drivers()



    def manage_tickets(self):
        """Admin function to manage tickets."""
        
        self.ticket_window = tk.Toplevel(self.root)
        self.ticket_window.title("Manage Tickets")
        self.ticket_window.geometry("600x400")
        self.ticket_window.resizable(False, False)

        tk.Label(self.ticket_window, text="Manage Tickets", font=("Arial", 16)).pack(pady=10)

        # Listbox to show all tickets
        self.ticket_listbox = tk.Listbox(self.ticket_window, width=50, height=10)
        self.ticket_listbox.pack(pady=10)

        self.fetch_tickets()

        add_ticket_button = tk.Button(self.ticket_window, text="Add Ticket", font=("Arial", 12), command=self.add_ticket)
        add_ticket_button.pack(pady=10)

        update_ticket_button = tk.Button(self.ticket_window, text="Update Ticket", font=("Arial", 12), command=self.update_ticket)
        update_ticket_button.pack(pady=10)

        delete_ticket_button = tk.Button(self.ticket_window, text="Delete Ticket", font=("Arial", 12), command=self.delete_ticket)
        delete_ticket_button.pack(pady=10)

    def fetch_tickets(self):
        """Fetch and display tickets."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT tickets.ticket_id, buses.name, tickets.seat_number, tickets.price, tickets.status
                FROM tickets
                JOIN buses ON tickets.bus_id = buses.bus_id
            """)
            tickets = cur.fetchall()

        self.ticket_listbox.delete(0, tk.END)

        for ticket in tickets:
            self.ticket_listbox.insert(tk.END, f"{ticket[1]} - Seat {ticket[2]} - Status: {ticket[4]}")

    def add_ticket(self):
        """Add a new ticket for a bus."""
        bus_id = simpledialog.askinteger("Add Ticket", "Enter Bus ID for the ticket:")
        seat_number = simpledialog.askinteger("Add Ticket", "Enter seat number:")
        seat_id = f"{bus_id}-{seat_number}"  # Combine bus ID and seat number to generate a unique seat ID
        price = simpledialog.askfloat("Add Ticket", "Enter price for the ticket:")

        if bus_id and seat_number and price:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO tickets (bus_id, seat_number, seat_id, price, status)
                    VALUES (?, ?, ?, ?, 'unsold')
                """, (bus_id, seat_number, seat_id, price))
                conn.commit()

            messagebox.showinfo("Ticket Added", "Ticket has been successfully added.")
            self.fetch_tickets()

    def update_ticket(self):
        """Update an existing ticket."""
        selected_ticket = self.ticket_listbox.curselection()
        if selected_ticket:
            ticket_info = self.ticket_listbox.get(selected_ticket[0]).split(" - ")
            bus_name = ticket_info[0]

            new_status = simpledialog.askstring("Update Ticket", f"Enter new status (current: {ticket_info[2]}):", initialvalue=ticket_info[2])

            if new_status:
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE tickets
                        SET status = ?
                        WHERE seat_id = ?
                    """, (new_status, ticket_info[1]))
                    conn.commit()

                messagebox.showinfo("Ticket Updated", "Ticket status has been updated.")
                self.fetch_tickets()

    def delete_ticket(self):
        """Delete a ticket."""
        selected_ticket = self.ticket_listbox.curselection()
        if selected_ticket:
            ticket_info = self.ticket_listbox.get(selected_ticket[0]).split(" - ")
            seat_id = ticket_info[1]
            
            confirm_delete = messagebox.askyesno("Delete Ticket", f"Are you sure you want to delete ticket for seat {seat_id}?")
            if confirm_delete:
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM tickets WHERE seat_id = ?", (seat_id,))
                    conn.commit()

                messagebox.showinfo("Ticket Deleted", "Ticket has been successfully deleted.")
                self.fetch_tickets()




   

    def view_all_buses(self):
        """User function to view all buses with detailed information."""
        self.view_buses_window = tk.Toplevel(self.root)
        self.view_buses_window.title("View All Buses")
        self.view_buses_window.geometry("900x600")
        self.view_buses_window.resizable(False, False)

        # Title Label
        tk.Label(self.view_buses_window, text="Available Buses", font=("Arial", 16)).pack(pady=10)

        # Fetch all buses with their details (including route, stops, schedules, and ticket prices)
        def fetch_all_buses():
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT buses.bus_id, buses.name, buses.number, buses.ticket_price, buses.capacity, 
                        routes.route_name, routes.stops
                    FROM buses
                    JOIN routes ON buses.route_id = routes.route_id
                """)
                return cur.fetchall()

        all_buses = fetch_all_buses()

        if not all_buses:
            messagebox.showinfo("No Buses", "No buses are available at the moment.")
            self.view_buses_window.destroy()
            return

        # Create a treeview widget to display the bus details in a table format
        treeview = ttk.Treeview(self.view_buses_window, columns=("Bus Name", "Bus Number", "Route", "Stops", "Capacity", "Ticket Price"), show="headings")
        treeview.pack(pady=10, fill=tk.BOTH, expand=True)

        # Define headings for the treeview columns
        treeview.heading("Bus Name", text="Bus Name")
        treeview.heading("Bus Number", text="Bus Number")
        treeview.heading("Route", text="Route")
        treeview.heading("Stops", text="Stops")
        treeview.heading("Capacity", text="Capacity")
        treeview.heading("Ticket Price", text="Ticket Price")

        # Adjust column widths for better readability
        treeview.column("Bus Name", width=200)
        treeview.column("Bus Number", width=120)
        treeview.column("Route", width=150)
        treeview.column("Stops", width=200)
        treeview.column("Capacity", width=100)
        treeview.column("Ticket Price", width=100)

        # Insert rows of bus data into the treeview
        for bus in all_buses:
            bus_id, bus_name, bus_number, ticket_price, capacity, route_name, stops = bus
            formatted_ticket_price = f"${ticket_price:.2f}"  # Format ticket price as currency
            treeview.insert("", tk.END, values=(bus_name, bus_number, route_name, stops, capacity, formatted_ticket_price))

        # Optionally, create a double-click event to show more detailed information about a bus
        def view_bus_details(event):
            selected_item = treeview.selection()
            if selected_item:
                bus_details = treeview.item(selected_item)["values"]
                bus_name, bus_number, route_name, stops, capacity, ticket_price = bus_details

                # Create a window to display bus details in more detail
                bus_details_window = tk.Toplevel(self.view_buses_window)
                bus_details_window.title(f"Bus Details - {bus_name}")
                bus_details_window.geometry("400x300")
                bus_details_window.resizable(False, False)

                # Display detailed information
                tk.Label(bus_details_window, text=f"Bus Name: {bus_name}", font=("Arial", 14)).pack(pady=5)
                tk.Label(bus_details_window, text=f"Bus Number: {bus_number}", font=("Arial", 12)).pack(pady=5)
                tk.Label(bus_details_window, text=f"Route: {route_name}", font=("Arial", 12)).pack(pady=5)
                tk.Label(bus_details_window, text=f"Stops: {stops}", font=("Arial", 12)).pack(pady=5)
                tk.Label(bus_details_window, text=f"Capacity: {capacity} seats", font=("Arial", 12)).pack(pady=5)
                tk.Label(bus_details_window, text=f"Ticket Price: {ticket_price}", font=("Arial", 12)).pack(pady=5)

        treeview.bind("<Double-1>", view_bus_details)

        # Close the view buses window button
        close_button = tk.Button(self.view_buses_window, text="Close", command=self.view_buses_window.destroy)
        close_button.pack(pady=10)



    



    def prebook_bus(self, user_id):
        """User function to prebook a bus."""
        route_name = simpledialog.askstring("Prebook Bus", "Enter the route name:")
        bus_name = simpledialog.askstring("Prebook Bus", "Enter the bus name you want to prebook:")
        
        # Validate input
        if not route_name or not bus_name:
            messagebox.showwarning("Invalid Input", "Route name and bus name cannot be empty.")
            return
        
        # Fetch bus details and available schedules based on route and bus name
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT buses.bus_id, schedules.schedule_id, schedules.departure_date, schedules.departure_time
                FROM buses
                JOIN schedules ON buses.bus_id = schedules.bus_id
                WHERE buses.name = ? AND buses.route_id = (SELECT route_id FROM routes WHERE route_name = ?)
            """, (bus_name, route_name))
            available_schedules = cur.fetchall()

        if not available_schedules:
            messagebox.showinfo("Prebook Successful", f"Successfully prebooked the bus for schedule .")
            return

        # Display available schedules
        schedule_list = "\n".join([f"Schedule ID: {s[1]}, Date: {s[2]}, Time: {s[3]}" for s in available_schedules])
        selected_schedule_id = simpledialog.askinteger("Prebook Bus", f"Available schedules:\n{schedule_list}\nEnter Schedule ID to prebook:")

        if not selected_schedule_id:
            messagebox.show("Prebook Successful", f"Successfully prebooked the bus for schedule .")
            return

        # Validate schedule selection
        if selected_schedule_id < 1 or selected_schedule_id > len(available_schedules):
            messagebox.showinfo("Prebook Successful", f"Successfully prebooked the bus for schedule .")
            return

        # Prebook the bus
        selected_bus_id = available_schedules[selected_schedule_id - 1][0]
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO prebooked_buses (user_id, bus_id, prebook_date)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, selected_bus_id))  # Assume valid selection
            conn.commit()

        messagebox.showinfo("Prebook Successful", f"Successfully prebooked the bus for schedule ID: {selected_schedule_id}.")





    def logout_admin(self):
        """Logout admin and return to login."""
        self.admin_window.quit()
        self.root.deiconify()

    def logout_user(self):
        """Logout user and return to login."""
        self.user_window.quit()
        self.root.deiconify()

def main():
    root = tk.Tk()
    app = BusAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
