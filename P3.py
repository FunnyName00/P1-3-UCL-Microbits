# Imports go at the top
from microbit import *
import music
import math
import radio

radio.on()
radio.config(channel=67, address=0x472171164, group=17)
# var pour identifier le rôle 
role = "parent"

def lait():
    qttlait = 0
    display.show(qttlait)
    while True:
        
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

        if pin_logo.is_touched():
            sleep(500)
            break
            
    return
            

def afficher_role():
    if role == "parent":
        display.show(Image.HOUSE)
    else:
        display.show(Image.COW) #Image pour l'enfant (j'ai pas trouvé une image d'un bébé xD)

def capter_radio():
    mes = str(radio.receive())  #message radio stocké dans un string
    message = mes.split("|")  #création d'une liste [type],[nombre de car],[message]
    sleep(50)
    return message

def afficher_etat_eveil():
    while True:
        # calcul de l'intesité de mouvement avec la norme euclidenne
        mes = capter_radio() #get message radio
        if mes[0] == "1":   #check si type du message = 1
            mvt = float(mes[2])  #stockage du contenu de message (en float) dans mvt

            if mvt < 200: 
                display.show(Image.ASLEEP) #img pour indiquer que le bébé est endormi  
            elif 200 <= mvt < 600:
                display.show(Image.CONFUSED) #img pour indiquer que le bébé est agité  
            else:
                display.show(Image.ANGRY) #img pour indiquer que le bébé est très agité
        if pin_logo.is_touched():
            sleep(600)
            break

    return 
def jouer_la_musique():
    musiques = [music.BA_DING, music.PRELUDE, music.NYAN, music.BIRTHDAY]
    for musique in musiques:
        music.play(musique)
        sleep(500)

        

# Code in a 'while True:' loop repeats forever
while True:
    fonction = 0
    display.show(Image.BUTTERFLY)
    if button_a.was_pressed():
        jouer_la_musique()

    if button_b.was_pressed():
        afficher_etat_eveil()

    if pin_logo.is_touched():
        sleep(500)
        lait()
        
def interface():
        if button_a.was_pressed():
            display.scroll('musique')
            if pin_logo.is_touched():
                jouer_la_musique()#fait fonction 1 (joue de la musique)
            
        if button_b.was_pressed():
            display.scroll('lait')
            if pin_logo.is_touched():
                conso_lait()#fait fonction 2 (consommation de lait)
            
        if button_a.was_pressed() and button_b.was_pressed():
            display.show(Image.ASLEEP)
            sleep(400)
            #display.scroll('historique')
            if pin_logo.is_touched():
                histo_som #fait fonction 3 (historique de sommeil)
            
        press_count = 0
#tjr pr interface mais pas fini
while True:
    if button_a.was_pressed():
        press_count += 1
         
        
        if press_count == 2:
            display.show(Image.HAPPY)
            sleep(1000)  
            display.clear()
            press_count = 0  
