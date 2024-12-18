# Imports go at the top
from microbit import *
import music
import math
import radio
import utime 


radio.on()
radio.config(channel=67, address=0x472171164, group=17)
# var pour identifier le rôle 
role = "parent"
heurs_debut = None
heurs_fin = None

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
        display.show(Image("09999:"
                           "09009:"
                           "09999:"
                           "09000:"
                           "09000")) #Image pour le parent = P
    else:
        display.show(Image.("09999:"
                           "09000:"
                           "09990:"
                           "09000:"
                           "09999")) #Image pour l'enfant = E

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

def calculer_temps_de_sommeil(etat):
    global heurs_debut, heurs_fin
    if etat == 'endormi' and heurs_debut is None:
        heurs_debut = utime.ticks_ms()
        display.scroll("Start")
    elif etat != 'endormi' and heurs_debut is not None:
        heurs_fin = utime.ticks_ms()
        temps_passe = utime.ticks_diff(heurs_fin, heurs_debut) // 1000
        hours = temps_passe // 3600
        min = (temps_passe % 3600) // 60
        sec = temps_passe % 60
        heurs_debut = None
        display.scroll("Duree: {:02}:{:02}:{:02}".format(hours, min, sec))

        

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
        
def confirmation():
    display.scroll("Confirmer ?")
    while not pin_logo.is_touched():  # Attendre que le logo soit touché
        sleep(100)
    display.show(Image.HEART)
    sleep(400)

# Boucle principale
while True:
    if button_a.is_pressed():  # Option 1 : Musique
        display.scroll("Music")
        confirmation()  # Confirmation avec le logo
        jouer_la_musique()

    elif button_b.is_pressed():  # Option 2 : Lait
        display.scroll("Lait")
        confirmation()  # Confirmation avec le logo
        lait()

    elif button_a.is_pressed() and button_b.is_pressed():  # Option 3 : Histo sommeil
        display.show(Image.ASLEEP)
        sleep(400)
        confirmation()  # Confirmation avec le logo
        calculer_temps_de_sommeil()
    
   
            
        press_count = 0
#tjr pr interface mais pas fini
while True:
    if button_a.was_pressed():
        press_count += 1
         
        
        if press_count == 2:
            display.show(Image.HAPPY)  #en attendant fct correspondante
            sleep(1000)  
            display.clear()
            press_count = 0  
