import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('car_lease.db')
cursor = conn.cursor()

# New cars data to be added (make, model, base_price, lease_term, interest_rate, mileage, residual_percentage)
new_cars = [
    ('Toyota', 'Corolla', 20000, 36, 0.035, 12000, 0.55),
    ('Honda', 'Accord', 26000, 36, 0.03, 15000, 0.57),
    ('Tesla', 'Model S', 80000, 36, 0.02, 12000, 0.40),
    ('Ford', 'F-150', 35000, 36, 0.06, 15000, 0.48),
    ('Chevrolet', 'Silverado', 42000, 36, 0.08, 15000, 0.47),
    ('BMW', '3 Series', 41000, 36, 0.10, 12000, 0.42),
    ('Audi', 'A4', 39000, 36, 0.07, 12000, 0.45),
    ('Mercedes', 'C-Class', 43000, 36, 0.03, 12000, 0.54),
    ('Hyundai', 'Elantra', 19500, 36, 0.04, 12000, 0.56),
    ('Kia', 'Sorento', 30000, 36, 0.04, 12000, 0.53),
    ('Jeep', 'Wrangler', 32000, 36, 0.045, 12000, 0.51),
    ('Nissan', 'Altima', 25000, 36, 0.035, 12000, 0.56),
    ('Mazda', 'CX-5', 29000, 36, 0.04, 12000, 0.57),
    ('Subaru', 'Forester', 28000, 36, 0.04, 12000, 0.58),
    ('Volkswagen', 'Passat', 27000, 36, 0.03, 12000, 0.57),
    ('Volvo', 'XC60', 48000, 36, 0.03, 12000, 0.52),
    ('Jaguar', 'XE', 45000, 36, 0.04, 12000, 0.53),
    ('Land Rover', 'Range Rover Evoque', 53000, 36, 0.045, 12000, 0.50),
    ('Chevrolet', 'Camaro', 38000, 36, 0.045, 12000, 0.52),
    ('Ford', 'Mustang', 36000, 36, 0.045, 12000, 0.54),
    ('Toyota', 'Highlander', 35000, 36, 0.035, 12000, 0.58),
    ('Lexus', 'RX', 60000, 36, 0.06, 12000, 0.60),
    ('Lexus', 'IS', 45000, 36, 0.02, 12000, 0.54),
    ('Porsche', 'Cayenne', 70000, 36, 0.02, 12000, 0.38),
    ('Honda', 'CR-V', 28000, 36, 0.035, 15000, 0.56)
]

# Insert new car data into the cars table
cursor.executemany('''
    INSERT INTO cars (make, model, base_price, lease_term, interest_rate, mileage, residual_percentage)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', new_cars)

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("New cars added to the database successfully.")
