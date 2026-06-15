#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 12:39 2026

@author: rodri

Module Documentation:


TODO

"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    import os
    import sqlite3

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================
# Assign a name to the database
DB_NAME = "recetas.db"

# Connect to the database
def connect():
    return sqlite3.connect(DB_NAME)

# Create a table (recipes) with columns [id, name, ingredients, steps, tags]
SQL_CREAR_RECETAS = "CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, ingredients TEXT, steps TEXT, tags TEXT)"

def start_db():
    conn = connect()
    conn.execute(SQL_CREAR_RECETAS)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    start_db()
print("Base de datos inicializada")