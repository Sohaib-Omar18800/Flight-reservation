import os
import sqlite3

DB_NAME = "flights.db"


def connect():
    conn = sqlite3.connect(DB_NAME)
    return conn


def setup_database():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            flight_number TEXT,
            departure TEXT,
            destination TEXT,
            date TEXT,
            seat_number TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_reservation(data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (name, flight_number, departure, destination, date, seat_number)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data["Full Name"],
        data["Flight Number"],
        data["Departure"],
        data["Destination"],
        data["Date"],
        data["Seat Number"]
    ))
    conn.commit()
    conn.close()


def fetch_reservations():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservations")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_reservation(res_id, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE reservations
        SET name = ?, flight_number = ?, departure = ?, destination = ?, date = ?, seat_number = ?
        WHERE id = ?
    ''', (
        data["Full Name"],
        data["Flight Number"],
        data["Departure"],
        data["Destination"],
        data["Date"],
        data["Seat Number"],
        res_id
    ))
    conn.commit()
    conn.close()


def delete_reservation(res_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
    from pprint import pprint
    pprint(fetch_reservations())
