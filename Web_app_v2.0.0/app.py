#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 11:51 2026

@author: rodri

Module Documentation:
- Run with: uv run streamlit run app.py on the app folder

TODO

"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    import random
    from datetime import datetime
    import streamlit as st
    import db_backend as db
    import json
    from pathlib import Path

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================

db.init_db()

### Page configuration
st.logo("app_icon.png", size="medium", link=None, icon_image=None)

st.set_page_config(
    page_title="Planificador Menus semanales",
    page_icon="app_icon.png",
    layout="wide",
)

### List of pages for the sidebar
# At some point maybe is better to change it to actual pages (different scripts for each page)
PAGES = [
    "Inicio",
    "Crear receta",
    "Ver recetas",
    "Crear Menú semanal"
]

# Global variables for use across pages

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

TAGS = db.get_all_tags()

LAST_MENU_SNAPSHOT_PATH = Path("last_weekly_menu.json")

MENU_EXPORTS_DIR = Path("menu_exports")

### Session state definition
if "ingredient_rows" not in st.session_state:
    st.session_state.ingredient_rows = 3
for i in range(len(DAYS)):
    if f"menu_lunch_{i}" not in st.session_state:
        st.session_state[f"menu_lunch_{i}"] = ""
    if f"menu_dinner_{i}" not in st.session_state:
        st.session_state[f"menu_dinner_{i}"] = ""

### Creation of sidebar
def render_sidebar():
    st.sidebar.title("Menú")
    selected_page = st.sidebar.radio("Ir a", PAGES)
    return selected_page

# =============================================================================
# Other helpful functions
# =============================================================================
def collect_menu_entries(weekly_num_people, check_num_people):
    menu_entries = []

    for i, day in enumerate(DAYS):
        lunch_recipe = st.session_state.get(f"menu_lunch_{i}", "")
        dinner_recipe = st.session_state.get(f"menu_dinner_{i}", "")

        lunch_people = (
            weekly_num_people if check_num_people else st.session_state.get(f"menu_lunch_people_{i}", weekly_num_people)
        )
        dinner_people = (
            weekly_num_people if check_num_people else st.session_state.get(f"menu_dinner_people_{i}", weekly_num_people)
        )

        if lunch_recipe:
            menu_entries.append(
                {
                    "day": day,
                    "meal_type": "comida",
                    "recipe_name": lunch_recipe,
                    "num_people": lunch_people,
                }
            )

        if dinner_recipe:
            menu_entries.append(
                {
                    "day": day,
                    "meal_type": "cena",
                    "recipe_name": dinner_recipe,
                    "num_people": dinner_people,
                }
            )

    return menu_entries


def build_weekly_menu_snapshot(weekly_num_people, check_num_people):
    days = []

    for i, day in enumerate(DAYS):
        lunch_recipe = st.session_state.get(f"menu_lunch_{i}", "")
        dinner_recipe = st.session_state.get(f"menu_dinner_{i}", "")

        lunch_people = (
            weekly_num_people
            if check_num_people
            else st.session_state.get(f"menu_lunch_people_{i}", weekly_num_people)
        )
        dinner_people = (
            weekly_num_people
            if check_num_people
            else st.session_state.get(f"menu_dinner_people_{i}", weekly_num_people)
        )

        days.append(
            {
                "day": day,
                "lunch": {
                    "recipe_name": lunch_recipe,
                    "num_people": lunch_people,
                },
                "dinner": {
                    "recipe_name": dinner_recipe,
                    "num_people": dinner_people,
                },
            }
        )

    return {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "weekly_num_people": weekly_num_people,
        "use_global_people": check_num_people,
        "days": days,
    }

def save_last_weekly_menu_snapshot(snapshot):
    LAST_MENU_SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def save_weekly_menu_history(snapshot):
    MENU_EXPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    export_path = MENU_EXPORTS_DIR / f"weekly_menu_{timestamp}.json"

    export_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return export_path

def persist_weekly_menu_snapshot(weekly_num_people, check_num_people):
    snapshot = build_weekly_menu_snapshot(weekly_num_people, check_num_people)
    save_last_weekly_menu_snapshot(snapshot)
    history_path = save_weekly_menu_history(snapshot)
    return snapshot, history_path

def load_last_weekly_menu_snapshot():
    if not LAST_MENU_SNAPSHOT_PATH.exists():
        return None

    return json.loads(LAST_MENU_SNAPSHOT_PATH.read_text(encoding="utf-8"))

def list_weekly_menu_snapshots():
    if not MENU_EXPORTS_DIR.exists():
        return []

    return sorted(
        MENU_EXPORTS_DIR.glob("weekly_menu_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
# =============================================================================
# Section for the different pages
# =============================================================================
# Home page
def render_home():
    st.title("Planificador familiar de recetas")

    snapshot = load_last_weekly_menu_snapshot()

    if not snapshot:
        st.info("Todavía no hay ningún menú semanal guardado.")
        return

    st.caption(f"Último menú guardado: {snapshot['saved_at']}")

    header = st.columns([0.15, 0.425, 0.425])
    with header[0]:
        st.markdown("**Día**")
    with header[1]:
        st.markdown("**Comida**")
    with header[2]:
        st.markdown("**Cena**")

    for day_entry in snapshot["days"]:
        col1, col2, col3 = st.columns([0.15, 0.425, 0.425])

        lunch = day_entry["lunch"]
        dinner = day_entry["dinner"]

        lunch_text = "—"
        dinner_text = "—"

        if lunch["recipe_name"]:
            lunch_text = f"{lunch['recipe_name']} ({lunch['num_people']} pers.)"
        if dinner["recipe_name"]:
            dinner_text = f"{dinner['recipe_name']} ({dinner['num_people']} pers.)"

        with col1:
            st.write(day_entry["day"])
        with col2:
            st.write(lunch_text)
        with col3:
            st.write(dinner_text)

        st.divider()

# Recipe creation page
def render_create_recipe():
    """
    
    """

    UNITS = ["", "ud", "g", "kg", "ml", "l", "lata", "bote"]

    st.title("Crear receta")

    # Control for the ingridients rows (add or remove)
    ing_rows_control = st.columns([1, 1, 1, 3])
    with ing_rows_control[0]:
        st.write("**Ingredientes**")
    with ing_rows_control[1]:
        if st.button("Añadir fila", width="stretch"):
            st.session_state.ingredient_rows += 1
            st.rerun()

    with ing_rows_control[2]:
        if st.button("Quitar fila", width="stretch", disabled=st.session_state.ingredient_rows <= 1,):
            st.session_state.ingredient_rows -= 1
            st.rerun()

    # Start of form widget
    with st.form("create_recipe_form"):
        st.subheader("Nombre")
        recipe_name = st.text_input("nombre de la receta", placeholder = "Nombre de la receta", label_visibility = "collapsed")
        
        # Add number of people so values of ingredients can be normalized
        num_people = st.number_input("Numero de personas", min_value=1, step=1, value=4, width = 150)

        st.subheader("Ingredientes")
        header_cols = st.columns([0.8, 0.1, 0.1])
        header_cols[0].markdown("**Ingrediente**")
        header_cols[1].markdown("**Cantidad**")
        header_cols[2].markdown("**Unidad**")

        for i in range(st.session_state.ingredient_rows):
            ing_col = st.columns([0.8, 0.1, 0.1])

            with ing_col[0]:
                st.text_input("Ingrediente",key=f"ingredient_name_{i}",label_visibility="collapsed",placeholder="Ingrediente")
            with ing_col[1]:
                st.number_input("Cantidad",min_value=0.0,step=0.5,key=f"ingredient_qty_{i}",label_visibility="collapsed")
            with ing_col[2]:
                st.selectbox("Unidad",UNITS,key=f"ingredient_unit_{i}",label_visibility="collapsed")
            

        st.subheader("Preparación")
        steps = st.text_area("Pasos", placeholder = "Pasos", label_visibility = "collapsed", height=180)

        st.subheader("Clasificación")
        tags_list = st.multiselect("Tags",options= TAGS, placeholder = "Selecciona o añade tags", label_visibility = "collapsed", accept_new_options = True)
        submitted = st.form_submit_button("Guardar receta", type="primary")

    if submitted:
        # Create ingredients list
        ingredients = []

        for i in range(st.session_state.ingredient_rows):
            raw_name = st.session_state.get(f"ingredient_name_{i}", "")
            qty = st.session_state.get(f"ingredient_qty_{i}", 0.0)
            unit = st.session_state.get(f"ingredient_unit_{i}", "")

            clean_name = raw_name.strip().lower()
            clean_unit = unit.strip().lower() if unit else None
            clean_qty = None if qty == 0 else qty

            if clean_name:
                ingredients.append(
                    {
                        "name": clean_name,
                        "quantity": clean_qty,
                        "unit": clean_unit,
                    }
                )
        # Convert the tags string into a list. Remove duplicates and normalize names
        tags = []
        for tag in tags_list:
            clean_tag = tag.strip().lower()
            if clean_tag and clean_tag not in tags:
                tags.append(clean_tag)

        #DEBUG for now, only to show the data
        st.success("Formulario enviado. Estos son los datos recogidos:")
        st.write("**Nombre:**", recipe_name)
        st.write("**Número de personas:**", num_people)
        st.write("**Pasos:**", steps)
        st.write("**Tags:**", tags)
        st.write("**Ingredientes:**")
        st.json(ingredients)
        db.add_recipe(recipe_name, num_people, ingredients, steps, tags)
        st.success("Receta guardada correctamente.")

# View list of recipies already created
def render_view_recipes():
    st.title("Ver recetas")
    search_name = st.text_input("Buscar por nombre")
    selected_tags = st.multiselect("Filtrar por tags",options=TAGS)
    search_ingredient = st.text_input("Buscar por ingrediente")

    recipes = db.search_recipes_by_name(search_name)

    visible_recipes = []

    for recipe in recipes:
        recipe_tags = db.get_tags_by_recipe(recipe["id"])
        recipe_ingredients = db.get_ingredients_by_recipe(recipe["id"])

        matches_tags = all(tag in recipe_tags for tag in selected_tags) if selected_tags else True

        if search_ingredient:
            ingredient_text = search_ingredient.strip().lower()
            matches_ingredient = any(
                ingredient_text in ingredient["ingredient_name"].lower()
                for ingredient in recipe_ingredients
            )
        else:
            matches_ingredient = True

        if matches_tags and matches_ingredient:
            visible_recipes.append((recipe, recipe_tags, recipe_ingredients))

    if not visible_recipes:
        st.info("No se han encontrado recetas.")
        return

    for recipe, recipe_tags, recipe_ingredients in visible_recipes:
        element = st.expander(f"{recipe['name']}")
        element.write(f"Raciones base: {recipe['num_people']}")
        element.write(f"Tags: {', '.join(recipe_tags) if recipe_tags else 'Sin tags'}")

        element.write("**Ingredientes:**")
        for ingredient in recipe_ingredients:
            qty = ingredient["quantity"]
            unit = ingredient["unit"] or ""

            if qty is None:
                element.write(f"- {ingredient['ingredient_name']}")
            else:
                element.write(f"- {ingredient['ingredient_name']}: {qty} {unit}")

        element.write("**Pasos:**")
        element.write(recipe["steps"])
        element.divider()

# Page to create a weekly menu
def render_create_menu():
    st.title("Crear Menú semanal")

    st.subheader("Plan semanal")

    # Buttons for menu actions
    control_cols = st.columns([1, 1, 4])

    with control_cols[0]:
        button_autofill = st.button("Autorrellenar", width="stretch")

    with control_cols[1]:
        button_clean = st.button("Limpiar", width="stretch")

    # Check if any tag has been selected
    selected_tags = st.multiselect("Tags", TAGS, key="weekly_menu_tags")

    # Get recipies from the database, filtered by tags if selected, and convert into a list
    # Maybe this two lines can be packaged in a function to use it across pages
    recipes = db.get_recipes_by_tags(selected_tags)
    recipe_options = [""] + [recipe["name"] for recipe in recipes]

    # Functionality for the buttons
    if button_autofill:
        # Some fallback in case there is no recipes with selected tags
        available_recipes = recipe_options[1:]
        if not available_recipes:
            st.warning("No hay recetas disponibles con los tags seleccionados.")
        else:
            for i in range(len(DAYS)):
                st.session_state[f"menu_lunch_{i}"] = random.choice(available_recipes)
                st.session_state[f"menu_dinner_{i}"] = random.choice(available_recipes)
            st.rerun()

    if button_clean:
        # Clean all the cells
        for i in range(len(DAYS)):
            st.session_state[f"menu_lunch_{i}"] = ""
            st.session_state[f"menu_lunch_people_{i}"] = weekly_num_people
            st.session_state[f"menu_dinner_{i}"] = ""
            st.session_state[f"menu_dinner_people_{i}"] = weekly_num_people
        st.rerun()

    # Number of people selection
    st.write("Numero de comensales")
    select_col1, select_col2, _ = st.columns([1, 3, 4])
    with select_col1:
        weekly_num_people = st.number_input("Numero de comensales", min_value=1, value=4, step=1, key="weekly_num_people", label_visibility="collapsed")
    with select_col2:
        check_num_people = st.checkbox("Usar este valor para toda la semana", value=True, key="check_num_people")


    if check_num_people:
        header = st.columns([0.1, 0.45, 0.45])
        with header[0]:
            st.markdown("**Día**")
        with header[1]:
            st.markdown("**Comida**")
        with header[2]:
            st.markdown("**Cena**")

        for i, day in enumerate(DAYS):
            col1, col2, col3 = st.columns([0.1, 0.45, 0.45])

            with col1:
                st.write(day)

            with col2:
                # First we check the current value of the cell
                # if the cell has a value, and the tag selection is changed it might be deleted
                # to avid this, the value is added to an internal list for this cell
                current_lunch = st.session_state.get(f"menu_lunch_{i}", "")
                lunch_options = recipe_options.copy()
                if current_lunch and current_lunch not in lunch_options:
                    lunch_options = [current_lunch] + lunch_options

                st.selectbox("Comida", lunch_options, key=f"menu_lunch_{i}", label_visibility="collapsed")

            with col3:
                # Same problem and solution as above
                current_dinner = st.session_state.get(f"menu_dinner_{i}", "")
                dinner_options = recipe_options.copy()
                if current_dinner and current_dinner not in dinner_options:
                    dinner_options = [current_dinner] + dinner_options
                st.selectbox("Cena", dinner_options, key=f"menu_dinner_{i}", label_visibility="collapsed")

            st.divider()
    else:
        header = st.columns([0.1, 0.4, 0.05, 0.4, 0.05])
        with header[0]:
            st.markdown("**Día**")
        with header[1]:
            st.markdown("**Comida**")
        with header[2]:
            st.markdown("**#**")
        with header[3]:
            st.markdown("**Cena**")
        with header[4]:
            st.markdown("**#**")
        
        for i, day in enumerate(DAYS):
            # Assign some values to session state for each slot in case the global check_num_people is not selected 
            if f"menu_lunch_people_{i}" not in st.session_state:
                st.session_state[f"menu_lunch_people_{i}"] = weekly_num_people
            if f"menu_dinner_people_{i}" not in st.session_state:
                st.session_state[f"menu_dinner_people_{i}"] = weekly_num_people

            col1, col2, col3, col4, col5 = st.columns([0.1, 0.4, 0.05, 0.4, 0.05])

            with col1:
                st.write(day)

            with col2:
                current_lunch = st.session_state.get(f"menu_lunch_{i}", "")
                lunch_options = recipe_options.copy()
                if current_lunch and current_lunch not in lunch_options:
                    lunch_options = [current_lunch] + lunch_options

                st.selectbox(
                    "Comida",
                    lunch_options,
                    key=f"menu_lunch_{i}",
                    label_visibility="collapsed",
                )

            with col3:
                st.number_input(
                    "Personas comida",
                    min_value=1,
                    step=1,
                    key=f"menu_lunch_people_{i}",
                    label_visibility="collapsed",
                )

            with col4:
                current_dinner = st.session_state.get(f"menu_dinner_{i}", "")
                dinner_options = recipe_options.copy()
                if current_dinner and current_dinner not in dinner_options:
                    dinner_options = [current_dinner] + dinner_options

                st.selectbox(
                    "Cena",
                    dinner_options,
                    key=f"menu_dinner_{i}",
                    label_visibility="collapsed",
                )

            with col5:
                st.number_input(
                    "Personas cena",
                    min_value=1,
                    step=1,
                    key=f"menu_dinner_people_{i}",
                    label_visibility="collapsed",
                )

            st.divider()

    # Buttons for the last actions
    end_cols = st.columns([1,1,4])
    with end_cols[0]:
        button_create_shopping_list = st.button("Crear lista", width="stretch", type="primary")
    with end_cols[1]:
        button_save_weekly_menu = st.button("Guardar", width="stretch")

   # Functions for the buttons
    if button_create_shopping_list:
        menu_entries = collect_menu_entries(weekly_num_people, check_num_people)

        if not menu_entries:
            st.warning("El menú semanal está vacío.")
        else:
            shopping_list = db.build_shopping_list(menu_entries)

            st.subheader("Lista de la compra")
            for item in shopping_list:
                qty = item["quantity"]
                unit = item["unit"]

                if qty is None:
                    st.write(f"- {item['ingredient_name']}")
                else:
                    st.write(f"- {item['ingredient_name']}: {qty:.2f} {unit}")

        snapshot, history_path = persist_weekly_menu_snapshot(
            weekly_num_people,
            check_num_people,
        )

    if button_save_weekly_menu:
        snapshot, history_path = persist_weekly_menu_snapshot(
            weekly_num_people,
            check_num_people,
        )
        st.success("Menú semanal guardado correctamente.")


# Sidebar with the different pages
selected_page = render_sidebar()

if selected_page == "Inicio":
    render_home()
elif selected_page == "Crear receta":
    render_create_recipe()
elif selected_page == "Ver recetas":
    render_view_recipes()
elif selected_page == "Crear Menú semanal":
    render_create_menu()