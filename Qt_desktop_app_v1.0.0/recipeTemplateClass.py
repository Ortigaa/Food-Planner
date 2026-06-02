#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 12:57:21 2020

@author: rodri

Module Documantation:
    
    
"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    # import os
    # import sys
    pass
    
except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))
    
# =============================================================================
# Your code starts here
# =============================================================================

class Recipe():
    """ Template of a recipe """
    
    def __init__(self, name):
        self.name = name
        self.ingredients_list = {}
        self.recipe = ""
        self.number_of_people = 0
        self.tags = []
        
    def add_ingredient(self, ingredient, quantity, unit):
        # Expects an string, float and string
        self.ingredients_list[ingredient] = [quantity, unit]
        
    def add_recipe(self, instructions):
        # Expects a string
        self.recipe = self.recipe + instructions
        
    def add_number_of_people(self, number):
        # Expects an integer
        self.number_of_people = self.number_of_people + number
        
    def add_tag(self, tag):
        """
        Adds the passed tags to the list of tags within the recipe class

        Parameters
        ----------
        tag : string
            A tag to define the recipe.

        Returns
        -------
        None.

        """
        # Expects a string
        self.tags.append(tag)
        
    def clear_recipe(self):
        """
        Clears all the instances created within a given recipe class

        Returns
        -------
        None.

        """
        self.ingredients_list = {}
        self.recipe = ""
        self.number_of_people = 0
        self.tags = []
    
    # def rescale(self):
        
    