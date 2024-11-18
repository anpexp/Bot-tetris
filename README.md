FUNCIONAMIENTO:
Comandos Anaconda:
```
conda create -n tetrio python=3.10
conda activate tetrio
pip install -r requirements.txt
python test.py
```
Configure additional settings directly in the script

Ajustes de juego:
- ARR 0ms
- DAS 40ms
- Minimo performance de juego
- Color base de las piezas del tetris

Ajustes de pantalla:
Juan Diego
x1_tablero, y1_tablero = 592,166 #Esquina superior izquierda
x2_tablero, y2_tablero = 806,591 #Esquina inferior derecha

x1, y1 = 877,216 #Ficha más alta, la primera pieza en caer
x5, y5 = 877,474 #La última ficha en aparecer

Andres
x1_tablero, y1_tablero  = 786,222 #Esquina superior izquierda
x2_tablero, y2_tablero = 1081,806 #Esquina inferior derecha

x1, y1 = 1180,281 #Ficha más alta, la primera pieza en caer
x5, y5 = 1178,657 #La última ficha en aparecer

Notas sobre el rendimiento
Mientras que aumentar la produndidad mejora la precision, el revisar tantas opciones lo vuelve lento
La razón por la que los primeros movimientos se ven erraticos es porque no está reiniciando el tablero, reiniciar el script lo soluciona
Falla cuando se vuelve dependiente de demasiadas barras verticales, no salen las suficientes y deja espacios acumulandolas
Bajar max_deph y calculation_acurancy a 3 para máxima velocidad, pero pierde 2 de cada 10 partidas por la razón anterior

