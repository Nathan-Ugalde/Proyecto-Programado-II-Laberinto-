#Importaciones
import random
import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import time
import json
import os

#---------------CREACIÓN DE LA BASE DE DATOS---------------#
arch = "usuarios.json"
def cargar_usuarios():
   if not os.path.exists(arch):
      with open(arch, "w") as f:
         json.dump({"usuarios": []}, f)

   with open(arch, "r") as f:
      return json.load(f)

def guardar_usuarios(data):
   with open(arch, "w") as f:
      json.dump(data, f, indent=4)

def registrar_usuario(nombre):
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
#----------------------------------------------------------#


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
   def __init__(self, filas=20, columnas=40):
      self.filas = filas
      self.columnas = columnas
      self.entrada = (0, 0)
      self.salida = (filas-1, columnas-1)
      self.jugador_pos = self.entrada
      self.enemigos_pos = []
      self.trampas = []# para modo Escapa

   def modo_actual(self):
      return ''

   def crear_mapa(self):
      tipos = [Camino, Lianas, Tuneles, Muro]
      pesos = [55, 10, 10, 25]  # 55% camino
      while True:
         self.matriz = [[random.choices(tipos, weights=pesos)[0]() for _ in range(self.columnas)] for _ in range(self.filas)]
         #Fuerza entrada y salida como camino
         self.matriz[0][0] = Camino()
         self.matriz[self.filas-1][self.columnas-1] = Camino()
         # Verifica si hay caminos 
         if self.hay_camino_jugador_escape() and self.hay_camino_jugador_cazador():
            self.colocar_enemigos(5) #Coloca enemigos 
            break
            
   def mostrar_mapa(self):
      self.ventana = tk.Tk()
      self.ventana.title("Maze Runner")
      tam_celda = 30  # Tamaño de cada casilla
      ancho = self.columnas * tam_celda
      alto = self.filas * tam_celda
      self.canvas = tk.Canvas(self.ventana, width=ancho, height=alto)
      self.canvas.pack()

      for y in range(self.filas):
         for x in range(self.columnas):
               x1 = x * tam_celda
               y1 = y * tam_celda
               x2 = x1 + tam_celda
               y2 = y1 + tam_celda
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
                     texto = ""
                  elif isinstance(celda, Muro):
                     color = "#282726"
                     texto = ""
                  elif isinstance(celda, Lianas):
                     color = "#1F470F"
                     texto = ""
                  elif isinstance(celda, Tuneles):
                     color = "#535353"
                     texto = ""
               self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
               if texto != "":
                  self.canvas.create_text(
                     (x1 + x2)//2,
                     (y1 + y2)//2,
                     text=texto,
                     fill="white",
                     font=("Comic Sans MS", 14))
                  
      #-------Player-------#
      self.jugador_grafico = self.canvas.create_oval(5, 5, 25, 25,fill="blue") #dibuja al jugador 
      #-----Movimiento-----#
      self.ventana.bind("<Up>", lambda e: self.mover_jugador(0, -1)) #izq = -1, 0
      self.ventana.bind("<Down>", lambda e: self.mover_jugador(0, 1)) #der = 1, 0
      self.ventana.bind("<Left>", lambda e: self.mover_jugador(-1, 0)) #up = 0, -1
      self.ventana.bind("<Right>", lambda e: self.mover_jugador(1, 0)) #down = 0, 1
      #-------Enemies------#
      self.enemigos_graficos = []
      for (y, x) in self.enemigos_pos:
         enemigo = self.canvas.create_rectangle(x*30+5, y*30+5, x*30+25, y*30+25, fill="purple")
         self.enemigos_graficos.append(enemigo)
      #-----Movimiento Escape Mode-----#      
      if self.modo_actual == 'Escape':
         def loop():
            self.mover_enemigos_Escape()
            self.ventana.after(400, loop)  #Entre mayor sea el número más lentos son
         loop()
      #-----Movimiento Cazador Mode-----#      
      elif self.modo_actual == 'Cazador':
         def loop():
            self.mover_enemigos_Cazador()
            self.ventana.after(400, loop)  #Entre mayor sea el número más lentos son
         loop()
      #--------------------#

   def hay_camino_jugador_escape(self):
      return self.bfs(lambda c: c.permite_jugador())
   '''
   el lambda permite que el BFS decida si puede avanzar 
   a una celda dependiendo de si esa celda permite el paso 
   del jugador o del enemigo
   '''
   def hay_camino_jugador_cazador(self):
      return self.bfs(lambda c: c.permite_enemigo())

   def bfs(self, permite_func): #determina que si existe un camino desde la entrada hasta la salida 
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
      posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas) if isinstance(self.matriz[y][x], Camino) and (y,x) not in [self.entrada, self.salida] and (y,x) != self.jugador_pos and (y,x) not in self.enemigos_pos]
      random.shuffle(posiciones_validas) 
      self.enemigos_pos = posiciones_validas[:cantidad]
   
   def mover_jugador(self, px, py):
      y, x = self.jugador_pos
      ny, nx = y + py, x + px

      #TODO: hacer que se de un mensaje de movimiento inválido o algo así xd, Why? Ya queda claro que no se puede salir de la pantalla o pasar por muros, okok
      if self.modo_actual == 'Escape':
         if not (0 <= ny < self.filas and 0 <= nx < self.columnas): #verifica que el jugador no pueda salir del mapa 
            return
         if not self.matriz[ny][nx].permite_jugador(): #verifica que jugador puede pasar por esa celda
            return
         self.jugador_pos = (ny, nx)

         self.canvas.coords(self.jugador_grafico, nx * 30 + 5, ny * 30 + 5, nx * 30 + 25, ny * 30 + 25)

         if (ny, nx) == self.salida:
            messagebox.showinfo("¡Felicidades!", "¡Has llegado a la salida!")
            self.ventana.destroy()

         
         if (ny, nx) in self.enemigos_pos:
            messagebox.showinfo("¡Has sido atrapado!", "¡Un enemigo te ha atrapado!")
            self.ventana.destroy()

      elif self.modo_actual == 'Cazador':
         if not (0 <= ny < self.filas and 0 <= nx < self.columnas): #verifica que el jugador no pueda salir del mapa 
            return
         if not self.matriz[ny][nx].permite_enemigo(): #verifica que jugador puede pasar por esa celda
            return
         self.jugador_pos = (ny, nx)

         self.canvas.coords(self.jugador_grafico, nx * 30 + 5, ny * 30 + 5, nx * 30 + 25, ny * 30 + 25)

         if (ny, nx) in self.enemigos_pos:
            index = self.enemigos_pos.index((ny, nx))
            self.eleminar_enemigo(index)

      return
   
   def mover_enemigos_Escape(self):
      yj, xj = self.jugador_pos
      nuevos = []

      for i, (ye, xe) in enumerate(self.enemigos_pos):

      # Calcular movimientos posibles
         opciones = [(-1,0),(1,0),(0,-1),(0,1)]
         mejor_mov = None
         mejor_dist = float('inf')

         for dy, dx in opciones:
            ny, nx = ye + dy, xe + dx
            #el enemigo puede entrar???
            if 0 <= ny < self.filas and 0 <= nx < self.columnas:
               if self.matriz[ny][nx].permite_enemigo():
                  # Distancia Manhattan a jugador
                  dist = abs(ny - yj) + abs(nx - xj)
                  # Buscar el mejor movimiento
                  if dist < mejor_dist:
                     mejor_dist = dist
                     mejor_mov = (ny, nx)
         if mejor_mov:
            ny, nx = mejor_mov
            nuevos.append((ny, nx))
            self.canvas.coords(self.enemigos_graficos[i], nx * 30 + 5, ny * 30 + 5, nx * 30 + 25, ny * 30 + 25)
         else:
            nuevos.append((ye, xe))
         if (ny, nx) == self.jugador_pos:
            messagebox.showinfo("¡Has sido atrapado!", "¡Un enemigo te ha atrapado!")
            self.ventana.destroy()
            
         self.enemigos_pos = nuevos

   def mover_enemigos_Cazador(self):
      yj, xj = self.jugador_pos
      nuevos = []

      for i, (ye, xe) in enumerate(self.enemigos_pos):
         
         # Calcular movimientos posibles
         opciones = [(-1,0),(1,0),(0,-1),(0,1)]
         mejor_mov = None
         mejor_dist = float('-inf')

         for dy, dx in opciones:
            ny, nx = ye + dy, xe + dx
            #el enemigo puede entrar???
            if 0 <= ny < self.filas and 0 <= nx < self.columnas:
               if self.matriz[ny][nx].permite_jugador():
                  # Distancia Manhattan a jugador
                  dist = abs(ny - yj) + abs(nx - xj)
                  # Buscar el mejor movimiento
                  if dist > mejor_dist:
                     mejor_dist = dist
                     mejor_mov = (ny, nx)
         if mejor_mov:
            ny, nx = mejor_mov
            nuevos.append((ny, nx))
            self.canvas.coords(self.enemigos_graficos[i], nx * 30 + 5, ny * 30 + 5, nx * 30 + 25, ny * 30 + 25)
         else:
            nuevos.append((ye, xe))
      self.enemigos_pos = nuevos

   def eleminar_enemigo(self, index):
      # Eliminar enemigo actual
      del self.enemigos_pos[index]
      self.canvas.delete(self.enemigos_graficos[index])
      del self.enemigos_graficos[index]

      # --- Generar un nuevo enemigo ---
      posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas) if isinstance(self.matriz[y][x], Camino) and (y, x) != self.jugador_pos and (y, x) != self.entrada and (y, x) != self.salida and (y, x) not in self.enemigos_pos]

      if posiciones_validas:
         y, x = random.choice(posiciones_validas)

         # Guardar posición
         self.enemigos_pos.append((y, x))

         # Dibujar enemigo
         nuevo_enemigo = self.canvas.create_rectangle(
               x * 30 + 5, y * 30 + 5,
               x * 30 + 25, y * 30 + 25,
               fill="purple"
         )

         self.enemigos_graficos.append(nuevo_enemigo)

class Jugador:
   def __init__(self, nombre, modo):
      self.nombre = nombre
      self.modo = modo
      self.stamina = 100
      self.correr = True
      self.puntos = 0
      self.puntaje_e = 0
      self.puntaje_c = 0
   
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
      Muro: "|"}

#Interfaz Gráfica

def iniciar_juego():
   ventana_juego = tk.Toplevel(main)
   ventana_juego.title("Maze Runner")
   ventana_juego.configure(bg="#465360")
   ventana_juego.geometry("600x500")

   titulo_juego = tk.Label(ventana_juego, text="Maze Runner", font=("comic sans ms", 24), bg="#465360", fg="white")
   titulo_juego.place(x=300, y=50, anchor="center")
   etiqueta_modo = tk.Label(ventana_juego, text="Seleccione el modo de juego:", font=("comic sans ms", 14), bg="#465360", fg="white")
   etiqueta_modo.place(x=300, y=120, anchor="center")

   def modo_escape():
      mapa = Mapa(20, 40)
      mapa.crear_mapa()
      mapa.modo_actual = "Escape"
      mapa.mostrar_mapa()
      return

   buton_escape = tk.Button(ventana_juego, text="Modo Escape", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=modo_escape)
   buton_escape.place(x=300, y=200, anchor="center")

   def modo_cazador():
      mapa = Mapa(20, 40)
      mapa.crear_mapa()
      mapa.modo_actual = "Cazador"
      mapa.mostrar_mapa()
      return

   buton_cazador = tk.Button(ventana_juego, text="Modo Cazador", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=modo_cazador)
   buton_cazador.place(x=300, y=260, anchor="center")

   buton_records = tk.Button(ventana_juego, text="Ver Records", font=("comic sans ms", 14), bg="#283845", fg="white", width=15)
   buton_records.place(x=300, y=320, anchor="center")
   buton_salir = tk.Button(ventana_juego, text="Salir", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=ventana_juego.destroy)
   buton_salir.place(x=300, y=380, anchor="center")

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

def iniciar_sesion():
   ventana_sesion = tk.Toplevel(main)
   ventana_sesion.title("Iniciar Sesión")
   ventana_sesion.configure(bg="#465360")
   ventana_sesion.geometry("400x300")
   data = cargar_usuarios()
   opcion_usuario = [u["nombre"] for u in data["usuarios"]]

   etiqueta_usuario = tk.Label(ventana_sesion, text="Nombre de Usuario:", font=("comic sans ms", 14), bg="#465360", fg="white")
   etiqueta_usuario.place(x=200, y=50, anchor="center")
   combo_usuarios = ttk.Combobox(ventana_sesion, font=("comic sans ms", 14), state="readonly", values=opcion_usuario,  width=20)
   combo_usuarios.place(x=200, y=100, anchor="center")
   buton_ingresar = tk.Button(ventana_sesion, text="Ingresar", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=iniciar_juego)
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
main.mainloop()