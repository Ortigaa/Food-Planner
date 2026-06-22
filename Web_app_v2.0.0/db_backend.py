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
DB_NAME = "recetas_mock.db"

# =============================================================================
# Connect to the database
# =============================================================================
def connect():
    """
    Connect to database
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# =============================================================================
# Create tables
# =============================================================================

# Create a table (recipes) with columns [id, name, steps, num_people]
SQL_RECIPES = """CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    steps TEXT NOT NULL,
    num_people INTEGER NOT NULL DEFAULT 1
);"""

SQL_INGREDIENTS = """CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity REAL,
    unit TEXT,
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


def add_recipe(name, num_people, ingredients, steps, tags):
    conn = connect()

    cursor = conn.execute(
        "INSERT INTO recipes (name, num_people, steps) VALUES (?, ?, ?)",
        (name.strip(), num_people, steps.strip()),
    )
    recipe_id = cursor.lastrowid

    for ingredient in ingredients:
        conn.execute(
            """
            INSERT INTO ingredients (recipe_id, ingredient_name, quantity, unit)
            VALUES (?, ?, ?, ?)
            """,
            (
                recipe_id,
                ingredient["name"],
                ingredient["quantity"],
                ingredient["unit"],
            ),
        )

    for tag in tags:
        conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        tag_row = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()
        conn.execute(
            "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)",
            (recipe_id, tag_row["id"]),
        )

    conn.commit()
    conn.close()


def get_all_recipes():
    conn = connect()
    rows = conn.execute("""SELECT id, name, num_people, steps FROM recipes ORDER BY name ASC""").fetchall()
    conn.close()
    return rows

def get_all_tags():
    conn = connect()
    rows = conn.execute("SELECT name FROM tags ORDER BY name ASC").fetchall()
    conn.close()
    return [row["name"] for row in rows]


def search_recipes_by_name(search_text: str):
    search_text = search_text.strip()

    if not search_text:
        return get_all_recipes()

    conn = connect()
    rows = conn.execute("""SELECT id, name, num_people, steps FROM recipes WHERE name LIKE ? ORDER BY name ASC""", (f"%{search_text}%",),).fetchall()
    conn.close()
    return rows

def get_tags_by_recipe(recipe_id):
    conn = connect()
    rows = conn.execute("""SELECT tags.name FROM tags JOIN recipe_tags ON tags.id = recipe_tags.tag_id WHERE recipe_tags.recipe_id = ? ORDER BY tags.name ASC""", (recipe_id,),).fetchall()
    conn.close()
    return [row["name"] for row in rows]


def get_ingredients_by_recipe(recipe_id):
    conn = connect()
    rows = conn.execute("""SELECT ingredient_name, quantity, unit FROM ingredients WHERE recipe_id = ? ORDER BY ingredient_name ASC""",(recipe_id,),).fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()   
    print("Base de datos inicializada")