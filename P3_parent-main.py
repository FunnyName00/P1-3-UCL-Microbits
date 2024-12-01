from microbit import *
import radio
import random
import music

#Can be used to filter the communication, only the ones with the same parameters will receive messages
radio.config(group=17, channel=67, address=0x472171164)
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
    nonce = int(random.randint(1,1000))
    
    #while binary_search(nonce_list, nonce) != False:
    #    nonce = int(random.randint(1,1000))
    
    
    message = str(nonce) + str(":") + str(content)
    
    #print("message non crypté :",message)
    crypted_message = str(vigenere(message, key))
    send = str(type)+ "|" +str(len(crypted_message))+ "|"+ str(crypted_message)
    #print("message envoyé :",send)
    radio.send(send)    
    
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
    #print("message reçu :",whole_crypted_message)
    
    message = unpack_data(whole_crypted_message, key)
    type = message[0]
    content_and_nonce = message[2].split(":")
    nonce = content_and_nonce[0]
    content = content_and_nonce[1]
    if binary_search(nonce_list, nonce) == True:
        print("attaque de hacker")
        type = ""
        length = ""
        content = ""
        
    else :
        nonce_list.append(nonce)
        length = len(content)
        
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
    print("connexion établie :",connexion_established)
    display.show(Image.HAPPY)
    #print("Session key :", session_key)      

def securise_connexion():
    message1 = receive_packet(key)
    #print("message reçu :",message1)
    type = message1[0]
    length = message1[1]
    content = int(message1[2])
    
    if type == "0x01" :
        respond_to_connexion_request(content, key)
        
        
        




securise_connexion()
