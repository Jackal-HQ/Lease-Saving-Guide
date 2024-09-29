import sqlite3

def clear_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('car_lease.db')
    cursor = conn.cursor()

    try:
        # Delete all records from the cars table
        cursor.execute("DELETE FROM cars")

        # Reset the auto-increment ID back to 1 (if needed)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='cars'")

        # Commit the changes
        conn.commit()

        print("Database cleared successfully. All car records have been deleted.")

    except sqlite3.Error as error:
        print(f"Error occurred while clearing the database: {error}")

    finally:
        # Close the connection
        if conn:
            conn.close()

# Call the function to clear the database
if __name__ == "__main__":
    clear_database()
