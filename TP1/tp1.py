#python -m pip install -U pip
#python -m pip install -U matplotlib
#pip install imagio

import tkinter
from tkinter import filedialog, StringVar, OptionMenu, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import imageio.v2 as imageio
import numpy as np

# Variables globales
rutaImagen = None
canvasOriginal = None
canvasProcesado = None

# Métodos de procesamiento
def procesarBlancoNegro(imagen):
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imagen[:, :, 0], cmap='gray')
    ax.set_title("Blanco y Negro")
    ax.axis('off')
    return fig

def procesarCanalRojo(imagen):
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imagen[:, :, 0], cmap='Reds')
    ax.set_title("Canal Rojo")
    ax.axis('off')
    return fig

def procesarCanalVerde(imagen):
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imagen[:, :, 1], cmap='Greens')
    ax.set_title("Canal Verde")
    ax.axis('off')
    return fig

def procesarCanalAzul(imagen):
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imagen[:, :, 2], cmap='Blues')
    ax.set_title("Canal Azul")
    ax.axis('off')
    return fig

def procesarLuminanciaSaturacion(imagen, a, b):
    fig, ax = plt.subplots(figsize=(4, 2))
    
    yiq = np.zeros(imagen.shape)
    yiq[:,:,0] = np.clip(0.299 * imagen[:,:,0] + 0.587 * imagen[:,:,1] + 0.114 * imagen[:,:,2],0,1)
    yiq[:,:,1] = np.clip(0.59 * imagen[:,:,0] + -0.27 * imagen[:,:,1] + -0.32 * imagen[:,:,2],-0.5957,0.5957)
    yiq[:,:,2] = np.clip(0.21 * imagen[:,:,0] + -0.52 * imagen[:,:,1] + 0.31 * imagen[:,:,2],-0.5226,0.5226)
    
    y = yiq[:,:,0]
    i = yiq[:,:,1]
    q = yiq[:,:,2]
    
    y1 = np.clip(a*y,0,1)
    i2 = np.clip(b*i,-0.5957,0.5957)
    q2 = np.clip(b*q,-0.5226,0.5226)

    yiq1 = np.zeros(yiq.shape)
    yiq1[:,:,0] = y1
    yiq1[:,:,1] = i2
    yiq1[:,:,2] = q2    
    
    r1g1b1 = np.zeros(yiq1.shape)

    r1g1b1[:,:,0] = np.clip(1 * yiq1[:,:,0] +  0.9663 * yiq1[:,:,1] + 0.6210 * yiq1[:,:,2],0,1)
    r1g1b1[:,:,1] = np.clip(1 * yiq1[:,:,0] + -0.2721 * yiq1[:,:,1] + -0.6474 * yiq1[:,:,2],0,1)
    r1g1b1[:,:,2] = np.clip(1 * yiq1[:,:,0] + -1.1070 * yiq1[:,:,1] + 1.7046 * yiq1[:,:,2],0,1)

    ax.imshow(r1g1b1)
    ax.set_title(f"Luminancia a={a}, Saturacion b={b}")
    ax.axis('off')
    return fig

def importarImagen():
    global rutaImagen, canvasOriginal, canvasProcesado
    rutaImagen = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    if rutaImagen:
        etiqueta["text"] = "Imagen importada correctamente!"
        mostrarImagen()  # Mostrar automáticamente la imagen cargada

def mostrarImagen():
    global rutaImagen, canvasOriginal
    if rutaImagen:
        imagen = imageio.imread(rutaImagen)
        imagen = np.clip(imagen /255.,0.,1.)
        
        # Destruir canvas anterior si existe
        if canvasOriginal:
            canvasOriginal.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.imshow(imagen)
        ax.set_title("Imagen Original")
        ax.axis('off')

        canvasOriginal = FigureCanvasTkAgg(fig, master=frameImagenOriginal)
        canvasOriginal.get_tk_widget().pack(expand=True)
        canvasOriginal.draw()
         
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"
        
def procesarImagen():
    global rutaImagen, canvasProcesado
    if rutaImagen:
        
        imagen = imageio.imread(rutaImagen)
        imagen = np.clip(imagen /255.,0.,1.)

        # Selección del tipo de procesamiento
        if tipoProcesamiento.get() == "Blanco y Negro":
            fig = procesarBlancoNegro(imagen)
        elif tipoProcesamiento.get() == "Canal Rojo":
            fig = procesarCanalRojo(imagen)
        elif tipoProcesamiento.get() == "Canal Verde":
            fig = procesarCanalVerde(imagen)
        elif tipoProcesamiento.get() == "Canal Azul":
            fig = procesarCanalAzul(imagen)
        elif tipoProcesamiento.get() == "Luminancia y Saturacion":
            # Mostrar diálogos en primer plano
            ventana.grab_set()
            a = simpledialog.askfloat("Luminancia", "Introduce el valor para 'a':", parent=ventana)
            b = simpledialog.askfloat("Saturacion", "Introduce el valor para 'b':", parent=ventana)
            ventana.grab_release()
            if a is not None and b is not None:
                fig = procesarLuminanciaSaturacion(imagen, a, b)
            else:
                etiqueta["text"] = "Operación cancelada."

        # Destruir canvas anterior si existe
        if canvasProcesado:
            canvasProcesado.get_tk_widget().destroy()

        canvasProcesado = FigureCanvasTkAgg(fig, master=frameImagenProcesada)
        canvasProcesado.get_tk_widget().pack(expand=True)
        canvasProcesado.draw()
        
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"

# Tkinter
ventana = tkinter.Tk()
ventana.geometry("1200x700")
ventana.resizable(False, False)

# Crear un marco para la imagen original
frameImagenOriginal = tkinter.Frame(ventana, width=960, height=250, bg="white")
frameImagenOriginal.pack(pady=10)

# Crear un marco para la imagen procesada
frameImagenProcesada = tkinter.Frame(ventana, width=960, height=250, bg="white")
frameImagenProcesada.pack(pady=10)

# Crear un frame para los botones y la etiqueta
frameControles = tkinter.Frame(ventana)
frameControles.pack(pady=10)

# Crear un botón para cargar la imagen
botonCargar = tkinter.Button(frameControles, text="Cargar Imagen", command=importarImagen)
botonCargar.grid(row=0, column=0, padx=10)

# Crear un botón para procesar la imagen
botonProcesar = tkinter.Button(frameControles, text="Procesar Imagen", command=procesarImagen)
botonProcesar.grid(row=0, column=2, padx=10)

# Etiqueta para mostrar mensajes de estado
etiqueta = tkinter.Label(frameControles, text="")
etiqueta.grid(row=1, columnspan=3, pady=3)

# Crear un menú desplegable para seleccionar el tipo de procesamiento
tipoProcesamiento = StringVar(value="Blanco y Negro")
opcionesProcesamiento = ["Blanco y Negro", "Canal Rojo", "Canal Verde", "Canal Azul", "Luminancia y Saturacion"]
menuProcesamiento = OptionMenu(frameControles, tipoProcesamiento, *opcionesProcesamiento)
menuProcesamiento.grid(row=0, column=1, padx=10)

ventana.mainloop()