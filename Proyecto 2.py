#Importaciones
import random
from collections import deque

#Clases
#-------------------------------------COMPONENTES DEL MAPA-------------------------------------
class Celda:
   def permite_jugador(self):
        return False
    
   def permite_enemigo(self):
        return False
#--------------------------------#
class Camino(Celda):
   def permite_jugador(self):
        return True
    
   def permite_enemigo(self):
        return True
#--------------------------------#       
class Lianas(Celda):
   def permite_jugador(self):
        return False
    
   def permite_enemigo(self):
        return True
#--------------------------------#      
class Tuneles(Celda):
   def permite_jugador(self):
        return True
    
   def permite_enemigo(self):
        return False
#--------------------------------#
class Muro(Celda):
   def permite_jugador(self):
        return False
    
   def permite_enemigo(self):
        return False
#----------------------------------------------------------------------------------------------

class Mapa:
    def __init__(self, filas=10, columnas=40):
        self.filas = filas
        self.columnas = columnas
        self.entrada = (0, 0)
        self.salida = (filas-1, columnas-1)
        self.jugador_pos = self.entrada
        self.enemigos_pos = []
        self.trampas = []# para modo Escapa

    def crear_mapa(self):
        from collections import deque
        tipos = [Camino, Lianas, Tuneles, Muro]
        pesos = [65, 10, 10, 15]  # 65% camino
        while True:
            self.matriz = [[random.choices(tipos, weights=pesos)[0]() for _ in range(self.columnas)] for _ in range(self.filas)]
            #Fuerza entrada y salida como camino
            self.matriz[0][0] = Camino()
            self.matriz[self.filas-1][self.columnas-1] = Camino()
            # Verifica si hay caminos 
            if self.hay_camino_jugador_escape() and self.hay_camino_jugador_cazador():
               self.colocar_enemigos(5) #Coloca enemigos 
               break

    def hay_camino_jugador_escape(self):
        return self.bfs(lambda c: c.permite_jugador())

    def hay_camino_jugador_cazador(self):
        return self.bfs(lambda c: c.permite_enemigo())

    def bfs(self, permite_func):
        visitado = [[False] * self.columnas for _ in range(self.filas)]
        cola = deque([self.entrada])
        visitado[0][0] = True

        while cola:
            y, x = cola.popleft()
            if (y, x) == self.salida:
                return True
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = y + dy, x + dx
                if (0 <= ny < self.filas and 0 <= nx < self.columnas 
                    and not visitado[ny][nx] 
                    and permite_func(self.matriz[ny][nx])):
                    visitado[ny][nx] = True
                    cola.append((ny, nx))
        return False

    def colocar_enemigos(self, cantidad):
        posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas) if isinstance(self.matriz[y][x], Camino) and (y,x) not in [self.entrada, self.salida]]
        random.shuffle(posiciones_validas) 
        self.enemigos_pos = posiciones_validas[:cantidad]

class Jugador:
   def __init__(self, nombre, modo):
      self.nombre = nombre
      self.modo = modo
      self.stamina = 100
      self.correr = True
      self.puntos = 0
      self.puntaje_e = 0
      self.puntaje_c = 0

   def direccion(self, direc):
      pass
   
   def ganar_puntos(self, puntos):
      self.puntos += puntos

   def perder_puntos(self, puntos):
      self.puntos -= puntos
   
   def bajar_stamina(self, cantidad):#TODO: Hacer coldown para que no baje tan rapido
      self.stamina -= cantidad
      if self.stamina < 0:
         self.stamina = 0

   def subir_stamina(self, cantidad):#TODO: Hacer coldown para que no suba tan rapido
      self.stamina += cantidad
      if self.stamina > 100:
         self.stamina = 100

   def calcular_puntaje(self, modo):
      if modo == "Cazador":
         self.puntaje_c = 0
      else:
         self.puntaje_e = 0

"""      
class Enemigo:

Ideas de allison:
1. Hacer que cada celda de la matriz del laberinto, que cada lado de la celda sea representado con una lista. Las casillas no tienen caras  
2. Stamina: Con cuadritos. dividir 100 en 5 cuadritos, cuando la stamina este en 100% se muestran los 5, si esta al 80% se muestran 4.
3. Nathan: Modo Cazador 
   Valeria: Modo Espace
"""

mapa1 = Mapa()
mapa1.crear_mapa()
simbolos = {
        Camino: "·",
        Lianas: "§",
        Tuneles: "≈",
        Muro: "|"
    }

for y in range(mapa1.filas):
   fila = ""
   for x in range(mapa1.columnas):
      if (y,x) == mapa1.entrada:
         fila += "E"
      elif (y,x) == mapa1.salida:
         fila += "S"
      else:
         fila += simbolos.get(type(mapa1.matriz[y][x]))
   print(fila)
print("\nEnemigos en:", mapa1.enemigos_pos)