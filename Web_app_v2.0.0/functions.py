#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 13:18 2026

@author: rodri

Module Documentation:
- Functions for the app

TODO

"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    from datetime import datetime
    import streamlit as st
    import db_backend as db
    import app as app
    import json
    from pathlib import Path

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================

def collect_menu_entries(weekly_num_people, bool_num_people):
    """
    Save all the entries in the create menu page.
    For use later in collecting ingredients.

    Parameters
    ---------
    weekly_num_people: int
        number of people eating
    bool_num_people: boolean
        if global parameters is set or not
    
    Returns
    ---------
    menu entries: list
        a list containing dicts with all the lunches and dinners names with the number of people
    """
    menu_entries = []

    for i, day in enumerate(app.DAYS):
        lunch_recipe = st.session_state.get(f"menu_lunch_{i}", "")
        dinner_recipe = st.session_state.get(f"menu_dinner_{i}", "")

        lunch_people = (
            weekly_num_people if bool_num_people else st.session_state.get(f"menu_lunch_people_{i}", weekly_num_people)
        )
        dinner_people = (
            weekly_num_people if bool_num_people else st.session_state.get(f"menu_dinner_people_{i}", weekly_num_people)
        )

        if lunch_recipe:
            menu_entries.append({"day": day, "meal_type": "comida", "recipe_name": lunch_recipe, "num_people": lunch_people})

        if dinner_recipe:
            menu_entries.append({"day": day, "meal_type": "cena", "recipe_name": dinner_recipe, "num_people": dinner_people})

    return menu_entries



def build_menu_snapshot(weekly_num_people, bool_num_people):
    """
    Create a snapshot of the current weekly menu.

    Parameters
    ---------
    weekly_num_people: int
        number of people eating
    bool_num_people: boolean
        if global parameters is set or not

    Returns
    ---------
    dictionary
    """
    days = []

    for i, day in enumerate(app.DAYS):
        lunch_recipe = st.session_state.get(f"menu_lunch_{i}", "")
        dinner_recipe = st.session_state.get(f"menu_dinner_{i}", "")

        lunch_people = (weekly_num_people if bool_num_people
                        else st.session_state.get(f"menu_lunch_people_{i}", weekly_num_people))
        dinner_people = (weekly_num_people if bool_num_people
                        else st.session_state.get(f"menu_dinner_people_{i}", weekly_num_people))

        days.append({"day": day,"lunch": {"recipe_name": lunch_recipe, "num_people": lunch_people}, "dinner": {"recipe_name": dinner_recipe,"num_people": dinner_people,}})

    return {"saved_at": datetime.now().isoformat(timespec="seconds"),"weekly_num_people": weekly_num_people,"use_global_people": bool_num_people,"days": days}


def save_last_menu_snapshot(snapshot):
    """
    Overwrites the last weekly menu snapshot
    """
    app.LAST_MENU_SNAPSHOT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2),encoding="utf-8")


def save_menu_snapshot(snapshot):
    """
    Save a snapshot of the weekly menu as a timestamped json file
    """
    app.MENU_EXPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    export_path = app.MENU_EXPORTS_DIR / f"weekly_menu_{timestamp}.json"

    export_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2),encoding="utf-8")
    return export_path

def persist_menu_snapshot(weekly_num_people, bool_num_people):
    """
    Wrapper to call the snapshot functions.

    Parameters
    ---------
    weekly_num_people: int
        number of people eating
    bool_num_people: boolean
        if global parameters is set or not
    
    Returns
    ---------
    """
    snapshot = build_menu_snapshot(weekly_num_people, bool_num_people)
    save_last_menu_snapshot(snapshot)
    history_path = save_menu_snapshot(snapshot)
    return snapshot, history_path


def load_last_menu_snapshot():
    """
    Load the last menu snapshot. Useful to show in the welcome page.
    """
    if not app.LAST_MENU_SNAPSHOT_PATH.exists():
        return None

    return json.loads(app.LAST_MENU_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def load_snapshot(snapshot_path):
    """
    Load a snapshot from the historic list
    """
    return json.loads(Path(snapshot_path).read_text(encoding="utf-8"))

def list_menu_snapshots():
    """
    Create a list of all the saved snapshot json files

    Returns
    ---------
    list
    """
    if not app.MENU_EXPORTS_DIR.exists():
        return []

    return sorted(app.MENU_EXPORTS_DIR.glob("weekly_menu_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)

def format_quantity(value):
    "Little helper to change the format of numbers"
    if value is None:
        return ""

    value = float(value)
    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}"


def format_menu(entries):
    """
    Changes the formating of the output menu so it is easier to copy/paste into a chat
    """
    lines = ["Menú semanal", ""]

    grouped = {}
    for entry in entries:
        day = entry["day"]
        grouped.setdefault(day, {"comida": None, "cena": None})
        grouped[day][entry["meal_type"]] = entry

    for day in app.DAYS:
        lunch = grouped.get(day, {}).get("comida")
        dinner = grouped.get(day, {}).get("cena")

        lunch_text = "—"
        dinner_text = "—"

        if lunch and lunch["recipe_name"]:
            lunch_text = f"{lunch['recipe_name']} ({lunch['num_people']} pers.)"

        if dinner and dinner["recipe_name"]:
            dinner_text = f"{dinner['recipe_name']} ({dinner['num_people']} pers.)"

        lines.append(f"{day}")
        lines.append(f"- Comida: {lunch_text}")
        lines.append(f"- Cena: {dinner_text}")
        lines.append("")

    return "\n".join(lines).strip()

def format_shopping_list(shopping_list):
    """
    Changes the formatting of the output shopping list so it is easier to copy/paste into a chat
    """
    lines = ["Lista de la compra", ""]

    for item in shopping_list:
        qty = item.get("quantity")
        unit = item.get("unit") or ""
        name = item["ingredient_name"]

        if qty is None:
            lines.append(f"- {name}")
        else:
            qty_text = format_quantity(qty)
            suffix = f" {unit}" if unit else ""
            lines.append(f"- {name}: {qty_text}{suffix}")

    return "\n".join(lines)


def load_snapshot_into_menu_state(snapshot):
    """
    Loads a snapshot menu into the build menu screen.
    Useful to make small changes to a previous menu.
    """
    st.session_state["weekly_num_people"] = snapshot.get("weekly_num_people", 4)
    st.session_state["weekly_use_global_people"] = snapshot.get("use_global_people", True)

    snapshot_days = snapshot.get("days", [])

    for i, day_entry in enumerate(snapshot_days):
        lunch = day_entry.get("lunch", {})
        dinner = day_entry.get("dinner", {})

        st.session_state[f"menu_lunch_{i}"] = lunch.get("recipe_name", "") or ""
        st.session_state[f"menu_dinner_{i}"] = dinner.get("recipe_name", "") or ""

        st.session_state[f"menu_lunch_people_{i}"] = lunch.get(
            "num_people",
            st.session_state["weekly_num_people"],
        )
        st.session_state[f"menu_dinner_people_{i}"] = dinner.get(
            "num_people",
            st.session_state["weekly_num_people"],
        )
