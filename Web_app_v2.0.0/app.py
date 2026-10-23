#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 11:51 2026

@author: rodri

Module Documentation:
- Run with: uv run streamlit run app.py on the app folder

TODO
- Fix number of people while loading previous snapshots
- Make snapshot more robust by saving recipe_id in case recipe is rename
- More input validation in create recipes
- Some code is reused in render_home and render_create_menu, make a function for both cases
- Split render_create_menu into some functions, now is too big and unweldy
- Better session_state initialization

"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    import random
    import streamlit as st
    import db_backend as db
    import functions as functions
    from pathlib import Path
    import config as config

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================

def init_app():
    db.init_db()
    ### Page configuration
    st.set_page_config(page_title="Planificador Menus semanales",page_icon="app_icon.png",layout="wide")
    st.logo("app_icon.png", size="medium", link=None, icon_image=None)

    ### Session state definition
    if "ingredient_rows" not in st.session_state:
        st.session_state.ingredient_rows = 3
    for i in range(len(config.DAYS)):
        if f"menu_lunch_{i}" not in st.session_state:
            st.session_state[f"menu_lunch_{i}"] = ""
        if f"menu_dinner_{i}" not in st.session_state:
            st.session_state[f"menu_dinner_{i}"] = ""

    if "editing_recipe_id" not in st.session_state:
        st.session_state["editing_recipe_id"] = None
    if "edit_ingredient_rows" not in st.session_state:
        st.session_state["edit_ingredient_rows"] = {}


### Creation of sidebar
def render_sidebar():
    st.sidebar.title("Menú")
    selected_page = st.sidebar.radio("Ir a", config.PAGES)
    return selected_page

# =============================================================================
# Other helpful functions
# =============================================================================
def render_edit_recipe_form(recipe_id):
    UNITS = ["", "ud", "g", "kg", "ml", "l", "lata"]

    st.markdown("### Editar receta")

    rows = st.session_state["edit_ingredient_rows"].get(recipe_id, 1)

    control_cols = st.columns([1, 1, 4])
    with control_cols[0]:
        if st.button("Añadir fila", key=f"edit_add_row_{recipe_id}", use_container_width=True):
            st.session_state["edit_ingredient_rows"][recipe_id] = rows + 1
            st.rerun()

    with control_cols[1]:
        if st.button(
            "Quitar fila",
            key=f"edit_remove_row_{recipe_id}",
            use_container_width=True,
            disabled=rows <= 1,
        ):
            st.session_state["edit_ingredient_rows"][recipe_id] = rows - 1
            st.rerun()

    with st.form(f"edit_recipe_form_{recipe_id}"):
        st.subheader("Nombre")
        recipe_name = st.text_input(
            "Nombre",
            key=f"edit_name_{recipe_id}",
            label_visibility="collapsed",
        )

        st.subheader("Ingredientes")
        num_people = st.number_input(
            "Número de personas",
            min_value=1,
            step=1,
            key=f"edit_num_people_{recipe_id}",
        )

        header_cols = st.columns([0.8, 0.1, 0.1])
        header_cols[0].markdown("**Ingrediente**")
        header_cols[1].markdown("**Cantidad**")
        header_cols[2].markdown("**Unidad**")

        for i in range(rows):
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

            with col1:
                st.text_input(
                    "Ingrediente",
                    key=f"edit_ingredient_name_{recipe_id}_{i}",
                    label_visibility="collapsed",
                    placeholder="Tomate",
                )

            with col2:
                st.number_input(
                    "Cantidad",
                    min_value=0.0,
                    step=0.5,
                    key=f"edit_ingredient_qty_{recipe_id}_{i}",
                    label_visibility="collapsed",
                )

            with col3:
                st.selectbox(
                    "Unidad",
                    UNITS,
                    key=f"edit_ingredient_unit_{recipe_id}_{i}",
                    label_visibility="collapsed",
                )

        st.subheader("Preparación")
        steps = st.text_area(
            "Pasos",
            key=f"edit_steps_{recipe_id}",
            label_visibility="collapsed",
            height=180,
        )

        st.subheader("Clasificación")
        tags_text = st.text_input(
            "Tags",
            key=f"edit_tags_{recipe_id}",
            label_visibility="collapsed",
        )

        save_col, cancel_col = st.columns(2)
        with save_col:
            submitted = st.form_submit_button("Guardar cambios")
        with cancel_col:
            cancelled = st.form_submit_button("Cancelar")

    if cancelled:
        st.session_state["editing_recipe_id"] = None
        st.rerun()

    if submitted:
        ingredients = []

        for i in range(rows):
            raw_name = st.session_state.get(f"edit_ingredient_name_{recipe_id}_{i}", "")
            qty = st.session_state.get(f"edit_ingredient_qty_{recipe_id}_{i}", 0.0)
            unit = st.session_state.get(f"edit_ingredient_unit_{recipe_id}_{i}", "")

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

        tags = []
        for tag in tags_text.split(","):
            clean_tag = tag.strip().lower()
            if clean_tag and clean_tag not in tags:
                tags.append(clean_tag)

        try:
            db.update_recipe(
                recipe_id=recipe_id,
                name=recipe_name,
                num_people=num_people,
                ingredients=ingredients,
                steps=steps,
                tags=tags,
            )
            st.session_state["editing_recipe_id"] = None
            st.success("Receta actualizada correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"No se pudo actualizar la receta: {e}")

# =============================================================================
# Section for the different pages
# =============================================================================
# Home page
def render_home():
    """
    Home page, shows last menu saved.
    """
    st.title("Planificador familiar de recetas")

    # Loads last snapshot saved
    last_snapshot = functions.load_last_menu_snapshot()
    # Create a list of all other snapshots
    historic_snapshot_list = functions.list_menu_snapshots()

    if not last_snapshot and not historic_snapshot_list:
        st.info("Todavía no hay ningún menú semanal guardado.")
        return
    
    # Create a dictionary with the selection options
    # The last one created is the first to appear
    snapshot_options = {"Último menú guardado": config.LAST_MENU_SNAPSHOT_PATH}
    # Then we add all the others
    for path in historic_snapshot_list:
        label_timestamp = path.stem.replace("weekly_menu_", "").replace("_", " ")
        snapshot_options[f"Histórico · {label_timestamp}"] = path
    # Show the list in the selecbox
    selected_label = st.selectbox("Mostrar menú", options=list(snapshot_options.keys()))
    # Pick the option from the dictionary
    selected_path = snapshot_options[selected_label]
    # And load it
    if selected_path == config.LAST_MENU_SNAPSHOT_PATH:
        snapshot = functions.load_last_menu_snapshot()
    else:
        snapshot = functions.load_snapshot(selected_path)

    if not snapshot:
        st.info("No se ha podido cargar el snapshot seleccionado.")
        return

    st.caption(f"Menú mostrado: {snapshot['saved_at']}")

    ### UI
    header = st.columns([0.15, 0.425, 0.425])
    with header[0]:
        st.markdown("**Día**")
    with header[1]:
        st.markdown("**Comida**")
    with header[2]:
        st.markdown("**Cena**")

    # Builds the calendar from the snapshot
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
    Page to create a new recipe.
    """

    UNITS = ["", "ud", "g", "kg", "ml", "l", "lata", "bote"]

    st.title("Crear receta")

    # Control for the ingredients rows (add or remove)
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
        tags_list = st.multiselect("Tags",options= db.get_all_tags(), placeholder = "Selecciona o añade tags", label_visibility = "collapsed", accept_new_options = True)
        submitted = st.form_submit_button("Guardar receta", type="primary")

    if submitted:
        # Create ingredients list
        ingredients = []

        for i in range(st.session_state.ingredient_rows):
            raw_name = st.session_state.get(f"ingredient_name_{i}", "")
            qty = st.session_state.get(f"ingredient_qty_{i}", 0.0)
            unit = st.session_state.get(f"ingredient_unit_{i}", "")
            # This is the first attempt to sanitize and normalize the input
            clean_name = raw_name.strip().lower()
            clean_unit = unit.strip().lower() if unit else None
            clean_qty = None if qty == 0 else qty

            if clean_name:
                ingredients.append({"name": clean_name,"quantity": clean_qty,"unit": clean_unit})
        # Convert the tags string into a list. Remove duplicates and normalize names
        tags = []
        for tag in tags_list:
            clean_tag = tag.strip().lower()
            if clean_tag and clean_tag not in tags:
                tags.append(clean_tag)

        #DEBUG for now, only to show the data
        #st.success("Formulario enviado. Estos son los datos recogidos:")
        #st.write("**Nombre:**", recipe_name)
        #st.write("**Número de personas:**", num_people)
        #st.write("**Pasos:**", steps)
        #st.write("**Tags:**", tags)
        #st.write("**Ingredientes:**")
        #st.json(ingredients)
        db.add_recipe(recipe_name, num_people, ingredients, steps, tags)
        st.success("Receta guardada correctamente.")

# View list of recipies already created
def render_view_recipes():
    """
    Page to see the recipes that already exist
    """
    st.title("Ver recetas")
    search_name = st.text_input("Buscar por nombre")
    selected_tags = st.multiselect("Filtrar por tags",options = db.get_all_tags())
    search_ingredient = st.text_input("Buscar por ingrediente")
    # Call the database
    recipes = db.search_recipes_by_name(search_name)

    visible_recipes = []

    for recipe in recipes:
        recipe_tags = db.get_tags_by_recipe(recipe["id"])
        recipe_ingredients = db.get_ingredients_by_recipe(recipe["id"])

        matches_tags = all(tag in recipe_tags for tag in selected_tags) if selected_tags else True

        if search_ingredient:
            ingredient_text = search_ingredient.strip().lower()
            matches_ingredient = any(ingredient_text in ingredient["ingredient_name"].lower() for ingredient in recipe_ingredients)
        else:
            matches_ingredient = True

        if matches_tags and matches_ingredient:
            visible_recipes.append((recipe, recipe_tags, recipe_ingredients))

    if not visible_recipes:
        st.info("No se han encontrado recetas.")
        return

    for recipe, recipe_tags, recipe_ingredients in visible_recipes:
        with st.expander(f"{recipe['name']}"):
            st.write(f"Raciones base: {recipe['num_people']}")
            st.write(f"Tags: {', '.join(recipe_tags) if recipe_tags else 'Sin tags'}")

            st.write("**Ingredientes:**")
            for ingredient in recipe_ingredients:
                qty = ingredient["quantity"]
                unit = ingredient["unit"] or ""

                if qty is None:
                    st.write(f"- {ingredient['ingredient_name']}")
                else:
                    st.write(f"- {ingredient['ingredient_name']}: {qty} {unit}")

            st.write("**Pasos:**")
            st.write(recipe["steps"])

            st.space("medium")
            col_edit, col_delete,= st.columns([0.1, 0.9])

            with col_edit:
                if st.button("Editar", key=f"edit_recipe_{recipe['id']}"):
                    full_recipe = db.get_recipe_by_id(recipe["id"])
                    st.session_state["editing_recipe_id"] = recipe["id"]
                    st.session_state["edit_ingredient_rows"][recipe["id"]] = max(1, len(full_recipe["ingredients"]))

                    st.session_state[f"edit_name_{recipe['id']}"] = full_recipe["name"]
                    st.session_state[f"edit_num_people_{recipe['id']}"] = full_recipe["num_people"]
                    st.session_state[f"edit_steps_{recipe['id']}"] = full_recipe["steps"]
                    st.session_state[f"edit_tags_{recipe['id']}"] = ", ".join(full_recipe["tags"])

                    for i, ingredient in enumerate(full_recipe["ingredients"]):
                        st.session_state[f"edit_ingredient_name_{recipe['id']}_{i}"] = ingredient["name"]
                        st.session_state[f"edit_ingredient_qty_{recipe['id']}_{i}"] = ingredient["quantity"] or 0.0
                        st.session_state[f"edit_ingredient_unit_{recipe['id']}_{i}"] = ingredient["unit"] or ""

                    st.rerun()
                        
            with col_delete:
                # Add a button to delete the recipe
                if st.button("Eliminar", key=f"delete_recipe_{recipe['id']}"):
                    st.session_state["recipe_pending_delete"] = recipe["id"]

                if st.session_state.get("recipe_pending_delete") == recipe["id"]:
                    st.warning("¿Seguro que quieres borrar esta receta?")

                    col_confirm, col_cancel, null= st.columns([0.1, 0.1, 0.8])

                    with col_confirm:
                        if st.button("Sí, borrar", key=f"confirm_delete_{recipe['id']}"):
                            db.delete_recipe(recipe["id"])
                            st.session_state["recipe_pending_delete"] = None
                            st.success("Receta eliminada.")
                            st.rerun()

                    with col_cancel:
                        if st.button("Cancelar", key=f"cancel_delete_{recipe['id']}"):
                            st.session_state["recipe_pending_delete"] = None
                            st.rerun()

            if st.session_state.get("editing_recipe_id") == recipe["id"]:
                render_edit_recipe_form(recipe["id"])

# Page to create a weekly menu
def render_create_menu():
    """
    Page used to create the weekly menu.

    Different recipes can be selected to fill the slots of a week. The list of recipes and ingredients can be then exported
    """
    st.title("Crear Menú semanal")

    st.subheader("Plan semanal")

    last_snapshot = functions.load_last_menu_snapshot()
    history_paths = functions.list_menu_snapshots()

    snapshot_options = {"Último menú guardado": config.LAST_MENU_SNAPSHOT_PATH}

    for path in history_paths:
        label_timestamp = path.stem.replace("weekly_menu_", "").replace("_", " ")
        snapshot_options[f"Histórico · {label_timestamp}"] = path


    # Buttons for menu actions
    control_cols = st.columns([1, 1, 1, 4])

    with control_cols[0]:
        button_autofill = st.button("Autorrellenar", width="stretch")

    with control_cols[1]:
        button_clean = st.button("Limpiar", width="stretch")

    with control_cols[2]:
        button_load = st.button("Cargar", width="stretch")

    with control_cols[3]:
        select_menu = st.selectbox("Snapshots", options=list(snapshot_options.keys()), label_visibility="collapsed")
        selected_snapshot = snapshot_options[select_menu]

    # Check if any tag has been selected
    selected_tags = st.multiselect("Tags", db.get_all_tags(), key="weekly_menu_tags")

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
            for i in range(len(config.DAYS)):
                st.session_state[f"menu_lunch_{i}"] = random.choice(available_recipes)
                st.session_state[f"menu_dinner_{i}"] = random.choice(available_recipes)
            st.rerun()

    if button_load:
        if selected_snapshot== config.LAST_MENU_SNAPSHOT_PATH:
            snapshot = functions.load_last_menu_snapshot()
        else:
            snapshot = functions.load_snapshot(selected_snapshot)

        if snapshot:
            functions.load_snapshot_into_menu_state(snapshot)
            st.success("Snapshot cargado correctamente.")
            st.rerun()
        else:
            st.warning("No se ha podido cargar el snapshot seleccionado.")

    # Number of people selection
    st.write("Numero de comensales")
    select_col1, select_col2, _ = st.columns([1, 3, 4])
    with select_col1:
        weekly_num_people = st.number_input("Numero de comensales", min_value=1, value=4, step=1, key="weekly_num_people", label_visibility="collapsed")
    with select_col2:
        check_num_people = st.checkbox("Usar este valor para toda la semana", value=True, key="bool_num_people")


    if check_num_people:
        header = st.columns([0.1, 0.45, 0.45])
        with header[0]:
            st.markdown("**Día**")
        with header[1]:
            st.markdown("**Comida**")
        with header[2]:
            st.markdown("**Cena**")

        for i, day in enumerate(config.DAYS):
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
        
        for i, day in enumerate(config.DAYS):
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

                st.selectbox("Comida", lunch_options, key=f"menu_lunch_{i}", label_visibility="collapsed")

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

                st.selectbox("Cena", dinner_options, key=f"menu_dinner_{i}", label_visibility="collapsed")

            with col5:
                st.number_input("Personas cena", min_value=1, step=1, key=f"menu_dinner_people_{i}", label_visibility="collapsed")

            st.divider()

    if button_clean:
            # Clean all the cells
            for i in range(len(config.DAYS)):
                st.session_state[f"menu_lunch_{i}"] = ""
                st.session_state[f"menu_lunch_people_{i}"] = weekly_num_people
                st.session_state[f"menu_dinner_{i}"] = ""
                st.session_state[f"menu_dinner_people_{i}"] = weekly_num_people
            st.rerun()

    # Buttons for the last actions
    end_cols = st.columns([1,1,4])
    with end_cols[0]:
        button_create_shopping_list = st.button("Crear lista", width="stretch", type="primary")
    with end_cols[1]:
        button_save_weekly_menu = st.button("Guardar", width="stretch")

   # Functions for the buttons
    if button_create_shopping_list:
        # This is the button that creates the shopping list
        menu_entries = functions.collect_menu_entries(weekly_num_people, check_num_people)

        if not menu_entries:
            st.warning("El menú semanal está vacío.")
        else:
            shopping_list = db.build_shopping_list(menu_entries)
            # Create the text for exporting to a chat
            menu_text = functions.format_menu(menu_entries)
            shopping_text = functions.format_shopping_list(shopping_list)
            combined_text = f"{menu_text}\n\n{shopping_text}"
            # Show the text
            st.text_area("Texto para copiar", value=combined_text, height=420)
        
        # The menu snapshot is also saved when the list is created
        snapshot, history_path = functions.persist_menu_snapshot(weekly_num_people, check_num_people)

    if button_save_weekly_menu:
        # This is the button that only saves the current menu as a snapshot
        snapshot, history_path = functions.persist_menu_snapshot(weekly_num_people, check_num_people)
        st.success("Menú semanal guardado correctamente.")


def main():
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

if __name__ == "__main__":
    init_app()
    main()