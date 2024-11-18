import keyboard
import time
import numpy as np
import math
from PIL import ImageGrab
from TetrisTablero import TetrisTablero


#Las coordenadas comienzan a contarse a partir de la esquina superior izquierda de la pantalla
x1_tablero, y1_tablero  = 786,222 #Esquina superior izquierda
x2_tablero, y2_tablero = 1081,806 #Esquina inferior derecha

x1, y1 = 1180,281 #Ficha más alta, la primera pieza en caer
x5, y5 = 1178,657 #La última ficha en aparecer
x2, y2 = (x1+x5)//2, y1+math.floor(((y5-y1)/4)*1)
x3, y3 = (x1+x5)//2, y1+math.floor(((y5-y1)/4)*2)
x4, y4 = (x1+x5)//2, y1+math.floor(((y5-y1)/4)*3)

pixel_area = (y5 - y1)//10
print("Inicializado")

pixel_area = 30 # Número de pixeles para verificar el color

#parámetros
rotar_horario = 'x' 
rotar_180 = 'a'
rotar_antihorario = 'z'
mov_izquierda = 'left'
mov_derecha = 'right'
soltar = 'space'
# constantes - ARR 0ms - DAS 40ms

presicion_cal = 3 # Número de movimientos para mantener a cada profundidad (es más preciso pero más lento con más)
profun_max = 3 # número de movimientos a simular en el futuro
retraso_refresco = 0.04 # tiempo de espera, no se puede reducir porque el tablero no alcanza a refrescarse
scan_tablero = True # Escanear el tablero


retraso = 0 #Por si está llendo demasiado rápido

# Colors for tetrio
colores = [
    (194, 64, 70),  # red - Z
    (142, 191, 61),  # lime - Z2
    (93, 76, 176), # dark blue - L2
    (192, 168, 64),  # yellow - O
    (62, 191, 144),  # turquoise - I
    (194, 115, 68), # orange - L
    (176, 75, 166), # purple - T
]

# Todas las piezas se representan en un arreglo
# 4x4 están representadas con 0s, es igual
tetris_piezas = {
    'I': [
        np.array([[1, 1, 1, 1]]),
        np.array([[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]])
    ],
    'O': [
        np.array([[0, 1, 1, 0], [0, 1, 1, 0]])
    ],
    'T': [
        np.array([[1, 1, 1, 0], [0, 1, 0, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0]]),
        np.array([[0, 1, 0, 0], [1, 1, 1, 0]]),
        np.array([[0, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0]]),
    ],
    'L': [
        np.array([[1, 1, 1, 0], [0, 0, 1, 0]]),
        np.array([[0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0]]),
        np.array([[1, 0, 0, 0], [1, 1, 1, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0]]),
    ],
    'L2': [
        np.array([[1, 1, 1, 0], [1, 0, 0, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0]]),
        np.array([[0, 0, 1, 0], [1, 1, 1, 0]]),
        np.array([[1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0]]),
    ],
    'Z': [
        np.array([[0, 1, 1, 0], [1, 1, 0, 0]]),
        np.array([[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0]])
    ],
    'Z2': [
        np.array([[1, 1, 0, 0], [0, 1, 1, 0]]),
        np.array([[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0]])
    ]
}


def evaluar_tablero(tablero):
    # Función eurística aquí
    # Encuentra la columna más alta, primer fila con un 1
    fila_mas_alta = 20
    for fila in range(tablero.shape[0]):
        if not np.any(tablero[fila] == 1):
            fila_mas_alta = fila
            break
    # La suma de la altura de todas las columnas
    sum_alturas = 0
    for col in range(tablero.shape[1]):
        for fila in reversed(range(tablero.shape[0])):
            if tablero[fila][col] == 1:
                sum_alturas += fila + 1
                break
    num_filas_limpias = np.sum(np.all(tablero == 1, axis=1))
    # número de huecos - los 0s que tienen 1 encima
    huecos = np.sum((tablero == 0) & (np.cumsum(tablero, axis=0) < np.sum(tablero, axis=0)))
    # The number of bloqueos - find number of 1s with 0s above
    bloqueos = np.sum((tablero == 1) & (np.cumsum(tablero, axis=0) > 0))
    # asigna persos más altos  a bloques más altos
    altura_compensada = 0
    for col in range(tablero.shape[1]):
        for fila in reversed(range(tablero.shape[0])):
            # encuentra el bloque más alto de cada columna
            if tablero[fila][col] == 1:
                if fila > 5:
                    altura_compensada += (fila + 1) * (fila + 1 - 5)
                else:
                    altura_compensada += (fila + 1)
                break

    A, B, C, D, E = -1, 10, -50, -1, -1
    puntaje = A * altura_compensada + B * num_filas_limpias * num_filas_limpias * num_filas_limpias + C * huecos + D * bloqueos + E * fila_mas_alta
    return puntaje

def obtener_posiciones(tablero, bloque_rotado):
    # Retorna una lista de los posibles movimientos de un bloque y sus rotaciones
    posiciones_posibles = []
    # Remueve los 0 de la matriz del bloque
    bloque_rotado = bloque_rotado[~np.all(bloque_rotado == 0, axis=1)]
    bloque_rotado = bloque_rotado[:, ~np.all(bloque_rotado == 0, axis=0)]
    # Arroja el bloque desde lo más alto de cada columna
    for x in range(tablero.shape[1] - bloque_rotado.shape[1] + 1):
        y = tablero.shape[0] - bloque_rotado.shape[0] - 1
        while y >= 0:
            if np.any(np.logical_and(bloque_rotado, tablero[y:y + bloque_rotado.shape[0], x:x + bloque_rotado.shape[1]])):
                if y > tablero.shape[0] - bloque_rotado.shape[0]:
                    print("You lose!")
                    break
                posiciones_posibles.append((y + 1, x))
                break
            if y == 0:
                posiciones_posibles.append((y, x))
            y -= 1

    return posiciones_posibles

def limpiar_filas_llenas(tablero):
    while True:
        for y, fila in enumerate(tablero):
            if all(cell == 1 for cell in fila):
                tablero = np.delete(tablero, y, axis=0)
                # inserta una nueva fila en la cima del tablero, indice 0
                tablero = np.insert(tablero, tablero.shape[0], 0, axis=0)
                break
            if y == tablero.shape[0] - 1:
                return tablero
            
def num_filas_llenas(tablero):
    return np.sum(np.all(tablero == 1, axis=1))

def econ_menos_huecos(tablero):
    return np.sum((tablero == 0) & (np.cumsum(tablero, axis=0) < np.sum(tablero, axis=0)))



def encon_mejor_posicion(tablero, arreglo_bloques, profundidad):
    def pruebas(tableros, bloque, arreglo_posiciones_rotaciones, tableros_mantener):
        return_arreglo_posiciones_rotaciones = None
        nuevos_tableros = []
        arreglo_nueva_posicion_rotacion = []
        arreglo_puntaje = []
        for index, tablero in enumerate(tableros):
            for rotation in range(len(bloque)):
                posiciones = obtener_posiciones(tablero, bloque[rotation])
                for position in posiciones:
                    nuevo_tablero = place_block(tablero, bloque[rotation], position)
                    # retorna la posición si el tetris está vacío
                    if num_filas_llenas(nuevo_tablero) == 4 or np.all(nuevo_tablero == 0):
                        if arreglo_posiciones_rotaciones is None:
                            return_arreglo_posiciones_rotaciones = [position, rotation]
                        else:
                            return_arreglo_posiciones_rotaciones = arreglo_posiciones_rotaciones[index]

                    # evalua la puntuación del tablero y lo agrega a la lista
                    puntaje = evaluar_tablero(nuevo_tablero)
                    arreglo_puntaje.append(puntaje)
                    nuevo_tablero = limpiar_filas_llenas(nuevo_tablero) # limpia luego de la evaluación
                    nuevos_tableros.append(nuevo_tablero)
                    if arreglo_posiciones_rotaciones is None:
                        arreglo_nueva_posicion_rotacion.append([position, rotation])
                    else:
                        arreglo_nueva_posicion_rotacion.append(arreglo_posiciones_rotaciones[index])
        #Obtiene los tableros de acuerdo a su puntaje según la precisión y los puntos
        top_tableros = [x for _, x in sorted(zip(arreglo_puntaje, nuevos_tableros), key=lambda pair: pair[0], reverse=True)][:tableros_mantener]
        mejor_posiciones_rotaciones = [x for _, x in sorted(zip(arreglo_puntaje, arreglo_nueva_posicion_rotacion), key=lambda pair: pair[0], reverse=True)][:tableros_mantener]
        
        return top_tableros, mejor_posiciones_rotaciones, return_arreglo_posiciones_rotaciones
    tablero = tablero.copy()
    top_tableros = []
    mejor_posiciones_rotaciones = []
    # añade piezas fantasma de tetris_piezas a arreglo_bloques
    if profundidad > len(arreglo_bloques):
        for i in range(profundidad - len(arreglo_bloques)):
            piece = tetris_piezas[list(tetris_piezas.keys())[np.random.randint(len(tetris_piezas))]]
            arreglo_bloques.append(piece)
    for i in range(profundidad):
        if i == 0:
            top_tableros, mejor_posiciones_rotaciones, return_arreglo_posiciones_rotaciones = pruebas([tablero], arreglo_bloques[i], None, presicion_cal)
            if return_arreglo_posiciones_rotaciones is not None:
                return return_arreglo_posiciones_rotaciones
        elif i == profundidad - 1:
            top_tableros, mejor_posiciones_rotaciones, return_arreglo_posiciones_rotaciones = pruebas(top_tableros, arreglo_bloques[i], mejor_posiciones_rotaciones, 1)
            if return_arreglo_posiciones_rotaciones is not None:
                return return_arreglo_posiciones_rotaciones
            return     mejor_posiciones_rotaciones[0]
        else:
            top_tableros,       mejor_posiciones_rotaciones, return_arreglo_posiciones_rotaciones = pruebas(top_tableros, arreglo_bloques[i],           mejor_posiciones_rotaciones, presicion_cal)
            if return_arreglo_posiciones_rotaciones is not None:
                return return_arreglo_posiciones_rotaciones


def place_block(tablero, bloque_rotado, posicion):
    nuevo_tablero = tablero.copy()
    # remueve los 0s de la rotación de las piezas
    bloque_rotado = bloque_rotado[~np.all(bloque_rotado == 0, axis=1)]
    bloque_rotado = bloque_rotado[:, ~np.all(bloque_rotado == 0, axis=0)]
    nuevo_tablero[posicion[0]:posicion[0] + bloque_rotado.shape[0], posicion[1]:posicion[1] + bloque_rotado.shape[1]] += bloque_rotado
    return nuevo_tablero

def euclidean_distance(color1, color2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))

def color_del_area(colores, x, y):
    min_diferencia = float('inf')
    color_cercano = (0, 0, 0)
    while min_diferencia > 20:
        # break si esc
        if keyboard.is_pressed('esc'):
            break
        # obtiene el color de los pixeles en un cuadrado de 10*10
        objetivo_colores = []
        # obtiene una porción de la pantalla
        half = pixel_area//2
        full = half * 2
        image = ImageGrab.grab(bbox=(x - half, y - half, x + half, y + half))
        # Revisa en ciclo los pixeles de la pantalla
        for i in range(full):
            for j in range(full):
                objetivo_colores.append(image.getpixel((i, j)))

        # Encuentra la mejor coincidencia de color
        color_cercano = (0, 0, 0)
        min_diferencia = float('inf')
        for color_objetivo in objetivo_colores:
            for color in colores:
                diferencia = euclidean_distance(color, color_objetivo)
                if diferencia < min_diferencia:
                    min_diferencia = diferencia
                    color_cercano = color
                if min_diferencia < 20:
                    break
    return tuple(color_cercano)

def obtenerPieza(color_encon, colores):
    piece = None
    if color_encon == colores[0]:
        # print('Rojo - Z')
        piece = tetris_piezas['Z']
    elif color_encon == colores[1]:
        # print('Verde - Z2')
        piece = tetris_piezas['Z2']
    elif color_encon == colores[2]:
        # print('Azul Oscuro - L2')
        piece = tetris_piezas['L2']
    elif color_encon == colores[3]:
        # print('Amarillo - O')
        piece = tetris_piezas['O']
    elif color_encon == colores[4]:
        # print('Azul claro - I')
        piece = tetris_piezas['I']
    elif color_encon == colores[5]:
        # print('Naranja - L')
        piece = tetris_piezas['L']
    elif color_encon == colores[6]:
        # print('Morado - T')
        piece = tetris_piezas['T']
    if piece is None:
        print('No piece found')
    return piece


#Crea un nuevo tablero
tetristablero = TetrisTablero()
tablero_initialized = False
piezas = []

def key_press(mejor_posicion, mejor_rotacion):
    # rotar
    if mejor_rotacion == 1:
        keyboard.press(rotar_horario)
        keyboard.release(rotar_horario)
        #if retraso > 0:
        #    time.sleep(retraso)
    elif mejor_rotacion == 2:
        keyboard.press(rotar_180)
        keyboard.release(rotar_180)
        #if retraso > 0:
        #    time.sleep(retraso)
    elif mejor_rotacion == 3:
        keyboard.press(rotar_antihorario)
        keyboard.release(rotar_antihorario)
        #if retraso > 0:
        #    time.sleep(retraso)
    # mueve hacia los lados para llegar a la posición objetivo
    if mejor_posicion[1] < 3:
        for i in range(3 - mejor_posicion[1]):
            keyboard.press(mov_izquierda)
            keyboard.release(mov_izquierda)
            #if retraso > 0:
            #    time.sleep(retraso)
    elif mejor_posicion[1] > 3:
        for i in range(mejor_posicion[1] - 3):
            keyboard.press(mov_derecha)
            keyboard.release(mov_derecha)
            #if retraso > 0:
            #    time.sleep(retraso)
    # suelta la pieza con espacio
    keyboard.press('space')
    keyboard.release('space')
    #if retraso > 0:
    #    time.sleep(retraso)


def get_tetris_tablero_from_screen(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    tablero_coords = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
    tablero_image = ImageGrab.grab(tablero_coords)
    tablero_image = tablero_image.convert('L')
    tablero = np.zeros((20, 10), dtype=int)
    ancho_bloque = tablero_image.width / 10
    alto_bloque = tablero_image.height / 20

    for fila in reversed(range(20)):
        fila_vacia = True
        for col in range(10):
            total_darkness = 0
            num_pixels = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x = math.floor(col * ancho_bloque + ancho_bloque / 2) + dx
                    y = math.floor(fila * alto_bloque + alto_bloque / 2) + dy
                    pixel_value = tablero_image.getpixel((x, y))
                    total_darkness += pixel_value
                    num_pixels += 1
            avg_darkness = total_darkness / num_pixels

            if avg_darkness < 30:
                tablero[20 - fila - 1][col] = 0
            else:
                fila_vacia = False
                tablero[20 - fila - 1][col] = 1
        if fila_vacia:
            break
    return tablero



# iniciar el programa
while True:
    # Rompe el procedimiento con P 
    if keyboard.is_pressed('/'):
        break

    if not tablero_initialized and keyboard.is_pressed('space'):
        print('Tablero iniciado')
        tablero_initialized = True
        # calcular pixel_area
        colorFicha1 = color_del_area(colores, x1, y1)
        colorFicha2 = color_del_area(colores, x2, y2)
        colorFicha3 = color_del_area(colores, x3, y3)
        colorFicha4 = color_del_area(colores, x4, y4)
        colorFicha5 = color_del_area(colores, x5, y5)

        piezas.append(obtenerPieza(colorFicha1, colores))
        piezas.append(obtenerPieza(colorFicha2, colores))
        piezas.append(obtenerPieza(colorFicha3, colores))
        piezas.append(obtenerPieza(colorFicha4, colores))
        piezas.append(obtenerPieza(colorFicha5, colores))

        first_move = True
        while True:
            # ESC para terminar el programa
            #if keyboard.is_pressed('/'):        en serio un if ejecutandose siempre en el ciclo?
            #    break
            # reiniciar
            #if keyboard.is_pressed('*'):
            #    tablero_initialized = False
            #    break
            # bloquear hasta que inicien las piezas
            if first_move:
                color_cercano1_0 = color_del_area(colores, x1, y1)
                color_cercano2_0 = color_del_area(colores, x2, y2)
                if colorFicha2 != color_cercano2_0 or colorFicha1 != color_cercano1_0:
                    first_move = False
                else:
                    continue

            # tiempo para obtener el color

            colorFicha5 = color_del_area(colores, x5, y5)
            piezas.append(obtenerPieza(colorFicha5, colores))

            if scan_tablero:
                # obtener el tablero de la pantalla
                tetristablero.tablero = get_tetris_tablero_from_screen(x1_tablero, y1_tablero, x2_tablero, y2_tablero)
                #for fila in reversed(tetristablero.tablero):
                #    print(fila)
                #print("--------------------------------------")

            # tiempo para encontrar la mejor jugada
            mejor_posicion, mejor_rotacion = encon_mejor_posicion(tetristablero.tablero, piezas.copy(), profun_max)

            mejor_pieza_rotada = piezas[0][mejor_rotacion]
            # remover la primer pieza del arreglo, la usada
            piezas.pop(0)

            # add offset depending on padded zeros on the left side of axis 1 only
            offset = 0
            for i in range(mejor_pieza_rotada.shape[1]):
                if not any(mejor_pieza_rotada[:, i]):
                    offset += 1
                else:
                    break
            mejor_posicion2 = (mejor_posicion[0], mejor_posicion[1] - offset)

            # Presión de las teclas
            key_press(mejor_posicion2, mejor_rotacion)

            # remover margen de 0s
            mejor_pieza_rotada = mejor_pieza_rotada[~np.all(mejor_pieza_rotada == 0, axis=1)]
            mejor_pieza_rotada = mejor_pieza_rotada[:, ~np.all(mejor_pieza_rotada == 0, axis=0)]
            tetristablero.add_piece(mejor_pieza_rotada, mejor_posicion)

            # limpiar todas las columnas
            tetristablero.limpiar_filas_llenas()
            time.sleep(retraso_refresco) # Tiempo de espera para refrescar la pantalla
