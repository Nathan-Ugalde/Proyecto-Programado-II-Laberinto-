#Importaciones
import random  

#Clases
class Celda:
   def __init__(self, pasa):
       self.pasa = True

class Camino(Celda):
   def verificar_paso(self):
       return self.pasa
        
class Lianas(Celda):
   def verificar_paso(self, jugador):
      if jugador.modo == "Cazador":
         return True
      else:
         return False
      
class Tuneles(Celda):
   def verificar_paso(self, jugador):
      if jugador.modo == "Escape":
         return True
      else:
         return False

class Muro(Celda):
   def verificar_paso(self):
      self.pasa = False
      return self.pasa


class Mapa:
   def __init__(self):
      self.entrada = (0, 0)
      self.salida = (0, 0)
      self.matriz = []

   def crear_mapa(self, filas=15, columnas=30):
      self.matriz = [[random.choice([Camino(True), Lianas(True), Tuneles(True), Muro(False)]) for _ in range(columnas)] for _ in range(filas)]
      print(self.matriz) 

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
"""
"""
Ideas de allison:
1. Hacer que cada celda de la matriz del laberinto, que cada lado de la celda sea representado con una lista. Las casillas no tienen caras  
2. Stamina: Con cuadritos. dividir 100 en 5 cuadritos, cuando la stamina este en 100% se muestran los 5, si esta al 80% se muestran 4.
3. Nathan: Modo Cazador 
   Valeria: Modo Espace
"""

mapa1 = Mapa()
mapa1.crear_mapa()
