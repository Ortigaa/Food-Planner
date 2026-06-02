#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 21:36:44 2020

@author: rodri
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants
from scipy import interpolate
import scipy.integrate as integrate
import scipy as scy
import os
import random
import string


def randomStringDigits(stringLength=8):
    """Generate a random string of letters and digits to be used as 
    ID for the different recipes"""
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


class Recipe():
    """ Template of a recipe """
    
    def __init__(self, name):
        self.name = name
        self.ingredients_list = {}
        self.recipe = ""
        
    def add_ingredient(self, ingredient, quantity):
        if quantity is not str:
            quant = str(quantity)
            self.ingredients_list[ingredient] = quant
        else:
            self.ingredients_list[ingredient] = quantity
        
    def add_recipe(self, instrunctions):
        self.recipe = self.recipe + instrunctions
        

print("Compilation finished")

recetas = []

ber_rell = Recipe("Berenjenas Rellenas")
ber_rell.add_ingredient("cebolla", 2)
ber_rell.add_ingredient("sal", "un pellizco")
ber_rell.add_recipe("Comer cebolla cruda")

pes_plancha = Recipe("Pescado a la plancha")
pes_plancha.add_ingredient("Sardinas", "un par")
pes_plancha.add_recipe("Poner el pescado en la plancha hasta que este negro")

recetas.append(ber_rell)
recetas.append(pes_plancha)


def printRecetario():
    for receta in recetas:
        print(receta.name)

print("Primer recetario")  
printRecetario()
    

new_name = input("Nombre de la receta: ")

# Create an unique name from the recipe name
def create_inst_name(intr_name):
    words = intr_name.split(" ")
    final_name = ""
    for w in words:
        if len(w) >= 4:
            final_name = final_name + w[:3]
        else:
            pass
    return final_name

print("Nombre de la instancia")
instName = create_inst_name(new_name)

# Create an instance of the class Recipe with the unique identifier and the attribute
# name as the name introduced in the input
globals()[instName] = Recipe(new_name)
recetas.append(globals()[instName])

print("Segundo recetario")
printRecetario()
    
def buscar_receta(cook_book, nombre):
    for receta in cook_book:
        if receta.name == nombre:
            print("Yaaaay")
        else:
#            print("Neiiiiin")
            pass
       
buscar_receta(recetas, new_name)


