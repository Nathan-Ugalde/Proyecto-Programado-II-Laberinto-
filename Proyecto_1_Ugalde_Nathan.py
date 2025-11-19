from tkinter import *
from tkinter import messagebox, ttk
import re
import random

#Funciones:

vuelos = [] # Cada vuelo es: vuelo# = [id, codigo, matriz, origen, destino, precio, vendidos]
"""
E: Número de filas (int), Número de columnas (int)
S: Matriz de asientos (lista de listas)
R: -
"""
def matriz_asientos(filas, columnas):
    nula = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(False)
        nula.append(fila)
    return nula
"""
E: Valor a verificar (cualquier tipo)
S: True si es entero, False si no lo es (bool)
R: -
"""
def is_integer(valor):
    try:
        int (valor)
        return True
    except:
        return False
    
"""
E: Índice de la fila (int)
S: Letras correspondientes a la fila (str)
R: -
"""
def indice_letras(k):
    letras = ""
    while k >= 0: 
        resto = k % 26 
        letras = chr(65 + resto) + letras
        k = k // 26 - 1
    return letras

"""
E: Matriz de asientos (lista de listas), fila inicial (int), columna inicial (int), cantidad de asientos a reservar (int)
S: True si hay asientos disponibles, False si no los hay (bool)
R: -
"""
def verificar_asientos(matriz, fila, columna, cantidad):
    if fila < 0 or fila >= len(matriz) or columna < 0 or columna >= len(matriz[0]): # Verifica que existan la fila y la columna.
        return False
    if columna + cantidad > len(matriz[0]): # Verifica que haya la cantidad de asientos a la derecha 
        return False
    for i in range(columna, columna + cantidad):
        if matriz[fila][i] != 0:
            return False
    return True

#Opción 1:

"""
E: -
S: Ventana para crear vuelo (ventana de Tkinter)
R: -
"""
def mostrar_crear_vuelo():
    ventana_boton_1 = Toplevel()
    ventana_boton_1.config(bg="#034113")
    ventana_boton_1.title('Crear vuelo.')
    ventana_boton_1.geometry('400x300')
    filas = StringVar()
    columnas = StringVar()
    """
    E: -
    S: Crea un vuelo y lo agrega a la lista de vuelos (lista)
    R: -
    """
    def crear_vuelo():
        vuelo = []
        v_filas = filas.get()
        v_columnas = columnas.get()
        if is_integer(v_filas) == True and is_integer(v_columnas) == True:
            if int(v_filas) > 50 or int(v_columnas) > 20:
                messagebox.showerror('Error', 'Los valores ingresados de las filas o columnas sobrepaso la capacidad del sitema\nMáximo 50 filas y 20 columnas.')
                return ''
            elif int(v_filas) <= 0 or int(v_columnas) <= 0:
                messagebox.showerror('Error', 'Los valores ingresados de las filas y columnas deben ser mayores que 0.')
                return ''
            else:    
                n_filas = int(v_filas)
                n_columnas = int(v_columnas)
                matriz_acientos = matriz_asientos(n_filas, n_columnas)
                vuelo = ['','','','','','',0]
                vuelo[0] = f'Vuelo{str(len(vuelos)+1)}'
                vuelo[2] = matriz_acientos
                vuelos.append(vuelo)
                messagebox.showinfo('Exito','Vuelo' + str(len(vuelos)) + ' fue creado exitosamente.')
        else:
            messagebox.showerror('Error', 'Los valores ingresados de las filas y columnas deben ser númericos.')

    lbl_filas = Label(ventana_boton_1, text='Ingrese el número de filas', font=('Arial',10), width=25, bg="#76827C")
    lbl_filas.place(relx=0.5, rely=0.2, anchor='center')
    entry_filas = Entry(ventana_boton_1, textvariable=filas)
    entry_filas.place(relx=0.5,rely=0.3, anchor='center')
    lbl_columnas = Label(ventana_boton_1, text='Ingrese el número de columnas', font=('Arial',10), width=25, bg="#76827C")
    lbl_columnas.place(relx=0.5, rely=0.4, anchor='center')
    entry_columnas = Entry(ventana_boton_1, textvariable=columnas)
    entry_columnas.place(relx=0.5,rely=0.5, anchor='center')
    boton_matriz = Button(ventana_boton_1, text='Crear vuelo', font=('Arial',10), width=25, bg="#76827C", command=crear_vuelo)
    boton_matriz.place(relx=0.5, rely=0.8, anchor='center')

#Opción 2:
"""
E: -
S: Ventana para asignar origen/destino y precio de los boletos (ventana de Tkinter)
R: -
"""
def mostrar_asignar():
    ventana_boton_2 = Toplevel()
    ventana_boton_2.config(bg="#034113")
    ventana_boton_2.title('Asignar origen/destino y precio de los boletos.')
    ventana_boton_2.geometry('400x600')
    codigo = StringVar()
    origen = StringVar()
    destino = StringVar()
    precio = StringVar()
    ids = [v[0] for v in vuelos]
    codigos = [v[1] for v in vuelos]
    """
    E: -
    S: Asigna los valores ingresados al vuelo seleccionado (lista)
    R: -
    """
    def asignar_valores():
        v_selecionado = combo_codigo.get()
        v_codigo = codigo.get()
        v_origen = origen.get()
        v_destino = destino.get()
        v_precio = precio.get()
        if v_selecionado == '' or v_codigo == '' or v_origen == '' or v_destino == '' or v_precio == '':
            messagebox.showerror('Error', 'Debe llenar todos los espacios.')
            return ''
        elif not re.fullmatch(r'[A-Z]{2}[0-9]{3}', v_codigo):
            messagebox.showerror("Error", "El código debe tener el formato (ej: AB123).")
            return ''
        try:
            v_precio = int(v_precio)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser numérico entero.")
            return ''
        if v_precio <= 0:
            messagebox.showerror("Error", "El precio debe ser numérico entero mayor que cero.")
            return ''
        elif v_codigo in codigos:
            messagebox.showerror('Error', 'Este código ya esta en uso.')
            return ''
        for item in vuelos:
            if item[0] == v_selecionado:
                if item[1] != '':
                    messagebox.showerror('Error', 'Este vuelo ya tiene código, origen y destino.')
                else:
                    item[1] = v_codigo
                    item[3] = v_origen
                    item[4] = v_destino
                    item[5] = v_precio
                    messagebox.showinfo('Exito', 'Se asignaron los valores al vuelo con el código: ' + v_codigo)

    lbl_combo_codigo = Label(ventana_boton_2, text='Ingrese el ID del vuelo', font=('Arial',10), width=30, bg="#76827C")
    lbl_combo_codigo.place(relx=0.5, y=40, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_2, values=ids, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=80, anchor='center')
    lbl_codigo = Label(ventana_boton_2, text='Ingrese el código del vuelo (Ej: AB123)', font=('Arial',10), width=30, bg="#76827C")
    lbl_codigo.place(relx=0.5, y=120, anchor='center')
    entry_codigo = Entry(ventana_boton_2, textvariable=codigo)
    entry_codigo.place(relx=0.5, y=160, anchor='center')
    lbl_origen = Label(ventana_boton_2, text='Ingrese el lugar de origen del vuelo', font=('Arial',10), width=30, bg="#76827C")
    lbl_origen.place(relx=0.5, y=200, anchor='center')
    entry_origen = Entry(ventana_boton_2, textvariable=origen)
    entry_origen.place(relx=0.5, y=240 , anchor='center')
    lbl_destino = Label(ventana_boton_2, text='Ingrese el destino del vuelo', font=('Arial',10), width=30, bg="#76827C")
    lbl_destino.place(relx=0.5, y=280, anchor='center')
    entry_destino = Entry(ventana_boton_2, textvariable=destino)
    entry_destino.place(relx=0.5, y=320, anchor='center')
    lbl_precio = Label(ventana_boton_2, text='Ingrese el precio del vuelo', font=('Arial',10), width=30, bg="#76827C")
    lbl_precio.place(relx=0.5, y=360, anchor='center')
    entry_precio = Entry(ventana_boton_2, textvariable=precio)
    entry_precio.place(relx=0.5, y=400, anchor='center')
    boton_asignar = Button(ventana_boton_2, text='Asignar valores', font=('Arial',10), width=30, bg="#76827C", command=asignar_valores)
    boton_asignar.place(relx=0.5, y=520, anchor='center')

#Opción 3:
"""
E: -
S: Ventana para ver el estado del vuelo (ventana de Tkinter)
R: -
"""
def mostrar_ver_estado():
    ventana_boton_3 = Toplevel()
    ventana_boton_3.config(bg="#034113")
    ventana_boton_3.title('Ver estado del vuelo')
    ventana_boton_3.geometry('250x250')
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Muestra el estado del vuelo seleccionado (ventana de Tkinter)
    R: -
    """
    def ver_estado():
        v_selecionado = combo_codigo.get()
        for i in range(len(vuelos)):
            if vuelos[i][1] == v_selecionado:
                if vuelos[i][3] == '' or vuelos[i][4] == '' or vuelos[i][5] == '':
                    messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
                    return ''
                else:
                    ventana_estado = Toplevel()
                    matriz = vuelos[i][2]
                    ancho = len(matriz)
                    alto = len(matriz[0])
                    asiento = 30
                    canva = Canvas(ventana_estado, width=alto*asiento + (asiento * 10), height=ancho*asiento + (asiento * 6), bg="#034113")
                    canva.pack()
                    reservados = vuelos[i][6]
                    for k in range(ancho):
                        for j in range(alto): 
                            x1 = (j * asiento) + (asiento*9)
                            y1 = (k * asiento) + asiento
                            x2 = x1 + asiento
                            y2 = y1 + asiento
                            if matriz[k][j] == False:
                                canva.create_rectangle(x1, y1, x2, y2, fill='green', outline='black')
                                canva.create_text(x1 + asiento/2, y1 + asiento/2, text=f"{indice_letras(k)}{j+1}")
                            else:
                                canva.create_rectangle(x1, y1, x2, y2, fill='red', outline='black')
                                canva.create_text(x1 + asiento/2, y1 + asiento/2, text=f"{indice_letras(k)}{j+1}")
                    lbl_avion = Label(ventana_estado, text='Código del vuelo: '+str(vuelos[i][1]), font=('Arial',10), width=25, bg="#034113")
                    lbl_avion.place(x=110, rely=0.3, anchor='center')
                    lbl_reservados = Label(ventana_estado, text='Asientos reservados: '+str(reservados), font=('Arial',10), width=25, bg="#034113")
                    lbl_reservados.place(x=110, rely=0.4, anchor='center')
                    lbl_asientos = Label(ventana_estado, text='Asientos totales: '+ str(ancho*alto), font=('Arial',10), width=25, bg="#034113")
                    lbl_asientos.place(x=110, rely=0.5, anchor='center')
                    lbl_porcentaje = Label(ventana_estado, text='Porcentaje de ocupación: '+ str(round(((reservados/(ancho*alto))*100),2)), font=('Arial',10), width=25, bg="#034113")
                    lbl_porcentaje.place(x=110, rely=0.6, anchor='center')
    lbl_combo_codigo = Label(ventana_boton_3, text='Ingrese el ID del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_combo_codigo.place(relx=0.5, y=40, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_3, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=90, anchor='center')
    boton_ver_estado = Button(ventana_boton_3, text='Ver estado del vuelo',font=('Arial',10), width=25, bg="#76827C", command=ver_estado)
    boton_ver_estado.place(relx=0.5,rely=0.6, anchor='center')

#Opción 4:
"""
E: -
S: Ventana para reservar asiento (ventana de Tkinter)
R: -
"""
def mostrar_reservar_asiento():
    ventana_boton_4 = Toplevel()
    ventana_boton_4.config(bg="#034113")
    ventana_boton_4.title('Ver asientos del vuelo')
    ventana_boton_4.geometry('250x250')
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Permite reservar un asiento en el vuelo seleccionado (modifica la lista de vuelos)
    R: -
    """
    def reservar_asiento():
        v_selecionado = combo_codigo.get()
        for v in vuelos:
            if v[1] == v_selecionado:
                vuelo_selec = v
                if v[3] == '' or v[4] == '' or v[5] == '':
                    messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
                else:
                    ventana_reserva = Toplevel()
                    ventana_reserva.config(bg="#034113")
                    ventana_reserva.title('Ver asientos del vuelo')
                    ventana_reserva.geometry('300x250')
                    asiento = StringVar()
                    asientos = vuelo_selec[2]
                    def reservar():
                        v_asiento = asiento.get()
                        v_asiento = v_asiento.upper()
                        encontrado = False
                        for i in range(len(asientos)):
                            for j in range(len(asientos[0])):
                                if v_asiento == indice_letras(i) + str(j+1):
                                    if asientos[i][j] == False:
                                        asientos[i][j] = True
                                        vuelo_selec[6] += 1
                                        messagebox.showinfo('Asiento reservado', 'El asiento que selecionó ha sido reservado.')
                                        encontrado = True
                                    else:
                                        messagebox.showerror('Asiento reservado', 'El asiento que selecionó ya esta reservado, favor elegir otro.')
                                        encontrado = True
                        if encontrado == False:
                            messagebox.showerror('Asiento no encontrado', 'El asiento que selecionó no se encontró, favor elegir otro.')
                    lbl_asiento = Label(ventana_reserva, text='Ingrese el asiento que desea reservar (Ej: A1)', font=('Arial',10), width=35, bg="#76827C")
                    lbl_asiento.place(relx=0.5, rely=0.2, anchor='center')
                    entry_asiento = Entry(ventana_reserva, textvariable=asiento)
                    entry_asiento.place(relx=0.5,rely=0.4, anchor='center')
                    boton_reservar = Button(ventana_reserva, text='Reservar asiento',font=('Arial',10), width=25, bg="#76827C", command=reservar)
                    boton_reservar.place(relx=0.5,rely=0.6, anchor='center')
    lbl_codigo = Label(ventana_boton_4, text='Ingrese el código del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_codigo.place(relx=0.5, rely=0.2, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_4, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    boton_ver_estado = Button(ventana_boton_4, text='Ver asientos del vuelo',font=('Arial',10), width=25, bg="#76827C",command=reservar_asiento)
    boton_ver_estado.place(relx=0.5,rely=0.6, anchor='center')

#Opción 5:
"""
E: -
S: Ventana para cancelar reserva de asiento (ventana de Tkinter)
R: -
"""
def mostrar_cancelar_reserva():
    ventana_boton_5 = Toplevel()
    ventana_boton_5.config(bg="#034113")
    ventana_boton_5.title('Ver asientos del vuelo')
    ventana_boton_5.geometry('250x250')
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Permite cancelar la reserva de un asiento en el vuelo seleccionado (modifica la lista de vuelos)
    R: -
    """
    def cancelar_reserva():
        v_selecionado = combo_codigo.get()
        for v in vuelos:
            if v[1] == v_selecionado:
                vuel_selec = v
                if v[3] == '' or v[4] == '' or v[5] == '':
                    messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
                else:
                    ventana_cancelar = Toplevel()
                    ventana_cancelar.config(bg="#034113")
                    ventana_cancelar.title('Ver asientos del vuelo')
                    ventana_cancelar.geometry('350x250')
                    asiento = StringVar()
                    asientos = vuel_selec[2]
                    def cancelar():
                        v_asiento = asiento.get()
                        v_asiento = v_asiento.upper()
                        encontrado = False
                        for i in range(len(asientos)):
                            for j in range(len(asientos[0])):
                                if v_asiento == indice_letras(i) + str(j+1):
                                    if asientos[i][j] == True:
                                        asientos[i][j] = False
                                        vuel_selec[6] -= 1
                                        messagebox.showinfo('Cancelar reserva', 'Reserva del asiento '+indice_letras(i) + str(j+1)+ ' cancelada.')
                                        encontrado = True
                                    else:
                                        messagebox.showerror('Cancelar reserva', 'El asiento que selecionó no esta reservado, favor elegir otro.')
                                        encontrado = True
                        if encontrado == False:
                            messagebox.showerror('Asiento no encontrado', 'El asiento que selecionó no se encontró, favor elegir otro.')
                    lbl_asiento = Label(ventana_cancelar, text='Ingrese el asiento para cancelar la reserva (Ej: A1)', font=('Arial',10), width=40, bg="#76827C")
                    lbl_asiento.place(relx=0.5, rely=0.2, anchor='center')
                    entry_asiento = Entry(ventana_cancelar, textvariable=asiento)
                    entry_asiento.place(relx=0.5,rely=0.4, anchor='center')
                    boton_reservar = Button(ventana_cancelar, text='Cancelar reserva',font=('Arial',10), width=25, bg="#76827C", command=cancelar)
                    boton_reservar.place(relx=0.5,rely=0.6, anchor='center')
    lbl_codigo = Label(ventana_boton_5, text='Ingrese el código del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_codigo.place(relx=0.5, rely=0.2, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_5, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    boton_ver_estado = Button(ventana_boton_5, text='Ver asientos del vuelo',font=('Arial',10), width=25, bg="#76827C",command=cancelar_reserva)
    boton_ver_estado.place(relx=0.5,rely=0.6, anchor='center')

#Opción 6:
"""
E: -
S: Ventana para ver estadísticas de ocupación (ventana de Tkinter)
R: -
"""
def mostrar_estadisticas_ocu():
    ventana_boton_6 = Toplevel()
    ventana_boton_6.config(bg="#034113")
    ventana_boton_6.title('Ver estadísticas del vuelo')
    ventana_boton_6.geometry('250x250')
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Muestra las estadísticas de ocupación del vuelo seleccionado (ventana de Tkinter)
    R: -
    """
    def estadisticas_ocu():
        v_seleccionado = combo_codigo.get()
        for v in vuelos:
            if v[1] == v_seleccionado:
                if v[3] == '' or v[4] == '' or v[5] == '':
                    messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
                else:
                    ventana_stats = Toplevel()
                    ventana_stats.config(bg="#034113")
                    ventana_stats.title('Ver asientos del vuelo')
                    ventana_stats.geometry('350x250')
                    reservados = v[6]
                    asientos = len(v[2])*len(v[2][0])
                    porcentaje = round(((reservados / asientos)*100),2)
                    lbl_1 = Label(ventana_stats, text=v[0]+' - '+v[1]+' '+v[3]+' -> '+v[4], font=('Arial', 13), width=30,bg="#034113")
                    lbl_1.place(relx=0.5, rely=0.1, anchor='center')
                    lbl_2 = Label(ventana_stats,  text='Asientos totales: '+str(asientos), font=('Arial', 13), width=25,bg="#034113")
                    lbl_2.place(relx=0.5, rely=0.3, anchor='center')
                    lbl_3 = Label(ventana_stats, text='Reservados: '+str(reservados), font=('Arial', 13), width=25,bg="#034113")
                    lbl_3.place(relx=0.5, rely=0.5, anchor='center')
                    lbl_4 = Label(ventana_stats, text='Porcentaje de ocupación: '+str(porcentaje)+'%', font=('Arial', 13), width=30,bg="#034113")
                    lbl_4.place(relx=0.5, rely=0.7, anchor='center')
    lbl_codigo = Label(ventana_boton_6, text='Ingrese el código del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_codigo.place(relx=0.5, rely=0.2, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_6, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    boton_ver_estado = Button(ventana_boton_6, text='Ver estadísticas de ocupación',font=('Arial',10), width=25, bg="#76827C", command=estadisticas_ocu)
    boton_ver_estado.place(relx=0.5,rely=0.6, anchor='center')

#Opción 7:
"""
E: -
S: Ventana para ver estadísticas de recaudación (ventana de Tkinter)
R: -
"""
def mostrar_estadistica_recau():
    ventana_boton_7 = Toplevel()
    ventana_boton_7.config(bg="#034113")
    ventana_boton_7.title('Ver estadísticas del vuelo')
    ventana_boton_7.geometry('250x250')
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Muestra las estadísticas de recaudación del vuelo seleccionado (ventana de Tkinter)
    R: -
    """
    def estadisticas_ocu():
        v_seleccionado = combo_codigo.get()
        for v in vuelos:
            if v[1] == v_seleccionado:
                if v[3] == '' or v[4] == '' or v[5] == '':
                    messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
                else:
                    ventana_recau = Toplevel()
                    ventana_recau.config(bg="#034113")
                    ventana_recau.title('Ver asientos del vuelo')
                    ventana_recau.geometry('350x250')
                    reservados = v[6]
                    precio = v[5]
                    asientos = len(v[2])*len(v[2][0])
                    porcentaje = round(((reservados / asientos)*100),2)
                    lbl_1 = Label(ventana_recau, text=v[0]+' - '+v[1]+' '+v[3]+' -> '+v[4], font=('Arial', 13), width=30,bg="#034113")
                    lbl_1.place(relx=0.5, rely=0.1, anchor='center')
                    lbl_2 = Label(ventana_recau,  text='Boletos vendidos: '+str(reservados), font=('Arial', 13), width=25,bg="#034113")
                    lbl_2.place(relx=0.5, rely=0.3, anchor='center')
                    lbl_3 = Label(ventana_recau, text='Precio por boleto: '+str(precio), font=('Arial', 13), width=25,bg="#034113")
                    lbl_3.place(relx=0.5, rely=0.5, anchor='center')
                    lbl_4 = Label(ventana_recau, text='Total recaudado: '+str(precio*reservados), font=('Arial', 13), width=30,bg="#034113")
                    lbl_4.place(relx=0.5, rely=0.7, anchor='center')
    lbl_codigo = Label(ventana_boton_7, text='Ingrese el código del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_codigo.place(relx=0.5, rely=0.2, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_7, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    boton_ver_estado = Button(ventana_boton_7, text='Ver estadísticas de recaudación',font=('Arial',10), width=25, bg="#76827C", command=estadisticas_ocu)
    boton_ver_estado.place(relx=0.5,rely=0.6, anchor='center')

#Opción 8:
"""
E: -
S: Ventana para filtrar vuelos por destino (ventana de Tkinter)
R: -
"""
def mostrar_buscar_destino():
    ventana_boton_8 = Toplevel()
    ventana_boton_8.config(bg="#034113")
    ventana_boton_8.title('Filtrar por destino')
    ventana_boton_8.geometry('250x250')
    opciones = []
    for v in vuelos:
        if v[4] not in opciones:
            opciones.append(v[4])
    """
    E: -
    S: Filtra los vuelos por destino seleccionado (ventana de Tkinter)
    R: -
    """
    def buscar_destino():
        d_seleccionado = combo_codigo.get()
        if d_seleccionado == '':
            messagebox.showerror('Error', 'Debe seleccionar un destino.')
            return ''
        ventana_buscar = Toplevel()
        ventana_buscar.title('Vuelos con destino '+d_seleccionado)
        cantidad = 0
        alto = 100
        largo = 450
        for v in vuelos:
            if v[4] == d_seleccionado:
                cantidad += 1
        canva = Canvas(ventana_buscar, width=largo, height=(alto*cantidad)+alto, bg="#034113")
        canva.create_text(largo/2, alto/2, text=f'Vuelos hacia {d_seleccionado}:')
        canva.pack()
        x = 0
        y = 1
        for v in vuelos:
            if v[4] == d_seleccionado:
                x1 = x * largo
                y1 = y * alto
                x2 = x1 + largo
                y2 = y1 + alto
                y += 1
                canva.create_rectangle(x1, y1, x2, y2, fill="#034113")
                canva.create_text(x1 + largo/2, y1 + alto/2, text=f"{v[0]}, [asientos disponibles {(len(v[2])*len(v[2][0])-v[6])}]")

    lbl_codigo = Label(ventana_boton_8, text='Ingrese el código del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_codigo.place(relx=0.5, rely=0.2, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_8, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    boton_ver_estado = Button(ventana_boton_8, text='Filtrar por destino',font=('Arial',10), width=25, bg="#76827C", command=buscar_destino)
    boton_ver_estado.place(relx=0.5,rely=0.6, anchor='center')

#Opción 9:
"""
E: -
S: Ventana para mostrar los vuelos disponibles (ventana de Tkinter)
R: -
"""
def mostrar_vuelos():
    ventana_boton_9 = Toplevel()
    ventana_boton_9.config(bg="#034113")
    ventana_boton_9.title('Vuelos disponibles')
    disponibles = []
    cantidad = 0
    alto = 80
    largo = 450
    for v in vuelos:
        total = len(v[2])*len(v[2][0])
        if total != v[6]:
            if v[1] == '':
                cantidad -= 1
            disponibles.append(v)
            cantidad += 1
    canva = Canvas(ventana_boton_9, width=largo, height=(alto*cantidad)+alto, bg="#034113")
    canva.create_text(largo/2, alto/2, text=f'------ Vuelos disponibles ------')
    canva.pack()
    x = 0
    y = 1
    for item in disponibles:
        if item[1] == '':
            continue
        total = len(item[2])*len(item[2][0])
        x1 = x * largo
        y1 = y * alto
        x2 = x1 + largo
        y2 = y1 + alto
        y += 1
        canva.create_rectangle(x1, y1, x2, y2, fill="#034113")
        canva.create_text(x1 + largo/2, y1 + alto/5, text=f"{item[0]} - {item[1]} {item[3]} --> {item[4]}")
        canva.create_text(x1 + largo/2, y1 + alto/2.25, text=f"Precio: {item[5]}")
        canva.create_text(x1 + largo/2, y1 + alto/1.5, text=f"Asientos disponibles: {total - item[6]}")

#Opción 10:
"""
E: -
S: Ventana para reservar asientos consecutivos (ventana de Tkinter)
R: -
"""
def mostrar_reservar_con():
    ventana_boton_10 = Toplevel()
    ventana_boton_10.config(bg="#034113")
    ventana_boton_10.title('Reservar consecutivos')
    ventana_boton_10.geometry('500x500')
    pos = StringVar()
    cantidad = StringVar()
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Ventana para reservar asientos consecutivos (ventana de Tkinter)
    R: -
    """
    def reservar_con():
        v_pos = pos.get()
        v_pos = v_pos.upper()
        v_cantidad = cantidad.get()
        v_seleccionado = combo_codigo.get()
        if v_seleccionado == '':
            messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
            return ''
        if is_integer(v_cantidad) == False:
            messagebox.showerror('Error', 'El valor de la cantidad de asientos debe ser un valor númerico.')
            return ''
        elif int(v_cantidad) < 2:
            messagebox.showerror('Error', 'Para usar esta función debe reservar al menos 2 aientos.')
            return ''
        for v in vuelos:
            if v[1] == v_seleccionado:
                matriz = v[2]
                for i in range(len(v[2])):
                    for j in range(len(v[2][0])):
                        if v_pos == chr(65+i) + str(j+1) :
                            fila = i
                            columna = j
                            if verificar_asientos(matriz, fila, columna, int(v_cantidad)) == False:
                                messagebox.showerror('Error', 'No hay suficientes asientos disponibles.')
                                return ''
                            else:
                                reservados = ''
                                for n in range(int(v_cantidad)):
                                    if n == v_cantidad:
                                        break
                                    else:
                                        matriz[i][j+n] = 1
                                        asiento = indice_letras(i) + str(n+j+1)
                                        reservados += (asiento+', ')
                                        v[6] =+ int(v_cantidad)
                                messagebox.showinfo('Exito', 'Reservados exitosamente: '+ reservados[:-2] )        

    lbl_codigo = Label(ventana_boton_10, text='Ingrese el código del vuelo', font=('Arial',10), width=40, bg="#76827C")
    lbl_codigo.place(relx=0.5, y=50, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_10, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    lbl_pos = Label(ventana_boton_10, text='Ingrese la posición del asiento', font=('Arial',10), width=40, bg="#76827C")
    lbl_pos.place(relx=0.5,y=150, anchor='center')
    entry_pos = Entry(ventana_boton_10, textvariable=pos)
    entry_pos.place(relx=0.5,y=200, anchor='center')
    lbl_cantidad = Label(ventana_boton_10, text='Ingrese la cantidad de asientos que desea reservar', font=('Arial',10), width=40, bg="#76827C")
    lbl_cantidad.place(relx=0.5,y=250, anchor='center')
    entry_cantidad = Entry(ventana_boton_10, textvariable=cantidad)
    entry_cantidad.place(relx=0.5,y=300, anchor='center')
    boton_reservar = Button(ventana_boton_10, text='Reservar asientos',font=('Arial',10), width=40, bg="#76827C", command=reservar_con)
    boton_reservar.place(relx=0.5,rely=0.8, anchor='center')

#Opción 11:
"""
E: -
S: Ventana para simular venta masiva (ventana de Tkinter)
R: -
"""
def mostrar_simular():
    ventana_boton_11 = Toplevel()
    ventana_boton_11.config(bg="#034113")
    ventana_boton_11.title('Simular venta masiva')
    ventana_boton_11.geometry('350x350')
    opciones = [v[1] for v in vuelos]
    porcentaje = StringVar()
    """
    E: -
    S: Ventana para simular venta masiva (ventana de Tkinter)
    R: -
    """
    def simular_venta():
        v_porcentaje = porcentaje.get()
        v_seleccionado = combo_codigo.get()
        if v_seleccionado == '':
            messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
            return ''
        elif is_integer(v_porcentaje) == False:
            messagebox.showerror('Error', 'Debe ingresar un valor númerico.')
            return ''
        elif v_porcentaje == '':
            messagebox.showerror('Error', 'Debe ingresar un porcentaje entre 1 y 100.')
            return ''
        elif int(v_porcentaje) < 1 or int(v_porcentaje) > 100:
            messagebox.showerror('Error', 'Debe ingresar un porcentaje entre 1 y 100.')
            return ''
        for v in vuelos:
            if v_seleccionado == v[1]:
                total = len(v[2]) * len(v[2][0])
                ocupados = 0
                porcentaje_a = (v[6]/total) * 100
                if porcentaje_a == int(v_porcentaje):
                    messagebox.showinfo('Exito', 'Venta simulada realizada, puede verificarlo en la opcion 3.')
                    return ''
                while (ocupados/total) * 100 < int(v_porcentaje):
                    i = random.randint(0, len(v[2])-1)
                    j = random.randint(0, len(v[2][0])-1)
                    if v[2][i][j] == False:
                        v[2][i][j] = True
                        v[6] += 1
                        ocupados += 1
                    else:
                        pass
                messagebox.showinfo('Exito', 'Venta simulada realizada, puede verificarlo en la opcion 3.')

    lbl_codigo = Label(ventana_boton_11, text='Ingrese el código del vuelo', font=('Arial',10), width=30, bg="#76827C")
    lbl_codigo.place(relx=0.5, y=50, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_11, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    lbl_porcentaje = Label(ventana_boton_11, text='Ingrese el porcentaje que desea simular', font=('Arial',10), width=30, bg="#76827C")
    lbl_porcentaje.place(relx=0.5, y=150, anchor='center')
    entry_porcentaje = Entry(ventana_boton_11, textvariable=porcentaje)
    entry_porcentaje.place(relx=0.5, y=200, anchor='center')
    boton_simular = Button(ventana_boton_11, text='Simular venta masiva', font=('Arial',10), width=30, bg="#76827C", command=simular_venta)
    boton_simular.place(relx=0.5, y=270, anchor='center')

#Opción 12:
"""
E: -
S: Ventana para reiniciar vuelo (ventana de Tkinter)
R: -
"""
def mostrar_reiniciar():
    ventana_boton_12 = Toplevel()
    ventana_boton_12.config(bg="#034113")
    ventana_boton_12.title('Ver estadísticas del vuelo')
    ventana_boton_12.geometry('250x250')
    opciones = [v[1] for v in vuelos]
    """
    E: -
    S: Ventana para reiniciar vuelo (ventana de Tkinter)
    R: -
    """
    def reiniciar():
        v_seleccionado = combo_codigo.get()
        if v_seleccionado == '':
            messagebox.showerror('Error', 'Debe seleccionar un vuelo existente.')
            return ''
        for v in vuelos:
            if v[1] == v_seleccionado:
                if v[6] != 0:
                    filas = len(v[2])
                    columnas = len(v[2][0])
                    v[2] = matriz_asientos(filas, columnas)
                    v[6] = 0
                    messagebox.showinfo('Exito', f'El vuelo {v[1]} ha sido reiniciado.')
                else:
                    messagebox.showerror('Error', 'El vuelo que selecciono ya se encuenntra vacío.')

    lbl_codigo = Label(ventana_boton_12, text='Ingrese el código del vuelo', font=('Arial',10), width=25, bg="#76827C")
    lbl_codigo.place(relx=0.5, rely=0.2, anchor='center')
    combo_codigo = ttk.Combobox(ventana_boton_12, values=opciones, state='readonly', font=('Arial',10), width=15)
    combo_codigo.place(relx=0.5,y=100, anchor='center')
    boton_reiniciar_vuelo = Button(ventana_boton_12, text='Reiniciar vuelo',font=('Arial',10), width=25, bg="#76827C", command=reiniciar)
    boton_reiniciar_vuelo.place(relx=0.5,rely=0.6, anchor='center')

#Opción 13:
"""
E: -
S: Cierra la ventana principal y termina el programa
R: -
"""
def salir():
    ventana_principal.quit()

#interfaz grafica:
ventana_principal = Tk()
ventana_principal.config(bg="#034113")
ventana_principal.title('Ventana Principal')
ventana_principal.geometry('400x1900')
lbl_menu = Label(ventana_principal,text='MENÚ PRINCIPAL', font=('Arial', 20), bg="#034113")
lbl_menu.place(relx=0.5,rely=0.08, anchor='center', )

#Botones:
boton_crear_vuelo = Button(ventana_principal, text='1. Crear vuelo.', font=('Arial', 10), width=30, height=1, bg="#76827C", command=mostrar_crear_vuelo)
boton_crear_vuelo.place(relx=0.5,rely=0.15, anchor='center', )
boton_asignar = Button(ventana_principal, text='2. Asignar origen/destino y precio a vuelo.', font=('Arial', 10),width=30, height=1,  bg='#76827C', command=mostrar_asignar)
boton_asignar.place(relx=0.5,rely=0.2, anchor='center', )
boton_estado = Button(ventana_principal, text='3. Ver estado del vuelo.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_ver_estado)
boton_estado.place(relx=0.5,rely=0.25, anchor='center', )
boton_reservar_asiento = Button(ventana_principal, text='4. Reservar asiento.', font=('Arial', 10),width=30, height=1, bg='#76827C', command=mostrar_reservar_asiento)
boton_reservar_asiento.place(relx=0.5,rely=0.3, anchor='center', )
boton_cancelar = Button(ventana_principal, text='5. Cancelar reserva.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_cancelar_reserva)
boton_cancelar.place(relx=0.5, rely=0.35, anchor='center')
boton_estad_ocupacion = Button(ventana_principal, text='6. Ver estado de ocupación.', font=('Arial', 10),width=30, height=1, bg='#76827C', command=mostrar_estadisticas_ocu)
boton_estad_ocupacion.place(relx=0.5, rely=0.4, anchor='center')
boton_estad_recau = Button(ventana_principal, text='7. Ver estadisticas de recaudación.', font=('Arial',10), width=30, height=1, bg='#76827C', command=mostrar_estadistica_recau)
boton_estad_recau.place(relx=0.5, rely=0.45, anchor='center')
boton_vuelos_destinos = Button(ventana_principal, text='8. Buscar vuelos por destino.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_buscar_destino)
boton_vuelos_destinos.place(relx=0.5, rely=0.5, anchor='center')
boton_vuelos_disp = Button(ventana_principal, text='9. Ver vuelos disponibles.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_vuelos)
boton_vuelos_disp.place(relx=0.5, rely=0.55, anchor='center')
boton_resevar_conse = Button(ventana_principal, text='10. Reservar varios asientos consecutivos.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_reservar_con)
boton_resevar_conse.place(relx=0.5,  rely=0.6, anchor='center')
boton_simular = Button(ventana_principal, text='11. Simular venta masiva.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_simular)
boton_simular.place(relx=0.5, rely=0.65, anchor='center')
boton_reiniciar = Button(ventana_principal, text='12. Reiniciar vuelo.', font=('Arial', 10), width=30, height=1, bg='#76827C', command=mostrar_reiniciar)
boton_reiniciar.place(relx=0.5, rely=0.7, anchor='center')
boton_salir = Button(ventana_principal, text='13. Salir', font=('Arial', 10), width=30, height=1, bg='#76827C', command=salir)
boton_salir.place(relx=0.5, rely=0.75, anchor='center')

ventana_principal.mainloop()
