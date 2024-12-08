import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gio

import requests
from io import BytesIO

import gettext

t = gettext.gettext

def iniciar(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("CocktailDesktop.glade")  # Buildeo el glade
        self.adminSignals(self)
        self.window = self.builder.get_object("App")
        self.stack = self.builder.get_object("pageStack")
        self.home = self.builder.get_object("home")
        self.boxSearchCocktail = self.builder.get_object("boxSearchCocktail")
        self.boxSearchIngridient = self.builder.get_object("boxSearchIngridient")
        self.boxDetailCocktail = self.builder.get_object("boxDetailCocktail")
        self.boxDetailIngridient = self.builder.get_object("boxDetailIngridient")
        self.boxIngridientDetails = self.builder.get_object("boxIngridientDetails")
        self.cocktailS1 = self.builder.get_object("IngridientS1")
        self.cocktailS2 = self.builder.get_object("IngridientS2")
        self.cocktailS3 = self.builder.get_object("IngridientS3")
        self.cocktailS4 = self.builder.get_object("IngridientS4")
        self.cocktailS1 = self.builder.get_object("cocktailS1")
        self.cocktailS2 = self.builder.get_object("cocktailS2")
        self.cocktailS3 = self.builder.get_object("cocktailS3")
        self.cocktailS4 = self.builder.get_object("cocktailS4")
        self.checkAlcoholicCocktail = self.builder.get_object("checkAlcoholicCocktail")
        self.checkNonAlcoholicCocktail = self.builder.get_object("checkNonAlcoholicCocktail")
        self.window.connect("destroy", Gtk.main_quit)
        self.cocktailSpinner = self.builder.get_object("spinnerSearchingCocktail")
        self.ingredientSpinner = self.builder.get_object("spinnerSearchingIngridientLoading")
        self.cocktailWaitLabel = self.builder.get_object("labelChooseCocktail")
        self.ingredientWaitLabel = self.builder.get_object("labelRecomendedIngridientesSearch")
        self.checkAlcoholicCocktail.connect("toggled", self.on_checkbox_toggled, self.checkNonAlcoholicCocktail)
        self.checkNonAlcoholicCocktail.connect("toggled", self.on_checkbox2_toggled, self.checkAlcoholicCocktail)
        #---------------------------------------------------------------------------------------------------------
        #Botones, cajas y funciones de errores
        #---------------------------------------------------------------------------------------------------------
        self.boxErrorSearchCocktail = self.builder.get_object("boxErrorSearchCocktail")
        self.boxErrorSSearchIngridient = self.builder.get_object("boxErrorSSearchIngridient")
        self.boxWebErrorCSearchCocktail = self.builder.get_object("boxWebErrorCSearchCocktail")
        self.boxWebErrorIngSearchIngridient = self.builder.get_object("boxWebErrorIngSearchIngridient")
        self.boxErrorWebCDDetailCocktail= self.builder.get_object("boxErrorWebCDDetailCocktail")
        self.boxErrorWebCDDetailIngridient = self.builder.get_object("boxErrorWebCDDetailIngridient")
        #---------------------------------------------------------------------------------------------------------
        #Labels
        #---------------------------------------------------------------------------------------------------------
        self.builder.set_translation_domain("App")
        self.buttonCocktailsHome = self.builder.get_object("buttonCocktailsHome")
        self.buttonIngredientsHome = self.builder.get_object("buttonIngredientsHome")
        self.buttonHomeSCocktail = self.builder.get_object("buttonHomeSCocktail")
        self.buttonIngridientsSCocktail = self.builder.get_object("buttonIngridientsSCocktail")
        self.searchCocktail = self.builder.get_object("searchCocktail")
        self.labelChooseCocktail = self.builder.get_object("labelChooseCocktail")
        self.labelFilterSCocktail = self.builder.get_object("labelFilterSCocktail")
        self.labelAlcoholSCocktail1 = self.builder.get_object("labelAlcoholSCocktail1")
        self.checkAlcoholicCocktail = self.builder.get_object("checkAlcoholicCocktail")
        self.checkNonAlcoholicCocktail = self.builder.get_object("checkNonAlcoholicCocktail")
        self.labelFilterbyIngridient = self.builder.get_object("labelFilterbyIngridient")
        self.searchCocktailByIngridient = self.builder.get_object("searchCocktailByIngridient")
        self.labelSearchRandomCocktail = self.builder.get_object("labelSearchRandomCocktail")
        self.buttonTryNewThings = self.builder.get_object("buttonTryNewThings")
        self.buttonHomeSIngridient = self.builder.get_object("buttonHomeSIngridient")
        self.buttonCocktailsSIngrdients = self.builder.get_object("buttonCocktailsSIngrdients")
        self.searchIngridient = self.builder.get_object("searchIngridient")
        self.labelRecomendedIngridientesSearch = self.builder.get_object("labelRecomendedIngridientesSearch")
        self.buttonBackDetailCocktail = self.builder.get_object("buttonBackDetailCocktail")
        self.buttonHomeDetailCocktail = self.builder.get_object("buttonHomeDetailCocktail")
        self.buttonIngridientDetailCocktail = self.builder.get_object("buttonIngridientDetailCocktail")
        self.labelCocktailLook = self.builder.get_object("labelCocktailLook")
        self.labelCocktailInstructions = self.builder.get_object("labelCocktailInstructions")
        self.labelIngridientstomakeit = self.builder.get_object("labelIngridientstomakeit")
        self.buttonBackDetailIngridient = self.builder.get_object("buttonBackDetailIngridient")
        self.buttonHomeDetailIngridient = self.builder.get_object("buttonHomeDetailIngridient")
        self.buttonIngridientDetailIngridient = self.builder.get_object("buttonIngridientDetailIngridient")
        self.labelIngridientLook = self.builder.get_object("labelIngridientLook")
        self.labelIngridientAlcohol = self.builder.get_object("labelIngridientAlcohol")
        self.labelIngridientDescription = self.builder.get_object("labelIngridientDescription")
        self.labelCocktailswhichInclude = self.builder.get_object("labelCocktailswhichInclude")
        
        #boxErrorWebCDDetailIngridient
        self.buttonErrorWebCDBackDetailIngridient = self.builder.get_object("buttonErrorWebCDBackDetailIngridient")
        self.buttonErrorWebCDHomeDetailIngridient = self.builder.get_object("buttonErrorWebCDHomeDetailIngridient")
        self.buttonErrorWebCDIngridientDetailIngridient = self.builder.get_object("buttonErrorWebCDIngridientDetailIngridient")
        self.labelErrorWebIngDNotFound = self.builder.get_object("labelErrorWebIngDNotFound")
        self.buttonErrorWebIngDReload = self.builder.get_object("buttonErrorWebIngDReload")

        #boxErrorWebCDDetailCocktail
        self.buttonErrorWebCDBackDetailCocktail = self.builder.get_object("buttonErrorWebCDBackDetailCocktail")
        self.buttonErrorWebCDHomeDetailCocktail = self.builder.get_object("buttonErrorWebCDHomeDetailCocktail")
        self.buttonErrorWebCDIngridientDetailCocktail = self.builder.get_object("buttonErrorWebCDIngridientDetailCocktail")
        self.labelErrorWebCDNotFound = self.builder.get_object("labelErrorWebCDNotFound")
        self.buttonErrorWebCDReload = self.builder.get_object("buttonErrorWebCDReload")

        #boxWebErrorIngSearchIngridient
        self.buttonWebErrorIngHomeSIngridient = self.builder.get_object("buttonWebErrorIngHomeSIngridient")
        self.buttonWebErrorIngCocktailsSIngrdients = self.builder.get_object("buttonWebErrorIngCocktailsSIngrdients")
        self.searchWebErrorIngIngridient = self.builder.get_object("searchWebErrorIngIngridient")
        self.labelWebErrorIngShowIngridients = self.builder.get_object("labelWebErrorIngShowIngridients")
        self.labelWebErrorIngNotFound = self.builder.get_object("labelWebErrorIngNotFound")
        self.buttonWebErrorIngReload = self.builder.get_object("buttonWebErrorIngReload")

        #boxWebErrorCSearchCocktail
        self.buttonWebErrorCHomeSCocktail = self.builder.get_object("buttonWebErrorCHomeSCocktail")
        self.buttonWebErrorCIngridientsSCocktail = self.builder.get_object("buttonWebErrorCIngridientsSCocktail")
        self.labelWebErrorCFilterSCocktail = self.builder.get_object("labelWebErrorCFilterSCocktail")
        self.searchWebErrorCCocktail = self.builder.get_object("searchWebErrorCCocktail")
        self.labelWebErrorCAlcoholSCocktail = self.builder.get_object("labelWebErrorCAlcoholSCocktail")
        self.labelWebErrorCChooseCocktail = self.builder.get_object("labelWebErrorCChooseCocktail")
        self.checkWebErrorCAlcoholicCocktail = self.builder.get_object("checkWebErrorCAlcoholicCocktail")
        self.checkWebErrorCNonAlcoholicCocktail = self.builder.get_object("checkWebErrorCNonAlcoholicCocktail")
        self.labelWebErrorCNotFound = self.builder.get_object("labelWebErrorCNotFound")
        self.buttonWebErrorCReload = self.builder.get_object("buttonWebErrorCReload")
        self.labelErrorSFilterbyIngridient1 = self.builder.get_object("labelErrorSFilterbyIngridient1")
        self.searchErrorSCocktailByIngridient1 = self.builder.get_object("searchErrorSCocktailByIngridient1")
        self.labelErrorSSearchRandomCocktail1 = self.builder.get_object("labelErrorSSearchRandomCocktail1")
        self.buttonErrorSTryNewThings1 = self.builder.get_object("buttonErrorSTryNewThings1")

        #boxErrorSSearchIngridient
        self.buttonErrorSIngHomeSIngridient1 = self.builder.get_object("buttonErrorSIngHomeSIngridient1")
        self.buttonErrorSIngCocktailsSIngrdients1 = self.builder.get_object("buttonErrorSIngCocktailsSIngrdients1")
        self.searcErrorSInghIngridient = self.builder.get_object("searcErrorSInghIngridient")
        self.labelErrorSIngShowIngridients = self.builder.get_object("labelErrorSIngShowIngridients")
        self.labelErrorSIngNotFound = self.builder.get_object("labelErrorSIngNotFound")
        self.buttonErrorSIngReload = self.builder.get_object("buttonErrorSIngReload")

        #boxErrorSearchCocktail
        self.buttonHomeSCocktail1 = self.builder.get_object("buttonHomeSCocktail1")
        self.buttonIngridientsSCocktail1 = self.builder.get_object("buttonIngridientsSCocktail1")
        self.labelErrorSFilterSCocktail = self.builder.get_object("labelErrorSFilterSCocktail")
        self.searchErrorSCocktail = self.builder.get_object("searchErrorSCocktail")
        self.labelErrorSAlcoholSCocktail = self.builder.get_object("labelErrorSAlcoholSCocktail")
        self.checkErrorSAlcoholicCocktail = self.builder.get_object("checkErrorSAlcoholicCocktail")
        self.checkErrorSNonAlcoholicCocktail = self.builder.get_object("checkErrorSNonAlcoholicCocktail")
        self.labelErrorSChooseCocktail = self.builder.get_object("labelErrorSChooseCocktail")
        self.labelErrorSCNotFound = self.builder.get_object("labelErrorSCNotFound")
        self.buttonErrorSCReload = self.builder.get_object("buttonErrorSCReload")
        self.labelErrorSFilterbyIngridient = self.builder.get_object("labelErrorSFilterbyIngridient")
        self.searchErrorSCocktailByIngridient = self.builder.get_object("searchErrorSCocktailByIngridient")
        self.labelErrorSSearchRandomCocktail = self.builder.get_object("labelErrorSSearchRandomCocktail")
        self.buttonErrorSTryNewThings = self.builder.get_object("buttonErrorSTryNewThings")


        #home
        self.buttonErrorSTryNewThings.set_label(t("Cocktails"))
        self.buttonIngredientsHome.set_label(t("Ingredients"))

        #boxSearchCocktail
        self.buttonHomeSCocktail.set_label(t("Home"))
        self.buttonIngridientsSCocktail.set_label(t("Ingredients"))
        self.searchCocktail.set_placeholder_text(t("Search Cocktail"))
        self.labelChooseCocktail.set_text(t("Recomended cocktails"))
        self.labelFilterSCocktail.set_text(t("Filters"))
        self.labelAlcoholSCocktail1.set_text(t("Alcohol"))
        self.checkAlcoholicCocktail.set_label(t("Alcoholic"))
        self.checkNonAlcoholicCocktail.set_label(t("Non Alcoholic"))
        self.labelFilterbyIngridient.set_text(t("Filter by ingredient"))
        self.searchCocktailByIngridient.set_placeholder_text(t("Search Ingredient"))
        self.labelSearchRandomCocktail.set_text(t("Search a random cocktail"))
        self.buttonTryNewThings.set_label(t("Let's try new things"))
        self.buttonHomeSIngridient.set_label(t("Home"))
        self.buttonCocktailsSIngrdients.set_label(t("Cocktails"))
        self.searchIngridient.set_placeholder_text(t("Search Ingredient"))
        self.labelRecomendedIngridientesSearch.set_text(t("Recomended Ingredients"))
        self.buttonBackDetailCocktail.set_label(t("Cocktails"))
        self.buttonHomeDetailCocktail.set_label(t("Home"))
        self.buttonIngridientDetailCocktail.set_label(t("Ingredients"))
        self.labelCocktailLook.set_text(t("Cocktail look"))
        self.labelCocktailInstructions.set_text(t("Instructions"))
        self.labelIngridientstomakeit.set_text(t("Ingredients to make it"))
        self.buttonBackDetailIngridient.set_label(t("Ingredients"))
        self.buttonHomeDetailIngridient.set_label(t("Home"))
        self.buttonIngridientDetailIngridient.set_label(t("Cocktails"))
        self.labelIngridientLook.set_text(t("Ingredient look"))
        self.labelIngridientAlcohol.set_text(t("Alcoholic:"))
        self.labelIngridientDescription.set_text(t("Description"))
        self.labelCocktailswhichInclude.set_text(t("Cocktails which include it"))
    #---------------------------------------------------------------------------------------------------------
    #COSAS DE ERRORES
    #---------------------------------------------------------------------------------------------------------
    #boxErrorWebCDDetailIngridient
        self.buttonErrorWebCDBackDetailIngridient = self.builder.get_object("buttonErrorWebCDBackDetailIngridient")
        self.buttonErrorWebCDHomeDetailIngridient = self.builder.get_object("buttonErrorWebCDHomeDetailIngridient")
        self.buttonErrorWebCDIngridientDetailIngridient = self.builder.get_object("buttonErrorWebCDIngridientDetailIngridient")
        self.labelErrorWebIngDNotFound = self.builder.get_object("labelErrorWebIngDNotFound")
        self.buttonErrorWebIngDReload = self.builder.get_object("buttonErrorWebIngDReload")
        #---
        self.buttonErrorWebCDBackDetailIngridient.set_label(t("Cocktails"))
        self.buttonErrorWebCDHomeDetailIngridient.set_label(t("Home"))
        self.buttonErrorWebCDIngridientDetailIngridient.set_label(t("Ingredient"))
        self.labelErrorWebIngDNotFound.set_text(t("Error:No acces to the database"))
        self.buttonErrorWebIngDReload.set_label(t("Reload"))

        #boxErrorWebCDDetailCocktail
        self.buttonErrorWebCDBackDetailCocktail = self.builder.get_object("buttonErrorWebCDBackDetailCocktail")
        self.buttonErrorWebCDHomeDetailCocktail = self.builder.get_object("buttonErrorWebCDHomeDetailCocktail")
        self.buttonErrorWebCDIngridientDetailCocktail = self.builder.get_object("buttonErrorWebCDIngridientDetailCocktail")
        self.labelErrorWebCDNotFound = self.builder.get_object("labelErrorWebCDNotFound")
        self.buttonErrorWebCDReload = self.builder.get_object("buttonErrorWebCDReload")

        self.buttonErrorWebCDBackDetailCocktail.set_label(t("Cocktails"))
        self.buttonErrorWebCDHomeDetailCocktail.set_label(t("Home"))
        self.buttonErrorWebCDIngridientDetailCocktail.set_label(t("Ingredient"))
        self.labelErrorWebCDNotFound.set_text(t("Error:No acces to the database"))
        self.buttonErrorWebCDReload.set_label(t("Reload"))


        #boxWebErrorIngSearchIngridient
        self.buttonWebErrorIngHomeSIngridient = self.builder.get_object("buttonWebErrorIngHomeSIngridient")
        self.buttonWebErrorIngCocktailsSIngrdients = self.builder.get_object("buttonWebErrorIngCocktailsSIngrdients")
        self.searchWebErrorIngIngridient = self.builder.get_object("searchWebErrorIngIngridient")
        self.labelWebErrorIngShowIngridients = self.builder.get_object("labelWebErrorIngShowIngridients")
        self.labelWebErrorIngNotFound = self.builder.get_object("labelWebErrorIngNotFound")
        self.buttonWebErrorIngReload = self.builder.get_object("buttonWebErrorIngReload")

        self.buttonWebErrorIngHomeSIngridient.set_label(t("Home"))
        self.buttonWebErrorIngCocktailsSIngrdients.set_label(t("Ingredients"))
        self.searchWebErrorIngIngridient.set_placeholder_text(t("Search Cocktail"))
        self.labelWebErrorIngShowIngridients.set_text(t("Recomended Ingredients"))
        self.labelWebErrorIngNotFound.set_text(t("Error:No acces to the database"))
        self.buttonWebErrorIngReload.set_label(t("Reload"))

        #boxWebErrorCSearchCocktail
        self.buttonWebErrorCHomeSCocktail = self.builder.get_object("buttonWebErrorCHomeSCocktail")
        self.buttonWebErrorCIngridientsSCocktail = self.builder.get_object("buttonWebErrorCIngridientsSCocktail")
        self.labelWebErrorCFilterSCocktail = self.builder.get_object("labelWebErrorCFilterSCocktail")
        self.searchWebErrorCCocktail = self.builder.get_object("searchWebErrorCCocktail")
        self.labelWebErrorCAlcoholSCocktail = self.builder.get_object("labelWebErrorCAlcoholSCocktail")
        self.labelWebErrorCChooseCocktail = self.builder.get_object("labelWebErrorCChooseCocktail")
        self.checkWebErrorCAlcoholicCocktail = self.builder.get_object("checkWebErrorCAlcoholicCocktail")
        self.checkWebErrorCNonAlcoholicCocktail = self.builder.get_object("checkWebErrorCNonAlcoholicCocktail")
        self.labelWebErrorCNotFound = self.builder.get_object("labelWebErrorCNotFound")
        self.buttonWebErrorCReload = self.builder.get_object("buttonWebErrorCReload")
        self.labelErrorSFilterbyIngridient1 = self.builder.get_object("labelErrorSFilterbyIngridient1")
        self.searchErrorSCocktailByIngridient1 = self.builder.get_object("searchErrorSCocktailByIngridient1")
        self.labelErrorSSearchRandomCocktail1 = self.builder.get_object("labelErrorSSearchRandomCocktail1")
        self.buttonErrorSTryNewThings1 = self.builder.get_object("buttonErrorSTryNewThings1")

        self.buttonWebErrorCHomeSCocktail.set_label(t("Home"))
        self.buttonWebErrorCIngridientsSCocktail.set_label(t("Ingredients"))
        self.labelWebErrorCFilterSCocktail.set_text(t("Filters"))
        self.searchWebErrorCCocktail.set_placeholder_text(t("Search Cocktail"))
        self.labelWebErrorCAlcoholSCocktail.set_text(t("Alcohol")) 
        self.labelWebErrorCChooseCocktail.set_text(t("Recomended cocktails")) 
        self.checkWebErrorCAlcoholicCocktail.set_label(t("Alcoholic")) 
        self.checkWebErrorCNonAlcoholicCocktail.set_label(t("Non Alcoholic")) 
        self.labelWebErrorCNotFound.set_text(t("Error:No acces to the database")) 
        self.buttonWebErrorCReload.set_label(t("Reload")) 
        self.labelErrorSFilterbyIngridient1.set_text(t("Filter by ingredient")) 
        self.searchErrorSCocktailByIngridient1.set_placeholder_text(t("Search Cocktail")) 
        self.labelErrorSSearchRandomCocktail1.set_text(t("Search a random cocktail")) 
        self.buttonErrorSTryNewThings1.set_label(t("Let's try new things")) 



        #boxErrorSSearchIngridient
        self.buttonErrorSIngHomeSIngridient1 = self.builder.get_object("buttonErrorSIngHomeSIngridient1")
        self.buttonErrorSIngCocktailsSIngrdients1 = self.builder.get_object("buttonErrorSIngCocktailsSIngrdients1")
        self.searcErrorSInghIngridient = self.builder.get_object("searcErrorSInghIngridient")
        self.labelErrorSIngShowIngridients = self.builder.get_object("labelErrorSIngShowIngridients")
        self.labelErrorSIngNotFound = self.builder.get_object("labelErrorSIngNotFound")
        self.buttonErrorSIngReload = self.builder.get_object("buttonErrorSIngReload")

        

        self.buttonErrorSIngHomeSIngridient1.set_label(t("Home")) 
        self.buttonErrorSIngCocktailsSIngrdients1.set_label(t("Ingredients")) 
        self.searcErrorSInghIngridient.set_placeholder_text(t("Search Cocktail")) 
        self.labelErrorSIngShowIngridients.set_text(t("Recomended Ingredients")) 
        self.labelErrorSIngNotFound.set_text(t("Error:No ingredients were found")) 
        self.buttonErrorSIngReload.set_label(t("Reload")) 


        #boxErrorSearchCocktail
        self.buttonHomeSCocktail1 = self.builder.get_object("buttonHomeSCocktail1")
        self.buttonIngridientsSCocktail1 = self.builder.get_object("buttonIngridientsSCocktail1")
        self.labelErrorSFilterSCocktail = self.builder.get_object("labelErrorSFilterSCocktail")
        self.searchErrorSCocktail = self.builder.get_object("searchErrorSCocktail")
        self.labelErrorSAlcoholSCocktail = self.builder.get_object("labelErrorSAlcoholSCocktail")
        self.checkErrorSAlcoholicCocktail = self.builder.get_object("checkErrorSAlcoholicCocktail")
        self.checkErrorSNonAlcoholicCocktail = self.builder.get_object("checkErrorSNonAlcoholicCocktail")
        self.labelErrorSChooseCocktail = self.builder.get_object("labelErrorSChooseCocktail")
        self.labelErrorSCNotFound = self.builder.get_object("labelErrorSCNotFound")
        self.buttonErrorSCReload = self.builder.get_object("buttonErrorSCReload")
        self.labelErrorSFilterbyIngridient = self.builder.get_object("labelErrorSFilterbyIngridient")
        self.searchErrorSCocktailByIngridient = self.builder.get_object("searchErrorSCocktailByIngridient")
        self.labelErrorSSearchRandomCocktail = self.builder.get_object("labelErrorSSearchRandomCocktail")
        self.buttonErrorSTryNewThings = self.builder.get_object("buttonErrorSTryNewThings")


        self.buttonHomeSCocktail1.set_label(t("Home")) 
        self.buttonIngridientsSCocktail1.set_label(t("Ingredients")) 
        self.labelErrorSFilterSCocktail.set_text(t("Filters"))
        self.searchErrorSCocktail.set_placeholder_text(t("Search Cocktail"))
        self.labelErrorSAlcoholSCocktail.set_text(t("Alcohol"))
        self.checkErrorSAlcoholicCocktail.set_label(t("Alcoholic")) 
        self.checkErrorSNonAlcoholicCocktail.set_label(t("Non Alcoholic")) 
        self.labelErrorSChooseCocktail.set_text(t("Recomended cocktails"))
        self.labelErrorSCNotFound.set_text(t("Error:No cocktail was found"))
        self.buttonErrorSCReload.set_label(t("Reload")) 
        self.labelErrorSFilterbyIngridient.set_text(t("Filter By Ingredient"))
        self.searchErrorSCocktailByIngridient.set_placeholder_text(t("Search Cocktail"))
        self.labelErrorSSearchRandomCocktail.set_text(t("Search a random cocktail"))
        self.buttonErrorSTryNewThings.set_label(t("Let's try new things")) 





run_on_main_thread = GLib.idle_add


class AppHandler:
    def on_cocktail_clicked() -> None: pass
    def on_ingredient_clicked() -> None: pass
    def on_cocktail_searched(name: str) -> None: pass
    def on_ingredient_searched(name: str) -> None: pass
    def on_cocktail_screen_clicked(name: str) -> None: pass
    def on_ingredient_screen_clicked(name: str) -> None: pass
    def on_random_cocktail_clicked() -> None: pass
    def on_cocktail_by_ingredient(ingredient: str) -> None: pass


class MiAplicacion:
    def __init__(self):
        iniciar(self)
        self.cocktailButtonsConnected = False
        self.ingredientButtonsConnected = False
        self.cocktailButtonsConnectedIng = [False, False, False, False]

    #Metodo para iniciar la aplicación
    def run(self):
        iniciar(self)
        self.window.show_all()
        Gtk.main()


    def setHandler(self, presenter: AppHandler):
        self.presenter = presenter


    #Metodo para administrar las señales
    def adminSignals(self, handler):
        self.builder.connect_signals(handler)


    #Metodos para botones de la barra superior
    def buttonGoCocktails(self, widget):
        self.presenter.on_cocktail_screen_clicked()
        

    def buttonGoIngridients(self, widget):
        self.presenter.on_ingredient_screen_clicked()


    def buttonGoHome(self, widget):
        self.stack.set_visible_child_name("home")


    #Metodos ver coctail en detalle
    def buttonClickedCocktail(self, widget, name):  
        self.cocktailSpinner.start()
        self.cocktailWaitLabel.set_text(t("Fetching cocktail info"))
        self.presenter.on_cocktail_clicked(name)
 

    def buttonRandomCocktail(self, widget):
        self.cocktailSpinner.start()
        self.cocktailWaitLabel.set_text(t("Fetching cocktail info"))
        self.presenter.on_random_cocktail_clicked()


        #Funciones auxiliares
    def getbuttonsSCocktail(self, widget):
        self.buttonSCocktail1 = self.builder.get_object("buttonSCocktail1")
        self.buttonSCocktail2 = self.builder.get_object("buttonSCocktail2")
        self.buttonSCocktail3 = self.builder.get_object("buttonSCocktail3")
        self.buttonSCocktail4 = self.builder.get_object("buttonSCocktail4")
        self.labelSCocktailName1 = self.builder.get_object("labelSCocktailName1")
        self.labelSCocktailName2 = self.builder.get_object("labelSCocktailName2")
        self.labelSCocktailName3 = self.builder.get_object("labelSCocktailName3")
        self.labelSCocktailName4 = self.builder.get_object("labelSCocktailName4")
        self.searchCocktail = self.builder.get_object("searchCocktail")
        self.searchCocktail.set_text("")
        self.searchCocktailByIngridient = self.builder.get_object("searchCocktailByIngridient")
        self.searchCocktailByIngridient.set_text("")



        #Funciones auxiliares
    def getbuttonsSIngridients(self,widget):
        self.buttonSIngridient1 = self.builder.get_object("buttonSIngridient1")
        self.buttonSIngridient2 = self.builder.get_object("buttonSIngridient2")
        self.buttonSIngridient3 = self.builder.get_object("buttonSIngridient3")
        self.buttonSIngridient4 = self.builder.get_object("buttonSIngridient4")
        self.labelSIngridientName1 = self.builder.get_object("labelSIngridientName1")
        self.labelSIngridientName2 = self.builder.get_object("labelSIngridientName2")
        self.labelSIngridientName3 = self.builder.get_object("labelSIngridientName3")
        self.labelSIngridientName4 = self.builder.get_object("labelSIngridientName4")
        self.buttonSIngridient1.show()
        self.buttonSIngridient2.show()
        self.buttonSIngridient3.show()
        self.buttonSIngridient4.show()
        self.labelSIngridientName1.show()
        self.labelSIngridientName2.show()
        self.labelSIngridientName3.show()
        self.labelSIngridientName4.show()
        self.searchIngridient = self.builder.get_object("searchIngridient")
        self.searchIngridient.set_text("")


    def BusquedaCocktail(self, entry):
        name = entry.get_text()
        self.cocktailWaitLabel.set_text(t("Searching cocktails"))
        self.cocktailSpinner.start()
        self.presenter.on_cocktail_searched(name)
        

    #Funciones filtros
    def BusquedaCocktailPorIngrediente(self, entry):
        name = entry.get_text()
        self.cocktailWaitLabel.set_text(t("Searching cocktails"))
        self.cocktailSpinner.start()
        self.presenter.on_cocktail_by_ingredient(name)
       

    def on_checkbox_toggled(self, widget, checkNonAlcoholicCocktail):
        if widget.get_active():
            checkNonAlcoholicCocktail.set_active(False)
            
    def on_checkbox2_toggled(self, widget, checkAlcoholicCocktail):
        if widget.get_active():
            checkAlcoholicCocktail.set_active(False)
            

    def isToggledAlcohol(self):
        return self.checkAlcoholicCocktail.get_active()


    def isToggledNonAlcohol(self):
        return self.checkNonAlcoholicCocktail.get_active()
    

    #Metodos ver ingredientes en detalle
    def buttonClickedIngridient(self, widget, name):
        self.ingredientSpinner.start()
        self.ingredientWaitLabel.set_text(t("Fetching ingredient info"))
        self.presenter.on_ingredient_clicked(name)
        
 
    def BusquedaIngredients(self, entry):
        name = entry.get_text()
        self.ingredientWaitLabel.set_text(t("Searching ingredients"))
        self.ingredientSpinner.start()
        self.presenter.on_ingredient_searched(name)


    def displayCocktails(self, names, images, changeScreen = False):
        self.cocktailSpinner.stop()
        self.cocktailWaitLabel.set_text(t("Recommended cocktails"))
        if changeScreen:
            self.stack.set_visible_child_name("boxSearchCocktail")
            self.checkAlcoholicCocktail.set_active(False)
            self.checkNonAlcoholicCocktail.set_active(False)
        self.getbuttonsSCocktail(self)

        image_widgets = []
        buttons = [self.buttonSCocktail1, self.buttonSCocktail2, self.buttonSCocktail3, self.buttonSCocktail4]
        labels = [self.labelSCocktailName1, self.labelSCocktailName2, self.labelSCocktailName3, self.labelSCocktailName4]
        for i in range (0, 4):
            if i > len(names)-1:
                buttons[i].hide()
                labels[i].hide()
            else:
                buttons[i].show()
                labels[i].show()
                image_widgets.append(mostrar_imagen_desde_url(images[i], 100, 100)) 
                buttons[i].set_image(image_widgets[i])

                #Poner aqui set del texto
                labels[i].set_text(names[i])
                
                #Desconectar función anterior
                if self.cocktailButtonsConnected:
                    buttons[i].disconnect_by_func(self.buttonClickedCocktail)
                
                #Definir funciones sobre botones
                buttons[i].connect('clicked', self.buttonClickedCocktail, labels[i].get_text())
        self.cocktailButtonsConnected = True

    def displayIngredients(self, names, images, changeScreen = False):
        self.ingredientSpinner.stop()
        self.ingredientWaitLabel.set_text(t("Recomended Ingredients"))
        if(changeScreen):
            self.stack.set_visible_child_name("boxSearchIngridient")
            self.checkAlcoholicCocktail.set_active(False)
            self.checkNonAlcoholicCocktail.set_active(False)
        self.getbuttonsSIngridients(self)

        image_widgets = []
        buttons = [self.buttonSIngridient1, self.buttonSIngridient2, self.buttonSIngridient3, self.buttonSIngridient4]
        labels = [self.labelSIngridientName1, self.labelSIngridientName2, self.labelSIngridientName3, self.labelSIngridientName4]
        for i in range (0, 4):
            if i > len(names)-1:
                buttons[i].hide()
                labels[i].hide()
            else:
                buttons[i].show()
                labels[i].show()
                image_widgets.append(mostrar_imagen_desde_url(images[i], 100, 100)) 
                buttons[i].set_image(image_widgets[i])

                #Poner aqui set del texto
                labels[i].set_text(names[i])

                if self.ingredientButtonsConnected:
                    buttons[i].disconnect_by_func(self.buttonClickedIngridient)
                
                #Definir funciones sobre botones
                buttons[i].connect('clicked', self.buttonClickedIngridient, names[i])
        self.ingredientButtonsConnected = True


    def displayCocktailInfo(self, info):
        self.cocktailSpinner.stop()
        self.stack.set_visible_child_name("boxDetailCocktail")
        self.labelCocktailName = self.builder.get_object("labelCocktailName")
        self.labelCocktailName.set_text(info[0])
        self.imageCocktailLook = self.builder.get_object("imageCocktailLook")
        picture = mostrar_imagen_desde_url(info[1], 300, 350)
        pixbuf = picture.get_pixbuf()
        self.imageCocktailLook.set_from_pixbuf(pixbuf)
        #Formateo de texto de instrucciones
        self.labelCocktailInstruction = self.builder.get_object("labelCocktailInstruction")
        self.labelCocktailInstruction.set_line_wrap(True)
        self.labelCocktailInstruction.set_text(info[2])
        #Formateo de texto de ingredientes
        self.labelCocktailIngridients = self.builder.get_object("labelCocktailIngridients")
        ingredientes = info[3]
        Measures = info [4]
        self.labelCocktailIngridients.set_text("")
        for i in range (0, len(ingredientes) -1):
            self.labelCocktailIngridients.set_text(self.labelCocktailIngridients.get_text() + f" - {ingredientes[i]}" + t("(Measure:") + f"{Measures[i]})\n")

    
    def displayIngredientInfo(self, info, cnames, cimages):
        self.ingredientSpinner.stop()
        self.stack.set_visible_child_name("boxDetailIngridient")
        self.imageIngridientLook = self.builder.get_object("imageIngridientLook")
        imagen_pocha = mostrar_imagen_desde_url(info[1], 150, 200)
        pixbuf = imagen_pocha.get_pixbuf()
        self.imageIngridientLook.set_from_pixbuf(pixbuf)
        #Formateo de texto de instrucciones
        self.labelIngredientDescription = self.builder.get_object("labelIngredientDescription")
        self.labelIngredientDescription.set_line_wrap(True)
        self.labelIngredientDescription.set_text(info[2])
        self.labelIngridientAlcohol = self.builder.get_object("labelIngridientAlcohol")
        self.labelIngridientAlcohol.set_text(t("Alcohol:") + f"{info[3]}")
        if ((info[3] == "Yes") & (info[4] != "None%")):
            self.labelIngridientABV = self.builder.get_object("labelIngridientABV")
            self.labelIngridientABV.show()
            self.labelIngridientABV.set_text(t("How much ->") + f" {info[4]}")   
        else:
            self.labelIngridientABV = self.builder.get_object("labelIngridientABV") 
            self.labelIngridientABV.hide()
              
         #Botones de ingredientes
        
        self.buttonCocktail1IngridientDetails = self.builder.get_object("buttonCocktail1IngridientDetails")
        self.buttonCocktail2IngridientDetails = self.builder.get_object("buttonCocktail2IngridientDetails")
        self.buttonCocktail3IngridientDetails = self.builder.get_object("buttonCocktail3IngridientDetails")
        self.buttonCocktail4IngridientDetails = self.builder.get_object("buttonCocktail4IngridientDetails")
        self.labelCocktail1IngridientDetails = self.builder.get_object("labelCocktail1IngridientDetails")
        self.labelCocktail2IngridientDetails = self.builder.get_object("labelCocktail2IngridientDetails")
        self.labelCocktail3IngridientDetails = self.builder.get_object("labelCocktail3IngridientDetails")
        self.labelCocktail4IngridientDetails = self.builder.get_object("labelCocktail4IngridientDetails")
        self.buttonCocktail1IngridientDetails.show()
        self.buttonCocktail2IngridientDetails.show()
        self.buttonCocktail3IngridientDetails.show()
        self.buttonCocktail4IngridientDetails.show()
        self.labelCocktail1IngridientDetails.show()
        self.labelCocktail2IngridientDetails.show()
        self.labelCocktail3IngridientDetails.show()
        self.labelCocktail4IngridientDetails.show()   
        #Poner aqui set de las fotos
        image_widgets = []
        buttons = [self.buttonCocktail1IngridientDetails, self.buttonCocktail2IngridientDetails, self.buttonCocktail3IngridientDetails, self.buttonCocktail4IngridientDetails]
        labels = [self.labelCocktail1IngridientDetails, self.labelCocktail2IngridientDetails, self.labelCocktail3IngridientDetails, self.labelCocktail4IngridientDetails]
        for i in range (0, 4):
            if i > len(cnames)-1:
                buttons[i].hide()
                labels[i].hide()
            else:
                buttons[i].show()
                labels[i].show()
                image_widgets.append(mostrar_imagen_desde_url(cimages[i], 100, 100)) 
                buttons[i].set_image(image_widgets[i])

                #Poner aqui set del texto
                labels[i].set_text(cnames[i])
                
                if self.cocktailButtonsConnectedIng[i]:
                    buttons[i].disconnect_by_func(self.buttonClickedCocktail)                

                #Definir funciones sobre botones
                buttons[i].connect('clicked', self.buttonClickedCocktail, cnames[i])
                self.cocktailButtonsConnectedIng[i] = True


    def cocktailSearchError(self):
        self.cocktailSpinner.stop()
        self.stack.set_visible_child_name("boxErrorSearchCocktail")
        self.checkAlcoholicCocktail.set_active(False)
        self.checkNonAlcoholicCocktail.set_active(False)
        self.searchCocktail.set_text("")
        self.searchCocktailByIngridient.set_text("")
        self.buttonErrorSCReload.connect('clicked', self.buttonGoCocktails)


    def cocktailDBError(self):
        self.cocktailSpinner.stop()
        self.stack.set_visible_child_name("boxWebErrorCSearchCocktail")
        self.checkAlcoholicCocktail.set_active(False)
        self.checkNonAlcoholicCocktail.set_active(False)
        self.searchCocktail.set_text("")
        self.searchCocktailByIngridient.set_text("")
        self.buttonWebErrorCReload.connect('clicked', self.buttonGoCocktails)

    
    def ingredientSearchError(self):
        self.stack.set_visible_child_name("boxErrorSSearchIngridient")
        self.searchIngridient.set_text("")
        self.buttonErrorSIngReload.connect('clicked', self.buttonGoIngridients)


    def ingredientDBError(self):
        self.stack.set_visible_child_name("boxWebErrorIngSearchIngridient")
        self.searchIngridient.set_text("")
        self.buttonWebErrorIngReload.connect('clicked', self.buttonGoIngridients)

    def cocktailFetchError(self, name):
        self.stack.set_visible_child_name("boxErrorWebCDDetailCocktail")
        if name == None:
            self.buttonErrorWebCDReload.connect('clicked', self.buttonRandomCocktail)
        else:
            self.buttonErrorWebCDReload.connect('clicked', self.buttonClickedCocktail, name)

    
    def ingredientFetchError(self, name):
        self.stack.set_visible_child_name("boxErrorWebCDDetailIngridient")
        self.buttonErrorWebIngDReload.connect('clicked', self.buttonClickedIngridient, name)



def mostrar_imagen_desde_url(url, ancho, alto):
    # Descargar la imagen desde la URL
    response = requests.get(url)
    if response.status_code != 200:
        return

    imagen_bytes = BytesIO(response.content)

    # Obtener la longitud de los datos descargados
    imagen_bytes_len = imagen_bytes.getbuffer().nbytes

    # Convertir BytesIO a InputStream
    imagen_input_stream = Gio.MemoryInputStream.new_from_data(imagen_bytes.read(), None)

    # Cargar la imagen desde InputStream
    pixbuf = GdkPixbuf.Pixbuf.new_from_stream(imagen_input_stream, None)
    if ancho and alto:
        pixbuf = pixbuf.scale_simple(ancho, alto, GdkPixbuf.InterpType.BILINEAR)
    # Crear un widget de imagen
    imagen = Gtk.Image.new_from_pixbuf(pixbuf)
    return imagen
