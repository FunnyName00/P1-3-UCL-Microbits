from microbit import *
import radio
import random
import music
import utime 

#Can be used to filter the communication, only the ones with the same parameters will receive messages
radio.config(group=17, channel=67, address=0x472171164, power= 7)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)

#Initialisation des variables du micro:bit
radio.on()
connexion_established = False
key = "gbtfv"
session_key = ""
connexion_key = None
nonce_list = []
baby_state = 0
set_volume(100)
heurs_debut = None
heurs_fin = None
temps_total_sommeil = 0
suivi_en_cours = False
message_number = 0
history_use = 0
""" 
           *** Fonctions de bases ***
    --------------------------------------------
"""

def hashing(string):
	"""
	Hachage d'une chaîne de caractères fournie en paramètre.
	Le résultat est une chaîne de caractères.
	Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.

	:param (str) string: la chaîne de caractères à hacher
	:return (str): le résultat du hachage
	"""
	def to_32(value):
		"""
		Fonction interne utilisée par hashing.
		Convertit une valeur en un entier signé de 32 bits.
		Si 'value' est un entier plus grand que 2 ** 31, il sera tronqué.

		:param (int) value: valeur du caractère transformé par la valeur de hachage de cette itération
		:return (int): entier signé de 32 bits représentant 'value'
		"""
		value = value % (2 ** 32)
		if value >= 2**31:
			value = value - 2 ** 32
		value = int(value)
		return value

	if string:
		x = ord(string[0]) << 7
		m = 1000003
		for c in string:
			x = to_32((x*m) ^ ord(c))
		x ^= len(string)
		if x == -1:
			x = -2
		return str(x)
	return ""

def vigenere(message, key, decryption=False):
    text = ""
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        #Letters encryption/decryption
        if char.isalpha():
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else : 
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            #Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        #Digits encryption/decryption
        elif char.isdigit():
            key_index = i % key_length
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:  
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text


def binary_search(list, search):
    list.sort()
    start = 0
    end = len(list) - 1

    while start <= end:
        mid = (start + end) // 2
        valeur_mid = list[mid]

        if valeur_mid == search:
            return True  
        elif valeur_mid < search:
            start = mid + 1  
        else:
            end = mid - 1  

    return False  
    
def send_packet(key, type, content):
    """
    Envoi de données fournies en paramètres
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit

    :param (str) key:       Clé de chiffrement
           (str) type:      Type du paquet à envoyer
           (str) content:   Données à envoyer
	:return none
    """
    global message_number
    random.seed(message_number)
    
    # Génération unique du nonce
    nonce = random.randint(1, 10000)
    while nonce in nonce_list:
        nonce = random.randint(1, 10000)

    nonce_list.append(str(nonce))

    
    #print("nonce",nonce)
    
    message = str(nonce) + str(":") + str(content)
    
    #print("message non crypté :",message)
    crypted_message = str(vigenere(message, key))
    send = str(type)+ "|" +str(len(crypted_message))+ "|"+ str(crypted_message)
    
    
    #print("nonce liste ", nonce_list)
    
    radio.send(send)  
    message_number +=1
    
#Unpack the packet, check the validity and return the type, length and content
def unpack_data(encrypted_packet, key):
    """
    Déballe et déchiffre les paquets reçus via l'interface radio du micro:bit
    Cette fonction renvoit les différents champs du message passé en paramètre

    :param (str) encrypted_packet: Paquet reçu
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)length:           Longueur de la donnée en caractères
            (str) message:         Données reçue
    """
    encrypted_packet = encrypted_packet.split("|")
    type = encrypted_packet[0]
    length = int(encrypted_packet[1])
    message = vigenere(encrypted_packet[2],key, True)
    
    return type, length, message
    
def receive_packet(key):
    """
    Traite les paquets reçus via l'interface radio du micro:bit
    Cette fonction utilise la fonction unpack_data pour renvoyer les différents champs du message passé en paramètre
    Si une erreur survient, les 3 champs sont retournés vides

    :param (str) packet_received: Paquet reçue
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)lenght:           Longueur de la donnée en caractère
            (str) message:         Données reçue
    """
    while True:
        whole_crypted_message = radio.receive()
        if whole_crypted_message:
            break

    message = unpack_data(whole_crypted_message, key)
    type= message[0]
    content_and_nonce = message[2].split(":")
    nonce = content_and_nonce[0]
    content = content_and_nonce[1]

    #print("message reçu :", message)
    if nonce in nonce_list:
        #print("Nonce déjà utilisé, paquet rejeté.")
        return ["", "", ""]

    nonce_list.append(nonce)
    length = len(content)
    #print("nonce liste ", nonce_list)
    return [type, length, content]

         
#Calculate the challenge response
def calculate_challenge_response(challenge):
    """
    Calcule la réponse au challenge initial de connection envoyé par l'autre micro:bit

    :param (str) challenge:            Challenge reçu
	:return (srt)challenge_response:   Réponse au challenge
    """
    random.seed(challenge)
    challenge_answer = hashing(str(random.random()))
    #print("réponse au challenge :",challenge_answer)
    return challenge_answer

#Respond to a connexion request by sending the hash value of the number received
def respond_to_connexion_request(challenge, key):
    """
    Réponse au challenge initial de connection avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                   Clé de chiffrement
	:return (srt) challenge_response:   Réponse au challenge
    """
    global session_key, connexion_established
    send_packet(key, "0x01", calculate_challenge_response(challenge))     #message de connexion établie
    session_key = str(calculate_challenge_response(challenge)) + key
    
    connexion_established = True
    #print("connexion établie :",connexion_established)
    display.show(Image.HAPPY)
    return True
    #print("Session key :", session_key)      


def securise_connexion():
    message1 = receive_packet(key)
    #print("message reçu :",message1)
    type = message1[0]
    length = message1[1]
    content = int(message1[2])
    
    if type == "0x01" :
        if respond_to_connexion_request(content, key) == True:
            return True
        else: return False
        
    
        

""" 
           *** Fonctions spécifiques ***
    --------------------------------------------
"""


def lait():
    send_packet(session_key, "lait", 'start')
    
    qttlait = 0
    display.show(qttlait)
    
    while True:
        
        if button_a.was_pressed() and button_b.was_pressed():
            qttlait =0
            display.show(qttlait)
            send_packet(session_key, "lait", str(qttlait))

        if button_b.was_pressed():
            
            qttlait+=1
            
            display.show(qttlait)
            send_packet(session_key, "lait", str(qttlait))
            
        if button_a.was_pressed():
            if qttlait >0:
                qttlait-=1
            display.show(qttlait)
            send_packet(session_key, "lait", str(qttlait))
            
        if pin_logo.is_touched():
            send_packet(session_key, "lait", 'quit')
            sleep(500)
            break
            
    return
    

def afficher_etat_eveil():
    send_packet(session_key, 'info', 'demande')
    fonction = 0
    while True:
        
        if pin_logo.is_touched():
            send_packet(session_key, 'info', 'quit')
            sleep(600)
            break

        if button_a.was_pressed():
            play_music()
            
        if button_b.was_pressed():
            fonction += 1
            
        if fonction == 0:
            send_packet(session_key, 'info', 'mvt') 
            mes = receive_packet(session_key)#get message radio   
              
            mvt = float(mes[2])  #stockage du contenu de message (en float) dans mvt
    
            if mvt < 200: 
                display.show(Image.ASLEEP) #img pour indiquer que le bébé est endormi  
            elif 200 <= mvt < 600:
                display.show(Image.CONFUSED) #img pour indiquer que le bébé est agité  
            else:
                display.show(Image.ANGRY)
                play_music()#img pour indiquer que le bébé est très agité

            if pin_logo.is_touched():
                send_packet(session_key, 'info', 'quit')
                sleep(600)
                break

        if fonction == 1:
            send_packet(session_key, 'info', 'temp')
            mes = receive_packet(session_key)
            if int(mes[2]) <= 35:
                display.show(Image('09990:'
		                   '90909:'
		                   '99999:'
		                   '09990:'
		                   '09990')) #crane
            else :
                display.scroll(mes[2])
            
            if pin_logo.is_touched():
                send_packet(session_key, 'info', 'quit')
                sleep(600)
                break
            
        if fonction == 2:
            send_packet(session_key, 'info', 'lum')
            mes = receive_packet(session_key)
            
            if pin_logo.is_touched():
                send_packet(session_key, 'info', 'quit')
                sleep(600)
                break
                
            if mes[2] == 'sun':
                display.show(Image('60606:'
                               '08980:'
                               '69996:'
                               '08980:'
                               '60606'))
                sleep(1000)
                
            elif mes[2] == 'moon':
                display.show(Image('07886:'
                               '79900:'
                               '99000:'
                               '79900:'
                               '07886'))
                sleep(1000)
                
        if fonction == 3:
            
            if pin_logo.is_touched():
                send_packet(session_key, 'info', 'quit')
                sleep(600)
                break
            send_packet(session_key, 'info', 'son')

            graph5 = Image("99999:"
                   "99999:"
                   "99999:"
                   "99999:"
                   "99999")
    
            graph4 = Image("44444:"
                   "99999:"
                   "99999:"
                   "99999:"
                   "99999")
    
            graph3 = Image("00000:"
                   "55555:"
                   "99999:"
                   "99999:"
                   "99999")
    
            graph2 = Image("00000:"
                   "00000:"
                   "55555:"
                   "99999:"
                   "99999")
    
            graph1 = Image("00000:"
                   "00000:"
                   "00000:"
                   "55555:"
                   "99999")
    
            graph0 = Image("00000:"
                   "00000:"
                   "00000:"
                   "00000:"
                   "00000")
    
            allGraphs = [graph0, graph1, graph2, graph3, graph4, graph5]
            mes = receive_packet(session_key)
            soundLevel = int(mes[2])
            display.show(allGraphs[soundLevel])

        if fonction > 3:
            fonction = 0
    return 


def calculer_temps_de_sommeil(etat):
    global heurs_debut, temps_total_sommeil, suivi_en_cours
    
    if etat == 'endormi' and not suivi_en_cours:
        heurs_debut = utime.ticks_ms()
        suivi_en_cours = True
        display.scroll("Start")
        
    elif etat == 'endormi' and suivi_en_cours and heurs_debut is not None:
        
        heures_fin = utime.ticks_ms()
        temps_passe = utime.ticks_diff(heures_fin, heurs_debut) // 1000
        temps_total_sommeil += temps_passe

        hours = temps_total_sommeil // 3600
        minutes = (temps_total_sommeil % 3600) // 60
        seconds = temps_total_sommeil % 60
        
        display.scroll("Duree: {:02}:{:02}:{:02}".format(hours, minutes, seconds))
        
    elif etat != 'endormi' and suivi_en_cours and heurs_debut is not None:
        heures_fin = utime.ticks_ms()
        temps_passe = utime.ticks_diff(heures_fin, heurs_debut) // 1000
        temps_total_sommeil += temps_passe
        heurs_debut = None
        suivi_en_cours = False
        
        hours = temps_total_sommeil // 3600
        minutes = (temps_total_sommeil % 3600) // 60
        seconds = temps_total_sommeil % 60
        
        display.scroll("Total: {:02}:{:02}:{:02}".format(hours, minutes, seconds))


def confirmation():
    display.show("?")
    while not pin_logo.is_touched():  # Attendre que le logo soit touché
        sleep(100)
    display.show(Image.HEART)
    sleep(400)


def play_music():
    #print("musique envoyée")
    send_packet(session_key, "music", "music")

def historique():
    global history_use
    history_use = 0
    
    while True:
        display.show(Image('07970:'
	                   '70907:'
	                   '79907:'
	                   '70007:'
	                   '07770'))
        
        if pin_logo.is_touched():
            sleep(600)
            break  # Sortie de la boucle si le logo est touché
        
        if button_a.is_pressed():
            if history_use == 0:
                calculer_temps_de_sommeil('endormi')
                history_use += 1
                print("history use :", history_use)
                utime.sleep_ms(300)  # Débounce pour éviter plusieurs détections rapides
            else:
                calculer_temps_de_sommeil('endormi')
                history_use += 1
                print("history use :", history_use)
                utime.sleep_ms(300)  # Débounce pour éviter des répétitions

        if button_b.is_pressed():
            calculer_temps_de_sommeil('reveil')
            history_use = 0
            utime.sleep_ms(300)  # Débounce

            
def loading():
    display.show(Image.CLOCK12)
    sleep(300)
    display.show(Image.CLOCK3)
    sleep(300)
    display.show(Image.CLOCK6)
    sleep(300)
    display.show(Image.CLOCK9)
    sleep(300)
    display.show(Image.CLOCK12)
    sleep(300)
    


        
# Boucle principale
while True:
    display.show("P")
    if pin_logo.is_touched():
        loading()
        if securise_connexion() == True:
            sleep(1000)    
            while True:
                display.show("P")
                sleep (600)    
                if button_a.was_pressed():  # Option 1 : Dodo
                    display.scroll("Dodo")
                    confirmation()  # Confirmation avec le logo
                    afficher_etat_eveil()
                        
                
                elif button_b.is_pressed():  # Option 2 : Lait
                    display.scroll("Lait")
                    confirmation()  # Confirmation avec le logo
                    lait()
                
                elif pin_logo.is_touched():  # Option 3 : Histo sommeil
                    display.scroll("Duree")
                    confirmation()  # Confirmation avec le logo
                    historique()

        
            
