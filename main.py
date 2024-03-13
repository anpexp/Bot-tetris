import keyboard
import cv2
import numpy as np
import pyautogui

#Hay que hacer una fila para las fichas (first in, firt out)y el hold es un comodin, se hace escaneo únicamente de la ultima ficha de la fila de próximas
#Es más eficiente hacer los cálculos con cuantas fichas?
#Reducir el problema a llenar huecos?

class jugador:
    def __init__ (self, hold, line, map):
        self.line = self.getline()
        self.hold = "" #Las fichas se pueden definir por letras (l,j,i,o,s,z,t)

    
    def getline():
        #Hay que comparar las piezas con el color de cada una, comparar imagen es lento, las piezas siempre tienen el mismo color y forma
    #Como search pero para todas las fichas en la fila
        return []


    def capture_screen():
        #captura la pantalla para analizarla después
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def search():
    #Aquí realiza la busqueda de la última ficha agregada


keyboard.press_and_release('alt+tab')