import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect("database.db")

# Open and execute the schema SQL script to set up the database schema
with open("schema.sql") as f:
    connection.executescript(f.read())

# Create a cursor object to interact with the database
cur = connection.cursor()

# Commit the changes to the database
connection.commit()

# Close the database connection
connection.close()