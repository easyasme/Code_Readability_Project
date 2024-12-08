#!/bin/python3

from p5 import *
from random import randint


def verdrietig(x_midden, y_oog, y_mond):
    ellipse(x_midden - 50, y_oog - 20, 60, 50) # x, y, breedte, hoogte
    ellipse(x_midden + 50, y_oog - 20, 60, 50)
    ellipse(x_midden, y_mond + 30, 100, 65)


def blij(x_midden, y_oog, y_mond):
    ellipse(x_midden - 50, y_oog + 20, 60, 50) # x, y, breedte, hoogte
    ellipse(x_midden + 50, y_oog + 20, 60, 50)
    ellipse(x_midden, y_mond - 30, 100, 65)


def setup():
    # Zet de code om eenmalig uit te voeren hier onder
    size(400, 400) # breedte en hoogte
    background(0, 0, 0) # verplaats onder draw() om de tekening voor elk frame opnieuw in te stellen
    rect_mode(CENTER)
    no_stroke()


def draw():
    # Zet hier code om bij elk frame uit te voeren
    masker_breedte = width / 2
    x_midden = width / 2
    y_oog = 180
    y_mond = 255
    # teken het masker
    fill(255, 255, 255) # wit
    rect(200, 150, masker_breedte, masker_breedte)
    ellipse(x_midden, 250, masker_breedte, 140)
    # ogen en mond
    fill(0) # zwart
    ellipse(x_midden - 50, y_oog, 60, 50) # x, y, breedte, hoogte
    ellipse(x_midden + 50, y_oog, 60, 50)
    ellipse(x_midden, y_mond, 100, 75)
    # bedek ogen en mond gedeeltelijk
    fill(255)
    if mouse_x > x_midden:
        blij(x_midden, y_oog, y_mond)
    else:
        verdrietig(x_midden, y_oog, y_mond)
    # bedek de bovenkant van het masker
    fill(0)
    ellipse(x_midden, 60, 250, 90)
    # verduister de helft van het masker
    fill(0, 25)
    rect(300, 200, width/2, height)


def mouse_pressed():
    # Zet code hier die moet worden uitgevoerd wanneer de muis wordt ingedrukt
    print(mouse_x, mouse_y)


# Bewaar dit om je code uit te voeren
run()
