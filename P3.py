# Imports go at the top
from microbit import *
import music
import math
# var pour identifier le rôle 
role = "parent"

def lait():
    qttlait = 0
    display.show(qttlait)
    while not pin_logo.is_touched():
        
        if button_a.was_pressed() and button_b.was_pressed():
            qttlait =0
            display.show(qttlait)
        

        if button_b.was_pressed():
            if qttlait <10:
                qttlait+=1
            
            display.show(qttlait)
            
        if button_a.was_pressed():
            if qttlait >0:
                qttlait-=1
            display.show(qttlait)
            
    return
            

def afficher_role():
    if role == "parent":
        display.show(Image.HOUSE)
    else:
        display.show(Image.COW) #Image pour l'enfant (j'ai pas trouvé une image d'un bébé xD)


def afficher_etat_eveil():
    while True:
        x = accelerometer.get_x()
        y = accelerometer.get_y()
        z = accelerometer.get_z()

    # calcul de l'intesité de mouvement avec la norme euclidenne
        mvt = abs((x**2 + y**2 + z**2) ** 0.5 - 1024)

        if mvt < 200: 
            display.show(Image.ASLEEP) #img pour indiquer que le bébé est endormi  
        elif 200 <= mvt < 600:
            display.show(Image.CONFUSED) #img pour indiquer que le bébé est agité  
        else:
            display.show(Image.ANGRY) #img pour indiquer que le bébé est très agité 
        
def jouer_la_musique():
    musiques = [music.BA_DING, music.PRELUDE, music.NYAN, music.BIRTHDAY]
    for musique in musiques:
        music.play(music.musique)
        sleep(500)

        

# Code in a 'while True:' loop repeats forever
while True:
    fonction = 0
    if button_a.was_pressed():
        display.show(Image.ANGRY)

    if button_b.was_pressed():
        display.show(Image.HEART)

    if pin_logo.is_touched():
        lait()
        
