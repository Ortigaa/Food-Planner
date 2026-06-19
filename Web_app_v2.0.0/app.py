#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 11:51 2026

@author: rodri

Module Documentation:


TODO

"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    import os
    import random
    from datetime import datetime
    import streamlit as st
    import sqlite3
    import db_backend as db

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================
### Page configuration
st.logo("app_icon.png", size="medium", link=None, icon_image=None)

st.set_page_config(
    page_title="Planificador Menus semanales",
    page_icon="🍽️",
    layout="wide",
)
### List of pages for the sidebar
# At some point maybe is better to change it to actual pages (different scripts for each page)
PAGES = [
    "Inicio",
    "Crear receta",
    "Ver recetas",
]

### Session state definition
if "ingredient_rows" not in st.session_state:
    st.session_state.ingredient_rows = 3


### Creation of sidebar
def render_sidebar():
    st.sidebar.title("Menú")
    selected_page = st.sidebar.radio("Ir a", PAGES)
    return selected_page

# =============================================================================
# Section for the different pages
# =============================================================================
# Home page
def render_home():
    """
    TODO
    - Add persistance, so the last weekly menu is displayed at the home page
    """
    st.title("Planificador familiar de recetas")

    DAYS = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo",]

    st.subheader("Semana actual")

    header1, header2, header3 = st.columns([1, 2, 2])
    with header1:
        st.markdown("**Día**")
    with header2:
        st.markdown("**Comida**")
    with header3:
        st.markdown("**Cena**")

    for day in DAYS:
        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:
            st.write(day)
        with col2:
            st.write("—")
        with col3:
            st.write("—")

        st.divider()

# Recipe creation page
def render_create_recipe():

    UNITS = ["", "ud", "g", "kg", "ml", "l", "lata"]

    st.title("Crear receta")

    # Control for the ingridients rows (add or remove)
    row0, controls_col1, controls_col2, _ = st.columns([1, 1, 1, 3])
    with row0:
        st.write("**Ingredientes**")
    with controls_col1:
        if st.button("Añadir fila", use_container_width=True):
            st.session_state.ingredient_rows += 1
            st.rerun()

    with controls_col2:
        if st.button("Quitar fila", use_container_width=True, disabled=st.session_state.ingredient_rows <= 1,):
            st.session_state.ingredient_rows -= 1
            st.rerun()

    with st.form("create_recipe_form"):
        st.subheader("Nombre")
        st.text_input("nombre de la receta", placeholder = "Nombre de la receta", label_visibility = "collapsed")

        st.subheader("Ingredientes")

        st.number_input("Numero de personas", min_value=1, step=1, width = 150)
        header_cols = st.columns([0.8, 0.1, 0.1])
        header_cols[0].markdown("**Ingrediente**")
        header_cols[1].markdown("**Cantidad**")
        header_cols[2].markdown("**Unidad**")

        for i in range(st.session_state.ingredient_rows):
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

            with col1:
                st.text_input("Ingrediente",key=f"ingredient_name_{i}",label_visibility="collapsed",placeholder="Tomate")
            with col2:
                st.number_input("Cantidad",min_value=0.0,step=0.5,key=f"ingredient_qty_{i}",label_visibility="collapsed")
            with col3:
                st.selectbox("Unidad",UNITS,key=f"ingredient_unit_{i}",label_visibility="collapsed")
            

        st.subheader("Preparación")
        st.text_area("Pasos", placeholder = "Pasos", label_visibility = "collapsed", height=180)

        st.subheader("Clasificación")
        st.text_input("Tags separados por comas", placeholder = "Tags separados por comas", label_visibility = "collapsed")
        submitted = st.form_submit_button("Guardar receta")

    if submitted:
        st.warning("Todavía no está conectada a la base de datos.")

# View list of recipies already created
def render_view_recipes():
    st.title("Ver recetas")
    search_name = st.text_input("Buscar por nombre")
    selected_tags = st.multiselect(
        "Filtrar por tags",
        options=["caliente", "rápida", "ensalada", "fría", "pasta"],
    )
    search_ingredient = st.text_input("Buscar por ingrediente")



selected_page = render_sidebar()

if selected_page == "Inicio":
    render_home()
elif selected_page == "Crear receta":
    render_create_recipe()
elif selected_page == "Ver recetas":
    render_view_recipes()