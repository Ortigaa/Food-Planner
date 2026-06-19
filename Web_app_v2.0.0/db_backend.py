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

# =============================================================================
# Connect to the database
# =============================================================================
def connect():
    """
    Connect to database
    """
    return sqlite3.connect(DB_NAME)

# =============================================================================
# Create tables
# =============================================================================

# Create a table (recipes) with columns [id, name, steps]
SQL_RECIPES = """CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    steps TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);"""

SQL_INGREDIENTS = """CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity REAL,
    unit TEXT,
    notes TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);"""

SQL_TAGS = """CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);"""

SQL_RECIPE_TAGS = """CREATE TABLE IF NOT EXISTS recipe_tags (
    recipe_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);"""

def init_db():
    conn = connect()
    conn.execute(SQL_RECIPES)
    conn.execute(SQL_INGREDIENTS)
    conn.execute(SQL_TAGS)
    conn.execute(SQL_RECIPE_TAGS)
    conn.commit()
    conn.close()


def insert_recipe(name, ingredients, steps, tags):
    conn = connect()
    conn.execute("INSERT INTO recipes (name, ingredients, steps, tags) VALUES (?, ?, ?, ?)", (name, ingredients, steps, tags))
    conn.commit()
    conn.close()


def get_recipes():
    conn = connect()
    rows = conn.execute("SELECT * FROM recipes").fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
print("Base de datos inicializada")