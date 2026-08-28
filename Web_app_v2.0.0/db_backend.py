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

def get_recipes_by_tags(selected_tags):
    if not selected_tags:
        return get_all_recipes()# If nothing is selected just run the regular get_all_recipies

    placeholders = ",".join("?" * len(selected_tags))

    conn = connect()
    rows = conn.execute(
        f"""
        SELECT DISTINCT r.id, r.name, r.num_people, r.steps
        FROM recipes r
        JOIN recipe_tags rt ON r.id = rt.recipe_id
        JOIN tags t ON t.id = rt.tag_id
        WHERE t.name IN ({placeholders})
        ORDER BY r.name ASC
        """,
        selected_tags,
    ).fetchall()
    conn.close()
    return rows

def get_recipe_by_name(recipe_name):
    conn = connect()
    row = conn.execute(
        "SELECT id, name, num_people, steps FROM recipes WHERE name = ?",
        (recipe_name,),
    ).fetchone()
    conn.close()
    return row

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

def get_ingredients_by_recipe_name(recipe_name):
    conn = connect()
    rows = conn.execute(
        """
        SELECT i.ingredient_name, i.quantity, i.unit
        FROM ingredients i
        JOIN recipes r ON r.id = i.recipe_id
        WHERE r.name = ?
        ORDER BY i.ingredient_name ASC
        """,
        (recipe_name,),
    ).fetchall()
    conn.close()
    return rows

def build_shopping_list(menu_entries):
    shopping_map = {}

    for entry in menu_entries:
        recipe_name = entry["recipe_name"]
        target_people = entry["num_people"]

        recipe = get_recipe_by_name(recipe_name)
        if recipe is None:
            continue

        base_people = recipe["num_people"] or 1
        scale_factor = target_people / base_people

        ingredients = get_ingredients_by_recipe_name(recipe_name)

        for ingredient in ingredients:
            ingredient_name = ingredient["ingredient_name"]
            unit = ingredient["unit"] or ""
            quantity = ingredient["quantity"]

            key = (ingredient_name, unit)

            if key not in shopping_map:
                shopping_map[key] = {
                    "ingredient_name": ingredient_name,
                    "unit": unit,
                    "quantity": 0 if quantity is not None else None,
                }

            if quantity is not None:
                shopping_map[key]["quantity"] += quantity * scale_factor

    shopping_list = list(shopping_map.values())
    shopping_list.sort(key=lambda item: (item["ingredient_name"], item["unit"]))
    return shopping_list

if __name__ == "__main__":
    init_db()   
    print("Base de datos inicializada")