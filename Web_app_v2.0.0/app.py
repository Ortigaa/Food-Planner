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
st.logo(r"C:\Users\rodrigo.delgado\Documentos\Food-Planner\Web_app_v2.0.0\app_icon.png", size="medium", link=None, icon_image=None)

st.set_page_config(
    page_title="Planificador Menus semanales",
    page_icon="🍽️",
    layout="wide",
)

PAGES = [
    "Inicio",
    "Crear receta",
    "Ver recetas",
]

DAYS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

def render_sidebar():
    st.sidebar.title("Menú")
    selected_page = st.sidebar.radio("Ir a", PAGES)
    return selected_page

def render_home():
    st.title("Planificador familiar de recetas")

    for dia in DAYS:
        with st.container(border=True):
            st.markdown(f"### {dia}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Comida**")
                st.info("Vacío")

            with col2:
                st.markdown("**Cena**")
                st.info("Vacío")

def render_create_recipe():
    st.title("Crear receta")
    st.write("Aquí irá el formulario para añadir una receta nueva.")

def render_view_recipes():
    st.title("Ver recetas")
    st.write("Aquí aparecerá la lista de recetas.")
    st.write("búsqueda y filtros por nombre, tags e ingredientes.")


selected_page = render_sidebar()

if selected_page == "Inicio":
    render_home()
elif selected_page == "Crear receta":
    render_create_recipe()
elif selected_page == "Ver recetas":
    render_view_recipes()