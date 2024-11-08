# Imports go at the top
from microbit import *
import music



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
            

        

# Code in a 'while True:' loop repeats forever
while True:
    fonction = 0
    if button_a.was_pressed():
        display.show(Image.ANGRY)

    if button_b.was_pressed():
        display.show(Image.HEART)

    if pin_logo.is_touched():
        lait()
        
