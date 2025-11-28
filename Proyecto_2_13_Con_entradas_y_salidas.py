#Elaborado Por: Valeria Vargas Benavides, Nathan Ugalde Villalobos
#Fecha de creación: 
#Fecha de última modificación:
#Versión de Python: 3.13.9

#Importaciones
import random
import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import time
import json
import os
import pygame

#---------------CREACIÓN DE LA BASE DE DATOS---------------#
'''
e: -
s: carga y guarda los usuarios en archivo JSON
r: -
'''
arch = "usuarios.json"
def cargar_usuarios():
   # E: Ninguna
   # S: dict con la estructura {"usuarios": [...]}
   if not os.path.exists(arch):
      with open(arch, "w") as f:
         json.dump({"usuarios": []}, f)

   with open(arch, "r") as f:
      return json.load(f)

'''
e: data (dict con estructura de usuarios)    
s: Ninguna (guarda en archivo)
r: -
'''
def guardar_usuarios(data):
   # E: data (dict con estructura de usuarios)
   # S: Ninguna (guarda en archivo)
   with open(arch, "w") as f:
      json.dump(data, f, indent=4)

'''
e: nombre (str)
s: bool (True si se registró, False si ya existe)
r: -
'''
def registrar_usuario(nombre):
   # E: nombre (str)
   # S: bool (True si se registró, False si ya existe)
    
    data = cargar_usuarios()

    for u in data["usuarios"]:
        if u["nombre"] == nombre:
            return False  #Ya existe

    data["usuarios"].append({
        "nombre": nombre,
        "puntaje_escape": 0,
        "puntaje_cazador": 0
    })

    guardar_usuarios(data)
    return True

#---------------SONIDOS---------------#
pygame.init()
pygame.mixer.init()
steps = pygame.mixer.Sound('pasos-435087.mp3')
steps.set_volume(1.0)
tramp = pygame.mixer.Sound('ceramic_mug_cup-31808.mp3')
tramp.set_volume(0.3)
killsound = pygame.mixer.Sound('sword-slash-and-swing-185432.mp3')
killsound.set_volume(0.3)
background_music = pygame.mixer.Sound('rock-thunder-rock-music-background-336548.mp3')
background_music.set_volume(0.1)
deadsound = pygame.mixer.Sound('bell-toll-407826.mp3')
deadsound.set_volume(1.0)
gameover = pygame.mixer.Sound('dead-8bit-41400.mp3')

#-----------------------CLASES-----------------------#
#--------Componente del jugador--------#
'''
e: nombre (str), modo (str: "Escape" o "Cazador")
s: Instancia de Jugador inicializada
r: -
'''
class Jugador:
   def __init__(self, nombre, modo):
      # E: nombre (str), modo (str: "Escape" o "Cazador")
      # S: Instancia de Jugador inicializada
      self.nombre = nombre
      self.modo = modo
      self.stamina = 100
      self.correr = True
      self.puntos = 0
      self.puntaje_e = 0
      self.puntaje_c = 0
   '''
   e: puntos (int)
   s: Ninguna (modifica self.puntos)
   r: -
   '''
   def ganar_puntos(self, puntos):
      # E: puntos (int)
      # S: Ninguna (modifica self.puntos)
      self.puntos += puntos
   '''
   e: puntos (int)
   s: Ninguna (modifica self.puntos)
   r: -
   '''
   def perder_puntos(self, puntos):
      # E: puntos (int)
      # S: Ninguna (modifica self.puntos)
      self.puntos -= puntos
   '''
   e: cantidad (int)
   s: Ninguna (modifica self.stamina)
   r: -
   '''
   def bajar_stamina(self, cantidad):
      # E: cantidad (int)
      # S: Ninguna (modifica self.stamina)
      self.stamina -= cantidad
      if self.stamina < 0:
         self.stamina = 0
   '''
   e: cantidad (int)
   s: Ninguna (modifica self.stamina)
   r: -
   '''
   def subir_stamina(self, cantidad):
      # E: cantidad (int)
      # S: Ninguna (modifica self.stamina)
      self.stamina += cantidad
      if self.stamina > 100:
         self.stamina = 100
   '''
   e: modo (str: "Escape" o "Cazador")
   s: Ninguna (asigna puntaje según modo)
   r: -
   '''
   def calcular_puntaje(self, modo):
      # E: modo (str: "Escape" o "Cazador")
      # S: Ninguna (asigna puntaje según modo)
      if modo == "Cazador":
         self.puntaje_c = self.puntos
      else:
         self.puntaje_e = self.puntos

#--------Coponentes del enemigo--------#
'''
e: y (int), x (int), mapa (Mapa), canvas (Canvas), modo (str)
s: Instancia de Enemigo inicializada
r: -
'''
class Enemigo:
   def __init__(self, y, x, mapa, canvas, modo):
      # E: y (int), x (int), mapa (Mapa), canvas (Canvas), modo (str)
      # S: Instancia de Enemigo inicializada
      self.y = y
      self.x = x
      self.mapa = mapa
      self.canvas = canvas
      self.modo = modo  # "Escape" o "Cazador"
      self.grafico = self.canvas.create_rectangle(x * 30 + 5, y * 30 + 5,x * 30 + 25, y * 30 + 25,fill="purple")

   '''
   e: Ninguna (usa atributos de self)
   s: Ninguna (modifica posición y estado del enemigo)
   r: -
   '''
   def mover(self):
      # E: Ninguna (usa atributos de self)
      # S: Ninguna (modifica posición y estado del enemigo)
      yj, xj = self.mapa.jugador_pos
      opciones = [(-1,0),(1,0),(0,-1),(0,1)]
      mejor_mov = None

      if self.modo == "Escape":
         mejor_dist = float('inf')
      else:  # Cazador
         mejor_dist = float('-inf')

      for dy, dx in opciones:
         ny, nx = self.y + dy, self.x + dx

         if 0 <= ny < self.mapa.filas and 0 <= nx < self.mapa.columnas:
            if self.modo == "Escape":
               if self.mapa.matriz[ny][nx].permite_enemigo():
                  dist = abs(ny - yj) + abs(nx - xj)
                  if dist < mejor_dist:
                     mejor_dist = dist
                     mejor_mov = (ny, nx)
            else:  # Cazador
               if self.mapa.matriz[ny][nx].permite_jugador():
                  dist = abs(ny - yj) + abs(nx - xj)
                  if dist > mejor_dist:
                     mejor_dist = dist
                     mejor_mov = (ny, nx)

      if mejor_mov:
         self.y, self.x = mejor_mov
         self.canvas.coords(
            self.grafico,
            self.x * 30 + 5, self.y * 30 + 5,
            self.x * 30 + 25, self.y * 30 + 25
         )

      # Si atrapa al jugador en modo escape
      if self.modo == 'Escape':
         for trampa in getattr(self.mapa, 'trampas', []):
            if trampa.esta_en_posicion(self.y, self.x):
               trampa.desactivar()
               self.eliminar()
               if self in self.mapa.enemigos:
                  self.mapa.enemigos.remove(self)
                  def reaparecer():
                     self.mapa.colocar_enemigo_aleatorio()
                  self.canvas.after(10000, reaparecer)
               return

         if (self.y, self.x) == self.mapa.jugador_pos:
            deadsound.play()
            messagebox.showinfo("¡Has sido atrapado!", "¡Un enemigo te ha atrapado!")
            self.mapa.ventana.destroy()
   ''' 
   e: Ninguna
   s: Ninguna (elimina el gráfico del canvas)
   r: -
   '''
   def eliminar(self):
      # E: Ninguna
      # S: Ninguna (elimina el gráfico del canvas)
      self.canvas.delete(self.grafico)

class Trampa:
   def __init__(self, y, x, canvas):
      # E: y (int), x (int), canvas (Canvas)
      # S: Instancia de Trampa inicializada
      self.y = y
      self.x = x
      self.activa = True
      self.canvas = canvas
        
      self.grafico = self.canvas.create_rectangle(x*30+10, y*30+10,x*30+20, y*30+20, fill="yellow")
   '''
   e: Ninguna
   s: Ninguna (modifica self.activa y canvas)
   r: -
   '''
   def desactivar(self):
      # E: Ninguna
      # S: Ninguna (modifica self.activa y canvas)
      self.activa = False
      self.canvas.delete(self.grafico)
   '''
   e: y (int), x (int)
   s: bool (True si trampa está en posición y está activa)
   r: -
   '''
   def esta_en_posicion(self, y, x):
      # E: y (int), x (int)
      # S: bool (True si trampa está en posición y está activa)
      return self.activa and self.y == y and self.x == x

#-------------------------------------COMPONENTES DEL MAPA-------------------------------------#
class Celda:
   '''
   e: - 
   s: bool (True si jugador puede pasar)
   r: -'''
   def permite_jugador(self):
        return False
   '''
   e: - 
   s: bool (True si enemigo puede pasar)
   r: -'''
   def permite_enemigo(self):
        return False
#--------------------------------#
class Camino(Celda):
   '''
   e: -
   s: bool (True si jugador puede pasar)
   r: -'''
   def permite_jugador(self):
        return True
   '''
   e: -
   s: bool (True si enemigo puede pasar)
   r: -'''
   def permite_enemigo(self):
        return True
#--------------------------------#       
class Lianas(Celda):
   '''
   e: -
   s: bool (True si jugador puede pasar)
   r: -'''
   def permite_jugador(self):
        return False
   '''
   e: -
   s: bool (True si enemigo puede pasar)
   r: -'''
   def permite_enemigo(self):
        return True
#--------------------------------#      
class Tuneles(Celda):
   '''
   e: -
   s: bool (True si jugador puede pasar)
   r: -'''
   def permite_jugador(self):
        return True
   '''
   e: -    
   s: bool (True si enemigo puede pasar)
   r: -'''
   def permite_enemigo(self):
        return False
#--------------------------------#
class Muro(Celda):
   '''
   e: -
   s: bool (True si jugador puede pasar)
   r: -'''
   def permite_jugador(self):
        return False
   '''
   e: -
   s: bool (True si enemigo puede pasar)
   r: -'''
   def permite_enemigo(self):
        return False
#----------------------------------------------------------------------------------------------

class Mapa:
   def __init__(self, jugador, dificultad, filas=20, columnas=40):
      # E: jugador (str), dificultad (str), filas (int), columnas (int)
      # S: Instancia de Mapa inicializada
      self.modo_actual = "Escape"   # o "Cazador"
      self.jugador = Jugador(jugador, self.modo_actual) 
      self.filas = filas
      self.columnas = columnas
      self.entrada = (0, 0)
      self.salida = (filas-1, columnas-1)
      self.jugador_pos = self.entrada
      self.trampas = []
      self.enemigos = []
      self.dificultad = dificultad #Facil, Medio, Dificl
      self.tiempo_inicio = time.time()
      self.tiempo_cazador = time.time() + 150 # 150 segundos para el modo Cazador
   '''
   e: Ninguna
   s: Ninguna (genera self.matriz con celdas aleatorias)
   r: -
   '''
   def crear_mapa(self):
      # E: Ninguna
      # S: Ninguna (genera self.matriz con celdas aleatorias)
      tipos = [Camino, Lianas, Tuneles, Muro]
      pesos = [55,15,15,15]

      while True:
         self.matriz = [[random.choices(tipos, weights=pesos)[0]() 
                      for _ in range(self.columnas)] for _ in range(self.filas)]

         self.matriz[0][0] = Tuneles()
         self.matriz[self.filas-1][self.columnas-1] = Camino()

         if self.hay_camino_jugador_escape() and self.hay_camino_jugador_cazador():
            break
   '''
   e: Ninguna
   s: Ninguna (actualiza canvas)
   r: -
   '''
   def actualizar_stamina(self):
      # E: Ninguna
      # S: Ninguna (actualiza canvas)
      # Borra la barra anterior
      self.canvas.delete("barraStamina")

      tam = 30
      veces = self.jugador.stamina // 20
      self.canvas.create_text(225, self.filas * tam + 20, text=f"Modo: {self.modo_actual} Usuario: {self.jugador.nombre}", fill="Black", font=("Comic Sans MS", 14), tags="barraStamina")
      self.canvas.create_text(980, self.filas * tam + 20, text=f"Dificultad: {self.dificultad}", fill="Black", font=("Comic Sans MS", 14), tags="barraStamina")
      for i in range(veces):
         self.canvas.create_rectangle(
               i * 60 + 455,
               self.filas * tam + 10,
               i * 60 + 510,
               self.filas * tam + 30,
               fill="green",
               outline="black",
               tags="barraStamina")
   '''
   e: Ninguna
   s: Ninguna (crea y muestra interfaz gráfica)
   r: -
   '''
   def mostrar_mapa(self):
      # E: Ninguna
      # S: Ninguna (crea y muestra interfaz gráfica)
      self.ventana = tk.Tk()
      self.ventana.title("Maze Runner")

      tam = 30
      self.canvas = tk.Canvas(self.ventana, width=self.columnas*tam, height=(self.filas*tam+tam), bg="#A9A9A9")
      self.canvas.pack()

      for y in range(self.filas):
         for x in range(self.columnas):
            x1, y1 = x*tam, y*tam
            x2, y2 = x1 + tam, y1 + tam

            if (y, x) == self.entrada:
               color = "green"
               texto = "E"
            elif (y, x) == self.salida:
               color = "red"
               texto = "S"
            else:
               celda = self.matriz[y][x]

               if isinstance(celda, Camino):
                  color = "#544428"
               elif isinstance(celda, Muro):
                  color = "#282726"
               elif isinstance(celda, Lianas):
                  color = "#1F470F"
               elif isinstance(celda, Tuneles):
                  color = "#535353"
               texto = ""

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

            if texto:
               self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=texto,
                                       fill="white", font=("Comic Sans MS", 14))
      self.actualizar_stamina()

      # JUGADOR
      self.jugador_grafico = self.canvas.create_oval(5, 5, 25, 25, fill="blue")
      #-----Movimiento-----#
      self.enCoolDown = False
      self.regenerar = False
      self.tiempoCorrer = 200  # Milisegundos
      self.tiempoTrampa = 5000 # Milisegundos
      self.ventana.bind("<Up>", lambda e: self.controlar_movimiento(0, -1))
      self.ventana.bind("<Down>", lambda e: self.controlar_movimiento(0, 1))
      self.ventana.bind("<Left>", lambda e: self.controlar_movimiento(-1, 0))
      self.ventana.bind("<Right>", lambda e: self.controlar_movimiento(1, 0))
      if self.modo_actual == "Escape":
         self.ventana.bind("<space>", lambda e: self.controlar_trampa())

      #-----Enemigos-----#
      enemigos = 0
      velocidad = 0
      if self.dificultad == 'Fácil':
         enemigos = 5
         velocidad = 600
      if self.dificultad == 'Medio':
         enemigos = 6
         velocidad = 500
      if self.dificultad == 'Difícil':
         enemigos = 7
         velocidad = 400
      self.colocar_enemigos(enemigos)
      '''   
      e: Ninguna
      s: Ninguna (mueve enemigos periódicamente)
      r: -
      '''
      def loop():
         self.mover_enemigos()
         self.ventana.after(velocidad, loop) #Entre mayor sea el número más lentos son los enemigo
      loop()
      self.ventana.mainloop()
   '''
   e: dx (int), dy (int)
   s: Ninguna (mueve jugador si tiene stamina)
   r: -
   '''
   def controlar_movimiento(self, dx, dy):
      # E: dx (int), dy (int)
      # S: Ninguna (mueve jugador si tiene stamina)
      if self.jugador.stamina > 0 and not self.regenerar:

         self.ventana.after((self.tiempoCorrer) - 100)
         self.mover_jugador(dx, dy)
         self.jugador.bajar_stamina(5)
         self.actualizar_stamina()
         steps.play(maxtime=400)

         # Si llegó a 0, empieza regeneración
         if self.jugador.stamina <= 0:
               self.jugador.stamina = 0
               self.regenerar = True
         return

      if self.regenerar:

         if self.enCoolDown:
               return  # espera antes del próximo paso

         self.mover_jugador(dx, dy)
         steps.play(maxtime=400)

         # cooldown por paso
         self.enCoolDown = True
         self.ventana.after(self.tiempoCorrer, self.reset_cooldown)

         # regenera
         self.jugador.subir_stamina(5)
         self.actualizar_stamina()
         # si ya llegó a 100 deja de regenerar
         if self.jugador.stamina >= 100:
               self.jugador.stamina = 100
               self.regenerar = False
      
   '''
   e: Ninguna
   s: Ninguna (coloca trampa si está disponible)
   r: -
   '''
   def controlar_trampa(self):
      # E: Ninguna
      # S: Ninguna (coloca trampa si está disponible)
      if not self.enCoolDown:
         self.colocar_trampa()
         self.enCoolDown = True
         self.ventana.after(self.tiempoTrampa, lambda: setattr(self, 'enCoolDown', False))
         tramp.play()
   '''
   e: Ninguna      
   s: Ninguna (resetea el cooldown)
   r: -
   '''
   def reset_cooldown(self):
      # E: Ninguna
      # S: Ninguna (resetea el cooldown)
      self.enCoolDown = False
   '''
   e: Ninguna
   s: Ninguna (mueve todos los enemigos)
   r: -
   '''
   def mover_enemigos(self):
      # E: Ninguna
      # S: Ninguna (mueve todos los enemigos)
      for enemigo in self.enemigos[:]:
         enemigo.mover()
   '''
   e: cantidad (int)
   s: Ninguna (añade enemigos a self.enemigos)
   r: -
   '''
   def colocar_enemigos(self, cantidad):
      # E: cantidad (int)
      # S: Ninguna (añade enemigos a self.enemigos)
      posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas)
         if isinstance(self.matriz[y][x], Camino)
         and (y,x) not in [self.entrada, self.salida]
         and (y,x) != self.jugador_pos]

      random.shuffle(posiciones_validas)

      for i in range(min(cantidad, len(posiciones_validas))):
         y, x = posiciones_validas[i]
         enemigo = Enemigo(y, x, self, self.canvas, self.modo_actual)
         self.enemigos.append(enemigo)
   '''
   e: Ninguna
   s: Ninguna (añade un enemigo en posición aleatoria)
   r: -
   '''
   def colocar_enemigo_aleatorio(self):
      # E: Ninguna
      # S: Ninguna (añade un enemigo en posición aleatoria)
      posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas)
         if isinstance(self.matriz[y][x], Camino)
         and (y,x) not in [self.entrada, self.salida]
         and (y,x) != self.jugador_pos]
      if posiciones_validas:
         y, x = random.choice(posiciones_validas)
         enemigo = Enemigo(y, x, self, self.canvas, self.modo_actual)
         self.enemigos.append(enemigo)
   '''
   e: px (int), py (int)
   s: Ninguna (mueve jugador, actualiza BD si necesario)
   r: -
   '''
   def mover_jugador(self, px, py):
      # E: px (int), py (int)
      # S: Ninguna (mueve jugador, actualiza BD si necesario)
      y, x = self.jugador_pos
      ny, nx = y + py, x + px

      if not (0 <= ny < self.filas and 0 <= nx < self.columnas):
         return

      if self.modo_actual == "Escape":
         if not self.matriz[ny][nx].permite_jugador():
            return

      if self.modo_actual == "Cazador":
         if not self.matriz[ny][nx].permite_enemigo():
            return
         
      max_puntos_E = 0
      puntos_x_kill = 0
      perdida_x_escape = 0
      multiplicador_dificultad = 0

      if self.dificultad == 'Fácil':
         max_puntos_E = 1500 #2:30 minutos
         puntos_x_kill = 30
         perdida_x_escape = 60
         multiplicador_dificultad = 10
      elif self.dificultad == 'Medio':
         max_puntos_E = 1200 #2 minutos
         puntos_x_kill = 40
         perdida_x_escape = 80
         multiplicador_dificultad = 20
      elif self.dificultad == 'Difícil':
         max_puntos_E = 900 #1:30 minutos
         puntos_x_kill = 50
         perdida_x_escape = 100
         multiplicador_dificultad = 30
      self.jugador_pos = (ny, nx)

      self.canvas.coords(self.jugador_grafico,
                         nx * 30 + 5,
                         ny * 30 + 5,
                         nx * 30 + 25,
                         ny * 30 + 25)
      if (ny, nx) == self.salida:
         if self.modo_actual == 'Escape':
            tiempo_total = time.time() - self.tiempo_inicio
            max_puntos_tiempo = max_puntos_E #Si dura más de 150 no obtiene puntos por tiempo 150 = 2:30 minutos Why? :v
            puntos_tiempo = max(0, max_puntos_tiempo - tiempo_total * multiplicador_dificultad)
            # Solo cuenta trampas desactivadas que eliminaron enemigos
            kills = sum(1 for t in self.trampas if not t.activa)
            puntos_kills = kills * puntos_x_kill
            puntaje_total = int(puntos_tiempo + puntos_kills)
            self.ventana.destroy()

            messagebox.showinfo("Victoria",
                  f"¡Llegaste a la salida!\n"
                  f"La dificultad del juego era: {self.dificultad}\n"
                  f"Tiempo: {tiempo_total:.1f} s\n"
                  f"Puntos por tiempo: {int(puntos_tiempo)}\n"
                  f"Bonus trampas ({kills} kills): {puntos_kills}\n"
                  f"Total: {puntaje_total}")

            self.jugador.ganar_puntos(puntaje_total)
            self.jugador.calcular_puntaje(self.modo_actual)

               #Actualiza la BD con el puntaje total de la partida en modo Escapa
            data = cargar_usuarios()
            for u in data["usuarios"]:
               if u["nombre"] == self.jugador.nombre:
                  if u.get("puntaje_escape", 0) < self.jugador.puntaje_e:
                     u["puntaje_escape"] = self.jugador.puntaje_e
                  break
            guardar_usuarios(data)

      for enemigo in self.enemigos[:]:
         if (enemigo.y, enemigo.x) == (ny, nx):
            if self.modo_actual == "Cazador":
               enemigo.eliminar()
               self.enemigos.remove(enemigo)
               self.colocar_enemigos(1)
               self.jugador.ganar_puntos(puntos_x_kill)
               killsound.play()

         if (enemigo.y, enemigo.x) == self.salida:
            if self.modo_actual == "Cazador":
               enemigo.eliminar()
               self.enemigos.remove(enemigo)
               # Actualiza la BD con el puntaje total de la partida en modo Cazador
               self.jugador.perder_puntos(perdida_x_escape)
               
      
      # Verificar condiciones de fin del modo Cazador
      if self.modo_actual == "Cazador":
         # Si no quedan enemigos
         if not self.enemigos:
            self.jugador.calcular_puntaje(self.modo_actual)
            if self.jugador.puntaje_c < 0:
                self.jugador.puntaje_c = 0
            gameover.play()
            messagebox.showinfo("Game over", f"No quedan más enemigos.\nLa dificultad de juego fue: {self.dificultad}\nPuntaje final: {self.jugador.puntaje_c}")
            data = cargar_usuarios()
            for u in data["usuarios"]:
                if u["nombre"] == self.jugador.nombre:
                    if u.get("puntaje_cazador", 0) < self.jugador.puntaje_c:
                        u["puntaje_cazador"] = self.jugador.puntaje_c
                    break
            guardar_usuarios(data)
            self.ventana.destroy()
         
         # Si se acabó el tiempo
         tiempo_actual = time.time()
         if tiempo_actual >= self.tiempo_cazador:
               self.jugador.calcular_puntaje(self.modo_actual)
               if self.jugador.puntaje_c < 0:
                  self.jugador.puntaje_c = 0
               data = cargar_usuarios()
               for u in data["usuarios"]:
                  if u["nombre"] == self.jugador.nombre:
                     if u.get("puntaje_cazador", 0) < self.jugador.puntaje_c:
                           u["puntaje_cazador"] = self.jugador.puntaje_c
                     break
               guardar_usuarios(data)
               gameover.play()
               messagebox.showinfo("Game over", f"Se acabó el tiempo para atrapar enemigos.\nLa dificultad de juego fue: {self.dificultad}\nPuntaje final: {self.jugador.puntaje_c}")
               self.ventana.destroy()
               
   '''
   e: Ninguna
   s: bool (True si hay camino válido para jugador)
   r: -
   '''
   def hay_camino_jugador_escape(self):
      # E: Ninguna
      # S: bool (True si hay camino válido para jugador)
      return self.bfs(lambda c: c.permite_jugador())
   '''
   e: Ninguna
   s: bool (True si hay camino válido para cazador)
   r: -
   '''
   def hay_camino_jugador_cazador(self):
      # E: Ninguna
      # S: bool (True si hay camino válido para cazador)
      return self.bfs(lambda c: c.permite_enemigo())
   '''
   e: permite_func (función lambda)
   s: bool (True si existe camino de entrada a salida)
   r: -
   '''
   def bfs(self, permite_func):
      # E: permite_func (función lambda)
      # S: bool (True si existe camino de entrada a salida)
      visitado = [[False]*self.columnas for _ in range(self.filas)]
      cola = deque([self.entrada])
      visitado[0][0] = True

      while cola:
         y, x = cola.popleft()

         if (y, x) == self.salida:
            return True

         for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y + dy, x + dx

            if (0 <= ny < self.filas and 0 <= nx < self.columnas and
               not visitado[ny][nx] and
               permite_func(self.matriz[ny][nx])):

               visitado[ny][nx] = True
               cola.append((ny, nx))

      return
   '''
   e: Ninguna
   s: Ninguna (coloca trampa si es posible)
   r: -
   '''
   def colocar_trampa(self):
      # Cuenta SOLO las trampas ACTIVAS
      trampas_activas = sum(1 for t in self.trampas if t.activa)
      if trampas_activas >= 3:
         return

      y, x = self.jugador_pos
      if isinstance(self.matriz[y][x], Tuneles):
         return
      for t in self.trampas:
         if t.activa and t.y == y and t.x == x:
            return

      nueva = Trampa(y, x, self.canvas)
      self.trampas.append(nueva)
   
   

"""
Ideas de allison:
1. Hacer que cada celda de la matriz del laberinto, que cada lado de la celda sea representado con una lista. Las casillas no tienen caras  
2. Stamina: Con cuadritos. dividir 100 en 5 cuadritos, cuando la stamina este en 100% se muestran los 5, si esta al 80% se muestran 4.
3. Nathan: Modo Cazador 
   Valeria: Modo Espace
"""
#Interfaz Gráfica
'''   
e: usuario (str), dificultad (str)
s: Ninguna (inicia ventana de juego)
r: -
'''
def iniciar_juego(usuario, dificultad):
   if dificultad == "":
         messagebox.showerror("Error", "Debe seleccionar una dificultad.")
         return
   ventana_juego = tk.Toplevel(main)
   ventana_juego.title("Maze Runner")
   ventana_juego.configure(bg="#465360")
   ventana_juego.geometry("600x500")

   titulo_juego = tk.Label(ventana_juego, text="Maze Runner", font=("comic sans ms", 24), bg="#465360", fg="white")
   titulo_juego.place(x=300, y=50, anchor="center")
   etiqueta_modo = tk.Label(ventana_juego, text="Seleccione el modo de juego:", font=("comic sans ms", 14), bg="#465360", fg="white")
   etiqueta_modo.place(x=300, y=120, anchor="center")
   '''   
   e: Ninguna
   s: Ninguna (inicia modo escape)
   r: -
   '''
   def modo_escape():
      mapa = Mapa(usuario, dificultad, 20, 40)
      mapa.crear_mapa()
      mapa.modo_actual = "Escape"
      mapa.mostrar_mapa()
      return

   buton_escape = tk.Button(ventana_juego, text="Modo Escape", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=modo_escape)
   buton_escape.place(x=300, y=200, anchor="center")
   '''
   e: Ninguna
   s: Ninguna (inicia modo cazador)
   r: -
   '''
   def modo_cazador():
      mapa = Mapa(usuario, dificultad, 20, 40)
      mapa.crear_mapa()
      mapa.modo_actual = "Cazador"
      mapa.mostrar_mapa()
      return

   buton_cazador = tk.Button(ventana_juego, text="Modo Cazador", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=modo_cazador)
   buton_cazador.place(x=300, y=260, anchor="center")
   '''   
   e: Ninguna
   s: Ninguna (muestra records)
   r: -
   '''
   def ver_records():
      data = cargar_usuarios()
      records_escape = sorted(data["usuarios"], key=lambda u: u.get("puntaje_escape", 0), reverse=True)[:5]
      records_cazador = sorted(data["usuarios"], key=lambda u: u.get("puntaje_cazador", 0), reverse=True)[:5]
      tam = 200

      ventana_records = tk.Toplevel(ventana_juego)
      ventana_records.title("Records")
      ventana_records.configure(bg="#465360")

      canvas_records = tk.Canvas(ventana_records, width=(tam*2)+50, height=(tam*3) + 25, bg="#283845")
      canvas_records.create_text(tam + 25, 50, text="-Top 5 Records Modo Escape - Top 5 Records Modo Cazador-", font=("comic sans ms", 11), fill="white", anchor="center")
      canvas_records.pack()
      x = 0
      y = 1
      i = 0
      for item in records_escape:
         x1 = (x * tam) + 25
         y1 = y * (tam//2)
         x2 = x1 + tam
         y2 = y1 + (tam // 2)
         y += 1
         canvas_records.create_rectangle(x1, y1, x2, y2, fill="#283845", outline="black")
         canvas_records.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=f"{i+1}. {item['nombre']} / {item.get('puntaje_escape', 0)} pts", font=("comic sans ms", 14), fill="white")
         i += 1
      i = 0
      y = 1
      for item in records_cazador:
         x1 = ((x + 1) * tam) + 25
         y1 = y * (tam//2)
         x2 = x1 + tam
         y2 = y1 + (tam // 2)
         y += 1
         canvas_records.create_rectangle(x1, y1, x2, y2, fill="#283845", outline="black")
         canvas_records.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=f"{i+1}. {item['nombre']} / {item.get('puntaje_cazador', 0)} pts", font=("comic sans ms", 14), fill="white")
         i += 1
   buton_records = tk.Button(ventana_juego, text="Ver Records", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=ver_records)
   buton_records.place(x=300, y=320, anchor="center")

   buton_salir = tk.Button(ventana_juego, text="Salir", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=ventana_juego.destroy)
   buton_salir.place(x=300, y=380, anchor="center")
'''
e: Ninguna
s: Ninguna (inicia ventana para crear usuario)
r: -
'''
def crear_usuario():
   ventana_crear = tk.Toplevel(main)
   ventana_crear.title("Crear Usuario")
   ventana_crear.configure(bg="#465360")
   ventana_crear.geometry("400x300")
   usuario = tk.StringVar()

   etiqueta_usuario = tk.Label(ventana_crear, text="Nombre de Usuario:", font=("comic sans ms", 14), bg="#465360", fg="white")
   etiqueta_usuario.place(x=200, y=50, anchor="center")  
   entrada_usuario = tk.Entry(ventana_crear, textvariable=usuario, font=("comic sans ms", 14), width=20)
   entrada_usuario.place(x=200, y=100, anchor="center")
   '''   
   e: Ninguna
   s: Ninguna (crea usuario)
   r: -
   '''
   def crear():
      nombre = usuario.get().strip()

      if nombre == "":
         messagebox.showerror("Error", "Ingrese un nombre.")
         return
        
      if registrar_usuario(nombre):
         messagebox.showinfo("Éxito", "Usuario creado correctamente.")
         ventana_crear.destroy()
      else:
         messagebox.showwarning("Error", "Ese usuario ya existe.")

   buton_ingresar = tk.Button(ventana_crear, text=" Crear ", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=crear)
   buton_ingresar.place(x=200, y=160, anchor="center")
   buton_salir = tk.Button(ventana_crear, text="Salir", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=ventana_crear.destroy)
   buton_salir.place(x=200, y=220, anchor="center")
'''
e: Ninguna
s: Ninguna (inicia ventana para crear usuario)
r: -
'''
def iniciar_sesion():
   data = cargar_usuarios() # Bro, puse esto primero, porque cuando no hay ususario, se ve por un segundo la ventana vacia.
   opcion_usuario = [u["nombre"] for u in data["usuarios"]]
   if opcion_usuario == []:
      messagebox.showwarning("Error", "No hay usuarios registrados. Cree uno primero.")
      ventana_sesion.destroy()
      return
   ventana_sesion = tk.Toplevel(main)
   ventana_sesion.title("Iniciar Sesión")
   ventana_sesion.configure(bg="#465360")
   ventana_sesion.geometry("400x300")
   '''   
   e: p1 (str), p2 (str)
   s: Ninguna (inicia juego con usuario y dificultad seleccionados)
   r: -
   '''
   def varias_tareas(p1, p2):
      iniciar_juego(p1, p2)
      ventana_sesion.destroy()
   '''   
   e: Ninguna
   s: Ninguna (inicia ventana para seleccionar dificultad)
   r: -
   '''
   def seleccionar_dificultad():
      if combo_usuarios.get() == "":
         messagebox.showerror("Error", "Debe seleccionar un usuario.")
         return
      ventana_dificultad = tk.Toplevel(ventana_sesion)
      ventana_dificultad.title("Seleccionar Dificultad")
      ventana_dificultad.configure(bg="#465360")
      ventana_dificultad.geometry("400x300")
      etiqueta_dificultad = tk.Label(ventana_dificultad, text="Seleccione la dificultad:", font=("comic sans ms", 14), bg="#465360", fg="white")
      etiqueta_dificultad.place(x=200, y=50, anchor="center")
      opciones_dificultad = ["Fácil", "Medio", "Difícil"]
      combo_dificultad = ttk.Combobox(ventana_dificultad, font=("comic sans ms", 14), state="readonly", values=opciones_dificultad, width=20)
      combo_dificultad.place(x=200, y=100, anchor="center")
      buton_seleccionar = tk.Button(ventana_dificultad, text="Seleccionar", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=lambda: varias_tareas(combo_usuarios.get(), combo_dificultad.get()))
      buton_seleccionar.place(x=200, y=160, anchor="center")
      buton_salir = tk.Button(ventana_dificultad, text="Salir", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=ventana_dificultad.destroy)
      buton_salir.place(x=200, y=220, anchor="center")
      
   etiqueta_usuario = tk.Label(ventana_sesion, text="Nombre de Usuario:", font=("comic sans ms", 14), bg="#465360", fg="white")
   etiqueta_usuario.place(x=200, y=50, anchor="center")
   combo_usuarios = ttk.Combobox(ventana_sesion, font=("comic sans ms", 14), state="readonly", values=opcion_usuario,  width=20)
   combo_usuarios.place(x=200, y=100, anchor="center")
   buton_ingresar = tk.Button(ventana_sesion, text="Ingresar", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=seleccionar_dificultad)
   buton_ingresar.place(x=200, y=160, anchor="center")
   buton_salir = tk.Button(ventana_sesion, text="Salir", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=ventana_sesion.destroy)
   buton_salir.place(x=200, y=220, anchor="center")

   


   

main = tk.Tk()
main.title("Maze Runner")
main.configure(bg="#465360")
main.geometry("600x400")
titulo = tk.Label(main, text="Maze Runner", font=("comic sans ms", 30), bg="#465360", fg="white")
titulo.place(x=300, y=80, anchor="center")
usuario_crear = tk.Button(main, text="Crear Usuario", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=crear_usuario)
usuario_crear.place(x=300, y=180, anchor="center")
buton_existente = tk.Button(main, text="Iniciar sesión", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=iniciar_sesion)
buton_existente.place(x=300, y=240, anchor="center")
buton_salir = tk.Button(main, text="Salir", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=main.quit)
buton_salir.place(x=300, y=300, anchor="center")
background_music.play(loops=-1)
main.mainloop()