import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import difflib
import database  # Import the database module

# Real cities list (simplified)
REAL_CITIES = ["Cairo", "London", "New York", "Tokyo",
               "Paris", "Berlin", "Dubai", "Rome", "Beijing", "Toronto"]


class FlightReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Reservation System")
        self.root.geometry("1000x700")

        database.setup_database()  # Ensure DB setup

        self.frames = {}
        self.create_frames()
        self.show_frame("Main")

    def create_frames(self):
        for frame_name in ("Main", "Booking", "Update"):
            frame = tk.Frame(self.root)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.create_main_frame()
        self.create_booking_frame()
        self.create_update_frame()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if name == "Update":
            self.populate_update_table()

    def create_main_frame(self):
        frame = self.frames["Main"]
        welcome = tk.Label(frame, text="Welcome to Flight Reservation System", font=(
            "Arial", 24, "bold"), fg="dark blue")
        welcome.pack(pady=20)

        btn_frame = tk.Frame(frame)
        btn_frame.pack()
        tk.Button(btn_frame, text="Book a Flight", command=lambda: self.show_frame(
            "Booking"), width=20).pack(side=tk.LEFT, padx=10)
        self.update_btn = tk.Button(
            btn_frame, text="Update Flights", command=lambda: self.show_frame("Update"), width=20)
        self.update_btn.pack(side=tk.LEFT, padx=10)

    def create_booking_frame(self):
        frame = self.frames["Booking"]
        tk.Label(frame, text="Book a Flight", font=("Arial", 20)).grid(
            row=0, column=0, columnspan=2, pady=20)

        labels = ["Full Name", "Flight Number", "Departure",
                  "Destination", "Date", "Seat Number"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(
                row=i+1, column=0, sticky="e", padx=10, pady=5)
            if label == "Date":
                date_var = tk.StringVar()
                self.entries[label] = date_var
                date_entry = tk.Entry(frame, textvariable=date_var)
                date_entry.grid(row=i+1, column=1, padx=10, pady=5)
                tk.Button(frame, text="Calendar", command=lambda: self.open_calendar(
                    date_var)).grid(row=i+1, column=2)
            else:
                entry = tk.Entry(frame)
                entry.grid(row=i+1, column=1, padx=10, pady=5)
                self.entries[label] = entry

        button_frame = tk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        tk.Button(button_frame, text="Back", command=lambda: self.show_frame(
            "Main"), width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Submit", command=self.save_booking,
                  width=10).pack(side=tk.LEFT, padx=10)

    def open_calendar(self, var):
        popup = tk.Toplevel(self.root)
        popup.title("Select Date")
        popup.geometry("300x300")

        cal = Calendar(popup, selectmode='day', year=2025, month=5, day=16)
        cal.pack(pady=10, fill="both", expand=True)

        def pick_date():
            var.set(cal.get_date())
            popup.destroy()

        tk.Button(popup, text="Select", bg="lightblue", font=("Arial", 10, "bold"),
                  command=pick_date).pack(pady=10, fill="x")

        popup.transient(self.root)
        popup.grab_set()
        popup.focus_force()

    def create_update_frame(self):
        frame = self.frames["Update"]
        tk.Label(frame, text="Update Flights",
                 font=("Arial", 20)).pack(pady=20)
        self.table_frame = tk.Frame(frame)
        self.table_frame.pack()
        tk.Button(frame, text="Back",
                  command=lambda: self.show_frame("Main")).pack(pady=10)

    def save_booking(self):
        data = {}
        for key, widget in self.entries.items():
            data[key] = widget.get() if isinstance(
                widget, tk.Entry) else widget.get()

        if any(not v.strip() for v in data.values()):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        if not data["Full Name"].replace(" ", "").isalpha():
            messagebox.showerror(
                "Invalid Name", "Name must contain only letters.")
            return

        for field in ["Departure", "Destination"]:
            city_input = data[field].strip().title()
            if city_input not in REAL_CITIES:
                closest = difflib.get_close_matches(
                    city_input, REAL_CITIES, n=1)
                suggestion = closest[0] if closest else "No suggestions"
                messagebox.showerror(
                    "Invalid City", f"{field} '{data[field]}' not found. Did you mean '{suggestion}'?")
                return
            data[field] = city_input

        database.save_reservation(data)
        messagebox.showinfo("Success", "Flight booked successfully!")
        self.show_frame("Main")

    def populate_update_table(self):
        from database import fetch_reservations  # Import here to avoid circular issues
        self.bookings = []  # Reset and refill with DB data

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Full Name", "Flight Number", "Departure",
                   "Destination", "Date", "Seat Number", "Actions"]
        for i, header in enumerate(headers):
            tk.Label(self.table_frame, text=header, font=(
                "Arial", 10, "bold")).grid(row=0, column=i, padx=5, pady=5)

        reservations = fetch_reservations()
        for r, row in enumerate(reservations, start=1):
            booking_id, name, flight_number, departure, destination, date, seat_number = row
            booking = {
                "id": booking_id,
                "Full Name": name,
                "Flight Number": flight_number,
                "Departure": departure,
                "Destination": destination,
                "Date": date,
                "Seat Number": seat_number
            }
            self.bookings.append(booking)

            for c, key in enumerate(["Full Name", "Flight Number", "Departure", "Destination", "Date", "Seat Number"]):
                tk.Label(self.table_frame, text=booking[key]).grid(
                    row=r, column=c, padx=5, pady=5)

            tk.Button(self.table_frame, text="Edit", command=lambda i=r -
                      1: self.edit_booking(i)).grid(row=r, column=6, padx=2)
            tk.Button(self.table_frame, text="Delete", command=lambda i=r -
                      1: self.delete_booking(i)).grid(row=r, column=7, padx=2)

        # Display in table
        for c, key in ["Full Name", "Flight Number", "Departure", "Destination", "Date", "Seat Number"]:
            tk.Label(self.table_frame, text=booking[key]).grid(
                row=r, column=c, padx=5, pady=5)

        tk.Button(self.table_frame, text="Edit", command=lambda i=r -
                  1: self.edit_booking(i)).grid(row=r, column=6, padx=2)
        tk.Button(self.table_frame, text="Delete", command=lambda i=r -
                  1: self.delete_booking(i)).grid(row=r, column=7, padx=2)

    def edit_booking(self, index):
        booking = self.bookings[index]

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Flight Info")
        edit_window.geometry("400x400")

        entries = {}
        for idx, field in enumerate(["Full Name", "Flight Number", "Departure", "Destination", "Date", "Seat Number"]):
            tk.Label(edit_window, text=field).grid(
                row=idx, column=0, padx=10, pady=5)
            var = tk.StringVar(value=booking[field])
            entry = tk.Entry(edit_window, textvariable=var)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = var

    # Save Button
        tk.Button(
            edit_window, text="Save", bg="lightgreen", font=("Arial", 10, "bold"),
            command=lambda: self.save_changes(
                booking["id"], entries, edit_window)
        ).grid(row=6, column=1, pady=15)

    def save_changes(self, booking_id, entries, window):
        updated = {key: var.get() for key, var in entries.items()}
        from database import update_reservation
        update_reservation(booking_id, updated)
        window.destroy()
        self.populate_update_table()

    def delete_booking(self, index):
        # Import here to avoid circular import issues
        from database import delete_reservation
        booking = self.bookings[index]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this booking?"):
            booking_id = booking.get("id")
            if booking_id is not None:
                delete_reservation(booking_id)
            self.bookings.pop(index)
            self.populate_update_table()
            if not self.bookings:
                self.update_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = FlightReservationApp(root)
    root.mainloop()
