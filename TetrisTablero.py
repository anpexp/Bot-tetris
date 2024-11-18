import numpy as np

#Se realiza una representación del tablero de juego en forma de matriz de 1 y 0
class TetrisTablero:
    #Se inicia el tablero con una matriz de 0 de 20X10
    def __init__(self):
        self.tablero = np.zeros((20, 10), dtype=int)

    
    def add_piece(self, piece, position):
        for y, row in enumerate(piece):
            for x, celda in enumerate(row):
                if celda:
                    self.tablero[position[0] + y, position[1] + x] = 1

    def does_piece_fit(self, piece, position):
        for y, row in enumerate(piece):
            for x, celda in enumerate(row):
                if celda:
                    if position[0] + y >= self.tablero.shape[0] or position[1] + x >= self.tablero.shape[1]:
                        return False
                    if self.tablero[position[0] + y, position[1] + x] == 1:
                        return False
        return True

    def limpiar_filas_llenas(self):
        while True:
            for y, row in enumerate(self.tablero):
                if all(celda == 1 for celda in row):
                    self.tablero = np.delete(self.tablero, y, axis=0)
                    # Insertar una nueva fila en el último lugar, el más alto del tablero
                    self.tablero = np.insert(self.tablero, self.tablero.shape[0], 0, axis=0)
                    break
                if y == self.tablero.shape[0] - 1:
                    return
        
