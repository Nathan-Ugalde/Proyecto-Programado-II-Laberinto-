#Importaciones
import random
import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import time
import json
import os
#TODO: Mostrar top5, stamina visual, niveles de dificultad, Cooldown movimientos de juagor, hacer que las ventanas de iniciar sesión y dificultad se cierren despues de seleccionar
#TODO: Validar si un puntaje se sobrescribe

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

def registrar_usuario(nombre): #😎
    
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
#--------Componente del jugador--------#
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
         self.puntaje_c = self.puntos
      else:
         self.puntaje_e = self.puntos

#--------Coponentes del enemigo--------#
class Enemigo:
   def __init__(self, y, x, mapa, canvas, modo):
      self.y = y
      self.x = x
      self.mapa = mapa
      self.canvas = canvas
      self.modo = modo  # "Escape" o "Cazador"
      self.grafico = self.canvas.create_rectangle(x * 30 + 5, y * 30 + 5,x * 30 + 25, y * 30 + 25,fill="purple")


   def mover(self):
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
                  self.canvas.after(2000, reaparecer)
               return

         if (self.y, self.x) == self.mapa.jugador_pos:
            messagebox.showinfo("¡Has sido atrapado!", "¡Un enemigo te ha atrapado!")
            self.mapa.ventana.destroy()

   def eliminar(self):
      self.canvas.delete(self.grafico)

class Trampa:
   def __init__(self, y, x, canvas):
      self.y = y
      self.x = x
      self.activa = True
      self.canvas = canvas
        
      self.grafico = self.canvas.create_rectangle(x*30+10, y*30+10,x*30+20, y*30+20, fill="yellow")

   def desactivar(self):
      self.activa = False
      self.canvas.delete(self.grafico)

   def esta_en_posicion(self, y, x):
      return self.activa and self.y == y and self.x == x

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
   def __init__(self, jugador, dificultad, filas=20, columnas=40):
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
      self.tiempo_cazador = time.time() + 150  # 150 segundos para el modo Cazador

   def crear_mapa(self):
      tipos = [Camino, Lianas, Tuneles, Muro]
      pesos = [55,15,15,15]

      while True:
         self.matriz = [[random.choices(tipos, weights=pesos)[0]() 
                      for _ in range(self.columnas)] for _ in range(self.filas)]

         self.matriz[0][0] = Tuneles()
         self.matriz[self.filas-1][self.columnas-1] = Camino()

         if self.hay_camino_jugador_escape() and self.hay_camino_jugador_cazador():
            break

   def mostrar_mapa(self):
      self.ventana = tk.Tk()
      self.ventana.title("Maze Runner")

      tam = 30
      self.canvas = tk.Canvas(self.ventana, width=self.columnas*tam, height=self.filas*tam)
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

      # JUGADOR
      self.jugador_grafico = self.canvas.create_oval(5, 5, 25, 25, fill="blue")
      #-----Movimiento-----#
      self.ventana.bind("<Up>", lambda e: self.mover_jugador(0, -1))
      self.ventana.bind("<Down>", lambda e: self.mover_jugador(0, 1))
      self.ventana.bind("<Left>", lambda e: self.mover_jugador(-1, 0))
      self.ventana.bind("<Right>", lambda e: self.mover_jugador(1, 0))
      self.ventana.bind("<space>", lambda e: self.colocar_trampa())

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
      def loop():
         self.mover_enemigos()
         self.ventana.after(velocidad, loop) #Entre mayor sea el número más lentos son los enemigo
      loop()
      self.ventana.mainloop()

   def mover_enemigos(self):
      for enemigo in self.enemigos[:]:
         enemigo.mover()

   def colocar_enemigos(self, cantidad):
      posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas)
         if isinstance(self.matriz[y][x], Camino)
         and (y,x) not in [self.entrada, self.salida]
         and (y,x) != self.jugador_pos]

      random.shuffle(posiciones_validas)

      for i in range(min(cantidad, len(posiciones_validas))):
         y, x = posiciones_validas[i]
         enemigo = Enemigo(y, x, self, self.canvas, self.modo_actual)
         self.enemigos.append(enemigo)

   def colocar_enemigo_aleatorio(self):
    posiciones_validas = [(y, x) for y in range(self.filas) for x in range(self.columnas)
        if isinstance(self.matriz[y][x], Camino)
        and (y,x) not in [self.entrada, self.salida]
        and (y,x) != self.jugador_pos]
    if posiciones_validas:
        y, x = random.choice(posiciones_validas)
        enemigo = Enemigo(y, x, self, self.canvas, self.modo_actual)
        self.enemigos.append(enemigo)

   def mover_jugador(self, px, py):
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
      if self.dificultad == 'Fácil':
         max_puntos_E = 1500 #2:30 minutos
         puntos_x_kill = 30
         perdida_x_escape = 60
      elif self.dificultad == 'Medio':
         max_puntos_E = 1200 #2 minutos
         puntos_x_kill = 40
         perdida_x_escape = 80
      elif self.dificultad == 'Difícil':
         max_puntos_E = 900 #1:30 minutos
         puntos_x_kill = 50
         perdida_x_escape = 100
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
            puntos_tiempo = max(0, max_puntos_tiempo - tiempo_total * 10)
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
               print("Enemigo eliminado. Puntos:", self.jugador.puntos)
            else:
               messagebox.showinfo("¡Atrapado!", "Un enemigo te atrapó")
               self.ventana.destroy()
         if (enemigo.y, enemigo.x) == self.salida:
            if self.modo_actual == "Cazador":
               enemigo.eliminar()
               self.enemigos.remove(enemigo)
               # Actualiza la BD con el puntaje total de la partida en modo Cazador
               self.jugador.perder_puntos(perdida_x_escape)
               print("Enemigo escapó. Puntos:", self.jugador.puntos)
      
      # Verificar condiciones de fin del modo Cazador
      if self.modo_actual == "Cazador":
         # Si no quedan enemigos
         if not self.enemigos:
            self.jugador.calcular_puntaje(self.modo_actual)
            if self.jugador.puntaje_c < 0:
                self.jugador.puntaje_c = 0
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
               messagebox.showinfo("Game over", f"Se acabó el tiempo para atrapar enemigos.\nLa dificultad de juego fue: {self.dificultad}\nPuntaje final: {self.jugador.puntaje_c}")
               self.ventana.destroy()
               

   def hay_camino_jugador_escape(self):
      return self.bfs(lambda c: c.permite_jugador())

   def hay_camino_jugador_cazador(self):
      return self.bfs(lambda c: c.permite_enemigo())

   def bfs(self, permite_func):
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

   def modo_escape():
      mapa = Mapa(usuario, dificultad, 20, 40)
      mapa.crear_mapa()
      mapa.modo_actual = "Escape"
      mapa.mostrar_mapa()
      return

   buton_escape = tk.Button(ventana_juego, text="Modo Escape", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=modo_escape)
   buton_escape.place(x=300, y=200, anchor="center")

   def modo_cazador():
      mapa = Mapa(usuario, dificultad, 20, 40)
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
   if opcion_usuario == []:
      messagebox.showwarning("Error", "No hay usuarios registrados. Cree uno primero.")
      ventana_sesion.destroy()
      return
   
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
      buton_seleccionar = tk.Button(ventana_dificultad, text="Seleccionar", font=("comic sans ms", 14), bg="#283845", fg="white", width=15, command=lambda: iniciar_juego(combo_usuarios.get(), combo_dificultad.get()))
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
main.mainloop()