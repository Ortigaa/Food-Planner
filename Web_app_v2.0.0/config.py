#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 15:54 2026

@author: rodri

Module Documentation:
- Global variables and constants for the proyect

TODO

"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    from pathlib import Path

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================

# Global variables for use across pages
### List of pages for the sidebar
# At some point maybe is better to change it to actual pages (different scripts for each page)
PAGES = [
    "Inicio",
    "Crear receta",
    "Ver recetas",
    "Crear Menú semanal"
]

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Variables to store previous menus
LAST_MENU_SNAPSHOT_PATH = Path("last_weekly_menu.json")
MENU_EXPORTS_DIR = Path("menu_exports")