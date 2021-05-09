#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:36:19 2020

@author: rodri

Module Documentation:


TODO
 - Handle errors in the recipe input, i.e. only allow digits in the quantity line edit
 - Fix the generate list to take into account ingredient of same name with different units
 - Maybe create an unit converter in the background
 - Implement maximum price for the shopping list
 - Button to clear specific date in calendar view
 - Button to add more days to the calendar
"""

# =============================================================================
# Import additional modules, if fail, raise an error
# =============================================================================
try:
    import os
    import random
    import sys
    import pickle
    from datetime import datetime

except ModuleNotFoundError as imp_error:
    print("Import Error: {0}".format(imp_error))

# =============================================================================
# Your code starts here
# =============================================================================

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QCompleter, QMessageBox, QMenu
# GUI files
import recetario_ui  # Name of the main GUI.py file. Convert from .ui to .py with pyuic5
# Additional GUI files
import newRecipeDialog
import newRecipeInputWindow
import listRecipesWindow
import chooseDate
# File with the class definition for the recipe template
import recipeTemplateClass

# =============================================================================
# Global variables
# =============================================================================
RECETAS = []


# =============================================================================
# Useful functions
# =============================================================================
# Create an unique name from the recipe name
def create_inst_name(intr_name):
    "Create and unique instance name"
    words = intr_name.split(" ")
    final_name = ""
    for word in words:
        if len(word) >= 4:
            final_name = final_name + word[:3]
        else:
            pass
    return final_name

# ==============================================================================

class newRecipeInput(QtWidgets.QDialog, newRecipeInputWindow.Ui_newRecipeInput):
    """
    This class defines the window in which all the parameters for a recipe are introduced
    by the user.
    """
    def __init__(self, parent=None):
        super(newRecipeInput, self).__init__(parent)
        self.setupUi(self)
        self.input_name_window = parent
        self.name = self.input_name_window.lineNameInput.text()
        global RECETAS
#        self.lblRecipeName.setText("Receta de " + RECETAS[-1].name)
        self.lblRecipeName.setText("Receta de " + self.name)
        self.btnBox.accepted.connect(self.add_recipe_to_list)

        # Data container for new lines functionalty
        self.list_linesNames, self.list_linesQty, self.list_cmbUnits, self.index = [], [], [], 0
        self.list_linesNames.append(self.lnName)
        self.list_linesQty.append(self.lnQty)
        self.list_cmbUnits.append(self.cmbUnits)
        self.index += 1

        # Add line button functionalty
        self.btnAddLine.clicked.connect(self.add_line)

        # Button to add tags to list
        self.btnAddTag.clicked.connect(self.add_tag_to_list)
        # Button to remove tags from the list
        self.btnRemoveTag.clicked.connect(self.remove_tag_from_list)

    def add_recipe_to_list(self):
        """
        Function to add all the input parameters to recipeTemplateClass.
        If everything goes fine, it takes the text, all the ingredients and the tags.
        At the end the recipe class is added to the global list of RECETAS (this is written as
        the recipe book after saving the book)
        """
        # TODO
        # - Handle errors
        # - Allow user to correct the mistakes in the input without closing the window
        all_good = True
        number_of_people = int(self.spinPeopleNumber.value())
        RECETAS[-1].add_number_of_people(number_of_people)
        instructions = self.textInstructions.toPlainText()
        # Get all the tags from the listTags widget, store them in a list
        tagsTextList = [str(self.listTags.item(i).text()) for i in range(self.listTags.count())]
        for tag in tagsTextList:
            # pass each tag in the list to the recipe class
            RECETAS[-1].add_tag(tag)
        if instructions:
            RECETAS[-1].add_recipe(instructions)
        else:
            RECETAS[-1].add_recipe(instructions)

        for e in range(len(self.list_linesNames)):
            ing_name = self.list_linesNames[e].text()
            ing_qty = self.list_linesQty[e].text()
            ing_unit = self.list_cmbUnits[e].currentText()
            if ing_name and ing_qty and ing_unit:
                try:
                    ing_qty_num = float(ing_qty)
                    norm_ing_qty = ing_qty_num/number_of_people
                except ValueError:
                    print("Can not convert to float")
                    all_good = False
            else:
                all_good = False
            if all_good:
                RECETAS[-1].add_ingredient(ing_name, norm_ing_qty, ing_unit)
            else:
                self.recipe_error()

    def recipe_error(self):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText("Parametros invalidos")
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()

    def add_tag_to_list(self):
        """
        Takes the tag and add it to the WidgetList of tags
        *** NOTE: this function does not add tags directly to the recipeClass instance,
        only visually to the widget.
        """
        tag = self.lineTag.text()
        self.listTags.addItem(tag)
        self.lineTag.clear()

    def remove_tag_from_list(self):
        """
        Removes the selected tag in the list from the list
        Unfortunately there is no implemented method in the QListWidget to do this
        easily, so I am resorted to do it the hard way.
        """
        self.listTags.takeItem(self.listTags.currentRow())

    def add_line(self):
        """
        This is a very long function, but I could not think of a better way to implement it.
        It adds a new line to the ingredient input after pressing the button. It is basically
        brute forcing a new line, by creating new objects after the ones in the original
        file
        """
        self.index += 1
        self.list_linesNames.append(QtWidgets.QLineEdit(self.scrollAreaWidgetContents))
        self.list_linesNames[-1].setObjectName("lnName"+str(self.index))
        self.gridLyIngridients.addWidget(self.list_linesNames[-1], self.index, 
                                                 0, 1, 1, QtCore.Qt.AlignTop)
        self.list_linesQty.append(QtWidgets.QLineEdit(self.scrollAreaWidgetContents))
        self.list_linesQty[-1].setObjectName("lnQty"+str(self.index))
        self.gridLyIngridients.addWidget(self.list_linesQty[-1], self.index, 
                                         1, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.list_cmbUnits.append(QtWidgets.QComboBox(self.scrollAreaWidgetContents))
        self.list_cmbUnits[-1].setObjectName("cmbUnits"+str(self.index))
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].setItemText(0, "")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.gridLyIngridients.addWidget(self.list_cmbUnits[-1], self.index, 
                                         2, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        # Add the labels in the combobox
        _translate = QtCore.QCoreApplication.translate
        self.list_cmbUnits[-1].setItemText(1, _translate("newRecipeInput", "gramos"))
        self.list_cmbUnits[-1].setItemText(2, _translate("newRecipeInput", "kilogramos"))
        self.list_cmbUnits[-1].setItemText(3, _translate("newRecipeInput", "piezas"))
        self.list_cmbUnits[-1].setItemText(4, _translate("newRecipeInput", "mL"))
        self.list_cmbUnits[-1].setItemText(5, _translate("newRecipeInput", "latas"))
        # Modify the spacer accordingly
        self.gridLyIngridients.removeItem(self.spacerItem)
        self.gridLyIngridients.removeItem(self.spacerItem1)
        self.gridLyIngridients.removeItem(self.spacerItem2)
        self.spacerItem = QtWidgets.QSpacerItem(20, 40, 
        QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLyIngridients.addItem(self.spacerItem, self.index+1, 0, 1, 1)
        self.spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLyIngridients.addItem(self.spacerItem1, self.index+1, 1, 1, 1)
        self.spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLyIngridients.addItem(self.spacerItem2, self.index+1, 2, 1, 1)

class newRecipe(QtWidgets.QDialog, newRecipeDialog.Ui_newRecipeDialog):
    "Shows a window to introduce the name of the new recipe"
    # TODO
    # - Make a function to search for duplicate names in the recipe list
    def __init__(self, parent=None):
        super(newRecipe, self).__init__(parent)
        self.setupUi(self)
        self.btnOptions.accepted.connect(self.accept_name)
        self.btnOptions.rejected.connect(self.cancel_new_recipe)
        self.recipe_name = self.lineNameInput.text()

    # Accept the name entrered in the dialog. Check is a name is given, if not retry
    def accept_name(self):
        if self.lineNameInput.text():
            self.recipe_name = self.lineNameInput.text()
#            print(self.recipe_name)
            self.instName = create_inst_name(self.recipe_name)
#            print(self.instName)
            globals()[self.instName] = recipeTemplateClass.Recipe(self.recipe_name)
            global RECETAS
            RECETAS.append(globals()[self.instName])
            self.new_recipe_input = newRecipeInput(self)
            self.new_recipe_input.show()
        else:
            # If no name give warning box pop up and close the dialog
            QtWidgets.QMessageBox.warning(None, "Advertencia", 
                                              "No has añadido ningun nombre")
            newRecipe(self).show()
            print("No name given")

    # Cancel the operation and close the window
    def cancel_new_recipe(self):
        # print("Close this window")
        self.close()

class recipeInspect(QtWidgets.QDialog, newRecipeInputWindow.Ui_newRecipeInput):
    "Display all the parameters of a recipe in a nice GUI"
    def __init__(self, recipeName, parent=None):
        super(recipeInspect, self).__init__(parent)
        self.setupUi(self)
        self.recipeName = recipeName
        # Set the name of the recipe
        self.lblRecipeName.setText("Receta de " + self.recipeName)
        # Search for the instance in the list of recipes
        for inst in RECETAS:
            if inst.name == self.recipeName:
                self.recipe_instance = inst
                self.recipeListIndex = RECETAS.index(inst)
        self.spinPeopleNumber.setValue(self.recipe_instance.number_of_people)
        self.spinPeopleNumber.valueChanged.connect(self.change_number_of_people)
        self.textInstructions.setText(self.recipe_instance.recipe)

        # Data container for new lines functionalty
        self.list_linesNames, self.list_linesQty, self.list_cmbUnits, self.index = [], [], [], 0
        self.list_linesNames.append(self.lnName)
        self.list_linesQty.append(self.lnQty)
        self.list_cmbUnits.append(self.cmbUnits)
        self.index += 1

        # Add line button functionalty
        self.btnAddLine.clicked.connect(self.add_line)
        
        # Button to add tags to list
        self.btnAddTag.clicked.connect(self.add_tag_to_list)
        # Button to remove tags from the list
        self.btnRemoveTag.clicked.connect(self.remove_tag_from_list)

        # Look the number of ingredients and add the corresponding number of lines
        for n in range(len(self.recipe_instance.ingredients_list)-1):
            self.add_line()

        # Fill the ingredient list
        for ingre, num in zip(self.recipe_instance.ingredients_list.keys(), range(self.index)):
            self.list_linesNames[num].setText(ingre)
            ingredient_quantity = self.recipe_instance.number_of_people \
                                *self.recipe_instance.ingredients_list[ingre][0]
            self.list_linesQty[num].setText(str(ingredient_quantity))
            self.list_cmbUnits[num].setCurrentIndex(
            self.list_cmbUnits[num].findText(self.recipe_instance.ingredients_list[ingre][1]))

        # Fill the tags from the recipe
        for tag in self.recipe_instance.tags:
            self.listTags.addItem(tag)
            
        # When the accept button is clicked check if changes has been made in the 
        # recipe, and ask the user if wants to save the changes
        self.btnBox.accepted.connect(self.check_changes)
        
    def check_changes(self):
        # print("Works!")
        all_good = True
        # Get all the parameters in the window
        # Get the number of people
        number_of_people = int(self.spinPeopleNumber.value())
        # Get all the tags from the listTags widget, store them in a list
        tagsTextList = [str(self.listTags.item(i).text()) for i in range(self.listTags.count())]
        # Get the instructions
        instructions = self.textInstructions.toPlainText()
        # Get the ingredients
        ingredients_virtual = {}
        for e in range(len(self.list_linesNames)):
            ing_name = self.list_linesNames[e].text()
            ing_qty = self.list_linesQty[e].text()
            ing_unit = self.list_cmbUnits[e].currentText()
            if ing_name and ing_qty and ing_unit:
                try:
                    ing_qty_num = float(ing_qty)
                    norm_ing_qty = ing_qty_num/number_of_people
                except ValueError:
                    print("Can not convert to float")
                    all_good = False
            else:
                all_good = False
            if all_good:
                ingredients_virtual[ing_name] = [norm_ing_qty, ing_unit]
        
        if self.recipe_instance.number_of_people == number_of_people and \
        tagsTextList == self.recipe_instance.tags and \
        self.recipe_instance.recipe == instructions and \
        self.recipe_instance.ingredients_list == ingredients_virtual:
            print("All was the same")
        else:
            buttonReply = QMessageBox.question(self, 'Receta Cambiada', 
           "¿Quieres guardar los cambios?", QMessageBox.Yes | QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                RECETAS[self.recipeListIndex].clear_recipe()
                RECETAS[self.recipeListIndex].add_number_of_people(number_of_people)
                for tag in tagsTextList:
                    RECETAS[self.recipeListIndex].add_tag(tag)
                RECETAS[self.recipeListIndex].add_recipe(instructions)
                RECETAS[self.recipeListIndex].ingredients_list = ingredients_virtual
            else:
                print('No clicked.')
        
    def add_tag_to_list(self):
        """
        Takes the tag and add it to the WidgetList of tags
        *** NOTE: this function does not add tags directly to the recipeClass instance,
        only visually to the widget.
        """
        tag = self.lineTag.text()
        self.listTags.addItem(tag)
        self.lineTag.clear()

    def remove_tag_from_list(self):
        """
        Removes the selected tag in the list from the list
        Unfortunately there is no implemented method in the QListWidget to do this
        easily, so I am resorted to do it the hard way.
        """
        self.listTags.takeItem(self.listTags.currentRow())
        
    def change_number_of_people(self):
        "Modify the ingredient quantity if the spin box value is changed"
        for ingre, num in zip(self.recipe_instance.ingredients_list.keys(), range(self.index)):
            ingredient_quantity = self.spinPeopleNumber.value() \
                            *self.recipe_instance.ingredients_list[ingre][0]
            self.list_linesQty[num].setText(str(ingredient_quantity))

    def add_line(self):
        "Add a new line to introduce ingredients in the window"
        self.index += 1
        self.list_linesNames.append(QtWidgets.QLineEdit(self.scrollAreaWidgetContents))
        self.list_linesNames[-1].setObjectName("lnName"+str(self.index))
        self.gridLyIngridients.addWidget(self.list_linesNames[-1], self.index, 
                                         0, 1, 1, QtCore.Qt.AlignTop)
        self.list_linesQty.append(QtWidgets.QLineEdit(self.scrollAreaWidgetContents))
        self.list_linesQty[-1].setObjectName("lnQty"+str(self.index))
        self.gridLyIngridients.addWidget(self.list_linesQty[-1], self.index,
                                 1, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.list_cmbUnits.append(QtWidgets.QComboBox(self.scrollAreaWidgetContents))
        self.list_cmbUnits[-1].setObjectName("cmbUnits"+str(self.index))
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].setItemText(0, "")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.list_cmbUnits[-1].addItem("")
        self.gridLyIngridients.addWidget(self.list_cmbUnits[-1], self.index, 
                             2, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        # Add the labels in the combobox
        _translate = QtCore.QCoreApplication.translate
        self.list_cmbUnits[-1].setItemText(1, _translate("newRecipeInput", "gramos"))
        self.list_cmbUnits[-1].setItemText(2, _translate("newRecipeInput", "kilogramos"))
        self.list_cmbUnits[-1].setItemText(3, _translate("newRecipeInput", "piezas"))
        self.list_cmbUnits[-1].setItemText(4, _translate("newRecipeInput", "mL"))
        self.list_cmbUnits[-1].setItemText(5, _translate("newRecipeInput", "latas"))
        # Modify the spacer accordingly
        self.gridLyIngridients.removeItem(self.spacerItem)
        self.gridLyIngridients.removeItem(self.spacerItem1)
        self.gridLyIngridients.removeItem(self.spacerItem2)
        self.spacerItem = QtWidgets.QSpacerItem(20, 40, 
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLyIngridients.addItem(self.spacerItem, self.index+1, 0, 1, 1)
        self.spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLyIngridients.addItem(self.spacerItem1, self.index+1, 1, 1, 1)
        self.spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLyIngridients.addItem(self.spacerItem2, self.index+1, 2, 1, 1)

class calendarWindowFromList(QtWidgets.QDialog, chooseDate.Ui_Dialog):
    "Opens a dialog to choose the date in which to add a recipe, when this recipe is selected from the list of recipes"
    def __init__(self, parent=None):
        super(calendarWindowFromList, self).__init__(parent)
        self.setupUi(self)
        # Set the parent of this window as the listRecipeWin
        self.list_recipes_window = parent
        self.buttonBox.accepted.connect(self.date_choosed)

    def date_choosed(self):
        "Adds the recipe to the main calendar widget in the main window"
#        self.rowCoord = (self.tableWidget.currentColumn(), self.tableWidget.currentRow())
        self.rowCoord = self.tableWidget.currentRow()
        self.colCoord = self.tableWidget.currentColumn()
        self.num_people = self.spinNumberPeople.value()
#        self.list_recipes_window.coordinates += self.coordinates
        self.recipe_name = self.list_recipes_window.listRecipes.currentItem().text()
        self.list_recipes_window.main_window.tableWeek.setItem(self.rowCoord, self.colCoord, QTableWidgetItem(self.recipe_name + "(" + str(self.num_people) +"p)"))


class calendarWindowFromMain(QtWidgets.QDialog, chooseDate.Ui_Dialog):
    """
    Opens a dialog to choose the date in which to add a recipe, 
    when this recipe is selected from the Buscar search bar in the main window
    """
    def __init__(self, parent=None):
        super(calendarWindowFromMain, self).__init__(parent)
        self.setupUi(self)
        # Set the parent of this window as the listRecipeWin
        self.main_window = parent
        self.buttonBox.accepted.connect(self.date_choosed)

    def date_choosed(self):
        "Adds the recipe to the main calendar widget in the main window"
#        self.rowCoord = (self.tableWidget.currentColumn(), self.tableWidget.currentRow())
        self.rowCoord = self.tableWidget.currentRow()
        self.colCoord = self.tableWidget.currentColumn()
#        self.list_recipes_window.coordinates += self.coordinates
        self.recipe_name = self.main_window.lineRecipe.text()
        self.num_people = self.spinNumberPeople.value()
        self.main_window.tableWeek.setItem(self.rowCoord, self.colCoord, 
        QTableWidgetItem(self.recipe_name + "(" + str(self.num_people) +"p)"))


class listRecipWin(QtWidgets.QDialog, listRecipesWindow.Ui_Dialog):
    "Simple window to list all the recipes in a book"
    def __init__(self, parent=None):
        super(listRecipWin, self).__init__(parent)
        self.setupUi(self)
        # Set the parent of this window as the main window
        self.main_window = parent
        if self.main_window.comes_from_search:
            for receta in self.main_window.similar_recipes:
                self.listRecipes.addItem(receta.name)
        else:
            global RECETAS
            for receta in RECETAS:
                self.listRecipes.addItem(receta.name)

        self.btnInspect.clicked.connect(self.inspectRecipe)
        self.btnClose.clicked.connect(self.close_window)
        self.btnAdd.clicked.connect(self.add_to_calendar)

        self.coordinates = ()
        
        # Reset the flag
        self.main_window.comes_from_search = False

    def inspectRecipe(self):
#        print(self.listRecipes.currentItem().text())
        # The name of the recipe (instance.name) is passed as argument in the new window
        self.inspect_window = recipeInspect(self.listRecipes.currentItem().text())
        self.inspect_window.show()

    def add_to_calendar(self):
        self.calendar_window = calendarWindowFromList(self)
        self.calendar_window.show()

    def close_window(self):
        self.close()



class MainWindow(QtWidgets.QMainWindow, recetario_ui.Ui_MainWindow):
    "Class for the main GUI window"
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # Fix table columns
        headerh = self.tableWeek.horizontalHeader()
        headerh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        for i in range(2):
            headerh.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        headerv = self.tableWeek.verticalHeader()
        headerv.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        for i in range(7):
            headerv.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        # Text for the book entry
        self.lineBook.setText("Ningún libro seleccionado")
        # Create an attibute to check where the list come from when listing all recipes
        self.comes_from_search = False

        # Menu buttons
        self.actionGuardar_Recetario.setShortcut("Ctrl+S")
        self.actionCerrar.setShortcut("Ctrl+Q")
        self.actionCerrar.triggered.connect(QtCore.QCoreApplication.instance().quit)
        self.actionA_adir_Receta.setShortcut("Ctrl+A")
        self.actionA_adir_Receta.triggered.connect(self.open_new_recipe_dialog)
        self.actionGuardar_Recetario.triggered.connect(self.save_recipe_book)
        self.actionAbrir_Recetario.triggered.connect(self.open_recipe_book)
        self.actionInspeccionar_Recetas.triggered.connect(self.open_recipe_list)


        # Functionality for slider and label of maximum price
        self.labelActualPrice.setText(str(self.sliderPrice.value())+" €")
        self.sliderPrice.valueChanged.connect(self.update_slider_prices)
        
        # Activate repetition
        self.checkRepetition.stateChanged.connect(self.activate_repetition)

        # Button funtions
        self.btnChangeBook.clicked.connect(self.open_recipe_book)
        self.btnAddRecipe.clicked.connect(self.add_to_calendar)
        self.btnGenerateList.clicked.connect(self.complete_table)
        self.btnReady.clicked.connect(self.generate_shopping_list)
        self.btnSearchRecipe.clicked.connect(self.search_recipe)
        
    #   TODO
    #    Attempt to create a context menu in the table widget
    #   to display after right click on the cell
    #
    #self.tableWeek.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
   
    #     self.tableWeek.customContextMenuRequested.connect(self.generateMenu)
    #     self.tableWeek.viewport().installEventFilter(self)
        
    #     # def contextMenuEvent(self, event):
    #     #     cmenu = QMenu(self)
    
    #     #     newAct = cmenu.addAction("New")
    #     #     openAct = cmenu.addAction("Open")
    #     #     quitAct = cmenu.addAction("Quit")
    #     #     action = cmenu.exec_(self.mapToGlobal(event))
    
    #     #     if action == quitAct:
    #     #         app.quit()
        
    # def eventFilter(self, source, event):
    #     if(event.type() == QtCore.QEvent.MouseButtonPress and 
    #        event.buttons() == QtCore.Qt.RightButton and
    #        source is self.tableWeek.viewport()):
    #         item = self.tableWeek.itemAt(event.pos())
    #         print('Global Pos:', event.globalPos())
    #         if item is not None:
    #             print('Table Item:', item.row(), item.column())
    #             self.menu = QMenu(self)
    #             self.menu.addAction(item.text())         #(QAction('test'))
    #             #menu.exec_(event.globalPos())
    #     return super(MainWindow, self).eventFilter(source, event)
    
    # def generateMenu(self, pos):
    #     print("pos======",pos)
    #     self.menu.exec_(self.tableWidget.mapToGlobal(pos))
    
    def activate_repetition(self):
        """
        Change the state of the spin box with the number of repetition for a
        given recipe

        Returns
        -------
        None.

        """
        if self.checkRepetition.isChecked():
            self.spBoxDepth.setReadOnly(False)
        else:
            self.spBoxDepth.setReadOnly(True)

    # Start functions for the widgets
    def search_recipe(self):
        "Search recipes with name similar to that in put in the text box"
        global RECETAS
        recetas_copy = RECETAS.copy()
        # Convert the search term and the recipe name all to lower case to match
        # any possible case
        search_term = self.lineRecipe.text().lower()
        self.similar_recipes = []
        # If no term has been introduced in the box pop up a window informing the error
        if not search_term:
            self.err_wind = QtWidgets.QMessageBox.information(None, "Informacion", 
              "No has introducido ningun termino de busqueda", QMessageBox.Ok)
        else:
            for receta in recetas_copy:
                if search_term in receta.name.lower():
#                    print(receta.name)
                    self.similar_recipes.append(receta)
                elif any(search_term in tag for tag in receta.tags):
                    self.similar_recipes.append(receta)
                else:
                    pass
            self.comes_from_search = True
            self.open_recipe_list()
            # print(self.comes_from_search)

    def save_recipe_book(self):
        """
        Save all the recipes added to the program into an external file with 
        extension .rec. For this use a native Python modules pickle, so it 
        creates a binary file. Can only be open or edited with Python
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, 
        "Guardar Libro de Recetas", "", "Recetario (*.rec);;All Files (*)", options=options)
        global RECETAS
        # If file has to be overwritten, remove the extension, 
        # then add it again because it has to be done
        if fileName.endswith(".rec"):
            fileName = fileName[:-4]
        with open(fileName+".rec", "wb") as out_file:
            pickle.dump(RECETAS, out_file)
        self.lineBook.setText(fileName)
        # Text for the line recipe. None at the beginning, but can autocomplete after
        # a cook book as been selected
        self.names = [receta.name for receta in RECETAS]
        self.completer = QCompleter(self.names)
        self.lineRecipe.setCompleter(self.completer)

    def open_recipe_book(self):
        "Open a recipe book with all the recipes previously save"
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 
        "Abrir Libro de Recetas", "", "Recetario (*.rec);;All Files (*)", options=options)
        # Check if any file has been selected
        if fileName:
            global RECETAS
            with open(fileName, "rb") as input_file:
                RECETAS = pickle.load(input_file)
            self.lineBook.setText(fileName)
        else:
            pass
        # Text for the line recipe. None at the beginning, but can autocomplete after
        # a cook book as been selected
        self.names = [receta.name for receta in RECETAS]
        self.completer = QCompleter(self.names)
        self.lineRecipe.setCompleter(self.completer)
        # Fill the tag list in the main window with all the tags from the different recipes
        self.listTags.clear()
        self.tags = []
        seen = set(self.tags)
        for receta in RECETAS:
            # Prevent the addition of duplicate entries
#            print(receta.tags)
            for tag in receta.tags:
                if tag not in seen:
                    seen.add(tag)
                    self.tags.append(tag)
        for tag in self.tags:
            self.listTags.addItem(tag)

    def update_slider_prices(self, value):
        "Updates the price when the slider is changed"
        self.labelActualPrice.setText(str(self.sliderPrice.value())+" €")

    def open_new_recipe_dialog(self):
        "Open the dialog for introducing a new recipe"
        self.new_recipe_dialog = newRecipe(self)
        self.new_recipe_dialog.show()

    def open_recipe_list(self):
        "Opens a window to inspect all recipes in the current recipe book"
        self.recipe_list = listRecipWin(self)
        self.recipe_list.show()
        # print("I open the recipe list")
        # print(self.comes_from_search)

    def add_to_calendar(self):
        """
        Add the selected recipe in the text box to the calendar. The date in 
        which to add is selected in the pop up window
        """
        if self.lineRecipe.text():
            self.calendar_window = calendarWindowFromMain(self)
            self.calendar_window.show()
        else:
            pass

    def complete_table(self):
        "Complete the week table with randomly selected recipes from the current book"
        global RECETAS
        # Get a copy of all the recipes, so they are not modified
        recetas_copy = RECETAS.copy()
        # Keep track of all the recipes used and the number of times
        used_recipes = {}
        num_people = str(self.spBoxNumberPeople.value())
        # self.tableWeek.clear() # Unfortunately this also clears the table headers
        # clear the table
        for row in range(self.tableWeek.rowCount()):
            for column in range(self.tableWeek.columnCount()):
                self.tableWeek.setItem(row, column, QTableWidgetItem(""))
        self.labelObj = self.listTags.selectedItems()
        labels = [lab.text() for lab in self.labelObj]
        # print(labels)
        try:
            if labels:
                # print("I tried this")
                # If there are labels selected fill the table with recipes that
                # have this labels
                # Create a sublist from all the recipes that match the labels selected
                recipe_labelled = [receta for receta in recetas_copy if any(tag in receta.tags for tag in labels)]
                # print(recipe_labelled)
                for row in range(self.tableWeek.rowCount()):
                    for column in range(self.tableWeek.columnCount()):
                        element = random.choice(recipe_labelled)
        #                print(row, column)
        #                print(element.name)
                        if self.checkRepetition.isChecked():
                            num_rep = self.spBoxDepth.value()
                            if element.name not in used_recipes.keys():  
                                self.tableWeek.setItem(row, column, 
                                QTableWidgetItem(element.name + "("+num_people+"p)"))
                                used_recipes[element.name] = 1
                            elif element.name in used_recipes.keys() and \
                            used_recipes[element.name] < num_rep:
                                self.tableWeek.setItem(row, column, 
                                QTableWidgetItem(element.name + "("+num_people+"p)"))
                                used_recipes[element.name] += 1
                            else:
                                recipe_labelled.remove(element)
                                element = random.choice(recipe_labelled)
                                self.tableWeek.setItem(row, column, 
                                QTableWidgetItem(element.name + "("+num_people+"p)"))
                                used_recipes[element.name] = 1
                        elif not self.checkRepetition.isChecked() and \
                            element.name not in used_recipes.keys():
                            self.tableWeek.setItem(row, column, 
                            QTableWidgetItem(element.name + "("+num_people+"p)"))
                            used_recipes[element.name] = 1
                            recipe_labelled.remove(element)
                        # elif not self.checkRepetition.isChecked() and \
                        #     element.name in used_recipes.keys():
                        #     element = random.choice(recetas_copy)
                        else:
                            pass
            else:
            # If no labels are selected
                for row in range(self.tableWeek.rowCount()):
                    for column in range(self.tableWeek.columnCount()):
                        element = random.choice(recetas_copy)
        #                print(row, column)
        #                print(element.name)
                        if self.checkRepetition.isChecked():
                            num_rep = self.spBoxDepth.value()
                            if element.name not in used_recipes.keys():  
                                self.tableWeek.setItem(row, column, 
                                QTableWidgetItem(element.name + "("+num_people+"p)"))
                                used_recipes[element.name] = 1
                            elif element.name in used_recipes.keys() and \
                            used_recipes[element.name] < num_rep:
                                self.tableWeek.setItem(row, column, 
                                QTableWidgetItem(element.name + "("+num_people+"p)"))
                                used_recipes[element.name] += 1
                            else:
                                recetas_copy.remove(element)
                                element = random.choice(recetas_copy)
                                self.tableWeek.setItem(row, column, 
                                QTableWidgetItem(element.name + "("+num_people+"p)"))
                                used_recipes[element.name] = 1
                                
                        elif not self.checkRepetition.isChecked() and \
                            element.name not in used_recipes.keys():
                            self.tableWeek.setItem(row, column, 
                            QTableWidgetItem(element.name + "("+num_people+"p)"))
                            used_recipes[element.name] = 1
                            recetas_copy.remove(element)
                        # elif not self.checkRepetition.isChecked() and \
                        #     element.name in used_recipes:
                        #     element = random.choice(recetas_copy)
                        else:
                            pass
        except IndexError:
            # Pass an error if no book has been selected
            self.err_wind = QtWidgets.QMessageBox.information(None, "Informacion",
                                      "No hay libro seleccionado", QMessageBox.Ok)

    def generate_shopping_list(self):
        self.infobox = QMessageBox.information(self, 'Crear Lista', 
           "Un archivo externo será creado con la lista de la compra, ¿quieres continuar?", QMessageBox.Yes | QMessageBox.No)
        """
        Produce an output text file with all the ingredients and the necessary
        quantities for the week recipes
        """
        if self.infobox == QMessageBox.Yes:
            global RECETAS
            # Copy the list of RECIPES so it is not modified by the program
            recetas_copy = RECETAS.copy()
            recipes_names = []
            shopping_list = {}
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for row in range(self.tableWeek.rowCount()):
                for column in range(self.tableWeek.columnCount()):
                    # print(shopping_list)
                    item = self.tableWeek.item(row, column)
                    if len(item.text())>1:
                        # print(item)
                        recipe_name = item.text()[:item.text().find("(")]
                        recipes_names.append(recipe_name)
                        num_people = float(item.text()[item.text().find("(")+1:item.text().find("p)")])
                        rec_obj = [receta for receta in recetas_copy if recipe_name == receta.name][0]
                        for ing in rec_obj.ingredients_list.keys():
                            # Check if the entry exist already in the shopping list
                            if ing not in shopping_list.keys():
                                # Create a new key in the shopping list dictionary and for its values
                                # copy of the ingredient list
                                shopping_list[ing] = rec_obj.ingredients_list[ing].copy()
                                # Rescale the value to the number of people
                                shopping_list[ing][0] = shopping_list[ing][0]*num_people
                            else:
                                # If it is already in the dictionary check if the units are the same
                                if rec_obj.ingredients_list[ing][1] == shopping_list[ing][1]:
                                    shopping_list[ing][0] += rec_obj.ingredients_list[ing][0]*num_people
                                else:
                                    # If the units are different create a new name 
                                    # with the unit attached
                                    shopping_list[ing+"_"+rec_obj.ingredients_list[ing][1]] = rec_obj.ingredients_list[ing].copy()
                                    # Rescale the value to the number of people
                                    shopping_list[ing+"_"+rec_obj.ingredients_list[ing][1]][0] = shopping_list[ing+"_"+rec_obj.ingredients_list[ing][1]][0]*num_people
                    else:
                        pass
            with open("Lista_Compra_"+timestamp+".txt", "w+") as outFile:
                outFile.write("Recetas:\n\n")
                for r in recipes_names:
                    outFile.write(r + "\n")
                outFile.write("\n")
                outFile.write("Ingredientes:\n\n")
                for e in shopping_list.keys():
                    outFile.write(e + "\t" + str(shopping_list[e][0]) + "\t" + shopping_list[e][1] + "\n")
                outFile.close()
            # print(shopping_list)
        else:
            pass

    def closeEvent(self, event):
        self.warning = QtWidgets.QMessageBox.critical(None, "Advertencia", 
"Las recetas no se guardan automaticamente", QMessageBox.Ok, QMessageBox.Cancel)
        if self.warning == QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()




def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()