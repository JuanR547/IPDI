#python -m pip install -U pip
#python -m pip install -U matplotlib
#pip install imagio

import tkinter
from tkinter import filedialog, StringVar, OptionMenu
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import imageio.v2 as imageio
import numpy as np

# Variables globales
rutaImagenA = None
rutaImagenB = None
canvasA = None
canvasB = None
canvasC = None

# Métodos
def cargarImagen(canvas, variableRuta, frame):
    global rutaImagenA, rutaImagenB
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    
    if ruta:
        etiqueta["text"] = "Imagen importada correctamente!"
        if variableRuta == 'A':
            rutaImagenA = ruta
        elif variableRuta == 'B':
            rutaImagenB = ruta
        mostrarImagen(ruta, canvas, frame)

def mostrarImagen(ruta, canvas, frame):
    if ruta:
        imagen = imageio.imread(ruta)
        imagen = np.clip(imagen / 255., 0., 1.)
        
        if canvas:
            canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.imshow(imagen)
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(expand=True)
        canvas.draw()
         
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"

def procesarImagen(rutaA, rutaB, frame):
    global canvasC
    if rutaA and rutaB:
        # Leer y procesar las imágenes
        imagenA = imageio.imread(rutaA)
        imagenA = np.clip(imagenA / 255., 0., 1.)

        imagenB = imageio.imread(rutaB)
        imagenB = np.clip(imagenB / 255., 0., 1.)

        # Realizar la operación según selección
        if tipoOperacion.get() == "Suma" and tipoFormato.get() == "Clampeo":
            fig = sumaClampeo(imagenA, imagenB)
        elif tipoOperacion.get() == "Suma" and tipoFormato.get() == "Promedio":
            fig = sumaPromedio(imagenA, imagenB)    
        elif tipoOperacion.get() == "Resta" and tipoFormato.get() == "Clampeo":
            fig = restaClampeo(imagenA, imagenB)    
        elif tipoOperacion.get() == "Resta" and tipoFormato.get() == "Promedio":
            fig = restaPromedio(imagenA, imagenB) 
        elif tipoOperacion.get() == "Suma" and tipoFormato.get() == "YIQ Clampeo":
            fig = sumaYiqClampeo(imagenA, imagenB) 
        elif tipoOperacion.get() == "Suma" and tipoFormato.get() == "If Lighter":
            fig = sumaIfLighter(imagenA, imagenB)
        elif tipoOperacion.get() == "Suma" and tipoFormato.get() == "If Darker":
            fig = sumaIfDarker(imagenA, imagenB)
            
        else:
            etiqueta["text"] = "No es posible realizar esa selección!"
            return

        # Limpiar el canvas previo
        if canvasC:
            canvasC.get_tk_widget().destroy()

        # Mostrar el resultado en el canvas
        canvasC = FigureCanvasTkAgg(fig, master=frame)
        canvasC.get_tk_widget().pack(expand=True)
        canvasC.draw()

    else:
        etiqueta["text"] = "Primero debes cargar las imágenes!"
        
def rgbToYiq(rgb):
    yiq = np.zeros(rgb.shape)
    
    yiq[:,:,0] = np.clip(0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2],0,1)
    yiq[:,:,1] = np.clip(0.59 * rgb[:,:,0] + -0.27 * rgb[:,:,1] + -0.32 * rgb[:,:,2],-0.5957,0.5957)
    yiq[:,:,2] = np.clip(0.21 * rgb[:,:,0] + -0.52 * rgb[:,:,1] + 0.31 * rgb[:,:,2],-0.5226,0.5226)
    
    return yiq

def yiqToRgb(yiq):
    rgb = np.zeros(yiq.shape)

    rgb[:,:,0] = np.clip(1 * yiq[:,:,0] +  0.9663 * yiq[:,:,1] + 0.6210 * yiq[:,:,2],0,1)
    rgb[:,:,1] = np.clip(1 * yiq[:,:,0] + -0.2721 * yiq[:,:,1] + -0.6474 * yiq[:,:,2],0,1)
    rgb[:,:,2] = np.clip(1 * yiq[:,:,0] + -1.1070 * yiq[:,:,1] + 1.7046 * yiq[:,:,2],0,1)
    
    return rgb

def sumaClampeo(imA, imB):
    imC = np.zeros(imA.shape)

    imC[:, :, 0] = np.clip(imA[:, :, 0] + imB[:, :, 0], 0., 1.)
    imC[:, :, 1] = np.clip(imA[:, :, 1] + imB[:, :, 1], 0., 1.)
    imC[:, :, 2] = np.clip(imA[:, :, 2] + imB[:, :, 2], 0., 1.)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imC)
    ax.axis('off')

    return fig

def sumaPromedio(imA, imB):
    imC = np.zeros(imA.shape)

    imC [:,:,0] = np.clip((imA[:,:,0] + imB[:,:,0])/2,0.,1.)
    imC [:,:,1] = np.clip((imA[:,:,1] + imB[:,:,1])/2,0.,1.)
    imC [:,:,2] = np.clip((imA[:,:,2] + imB[:,:,2])/2,0.,1.)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imC)
    ax.axis('off')

    return fig

def restaClampeo(imA, imB):
    imC = np.zeros(imA.shape)

    imC [:,:,0] = np.clip(imA[:,:,0] - imB[:,:,0],0.,1.)
    imC [:,:,1] = np.clip(imA[:,:,1] - imB[:,:,1],0.,1.)
    imC [:,:,2] = np.clip(imA[:,:,2] - imB[:,:,2],0.,1.)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imC)
    ax.axis('off')

    return fig

def restaPromedio(imA, imB):
    imC = np.zeros(imA.shape)

    imC [:,:,0] = np.clip((imA[:,:,0] - imB[:,:,0])/2,0.,1.)
    imC [:,:,1] = np.clip((imA[:,:,1] - imB[:,:,1])/2,0.,1.)
    imC [:,:,2] = np.clip((imA[:,:,2] - imB[:,:,2])/2,0.,1.)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(imC)
    ax.axis('off')

    return fig

def sumaYiqClampeo(imA, imB):
    
    yiqA = rgbToYiq(imA)
    yiqB = rgbToYiq(imB)
    
    yiqC = np.zeros(yiqA.shape)

    yiqC [:,:,0] = np.clip((yiqA[:,:,0] + yiqB[:,:,0]),0.,1.)

    yiqC [:,:,1] = ((yiqA[:,:,0] * yiqA[:,:,1]) + (yiqB[:,:,0] * yiqB[:,:,1])) / (yiqA [:,:,0] + yiqB [:,:,0])
    yiqC [:,:,2] = ((yiqA[:,:,0] * yiqA[:,:,2]) + (yiqB[:,:,0] * yiqB[:,:,2])) / (yiqA [:,:,0] + yiqB [:,:,0])
    
    rgbC = yiqToRgb(yiqC)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbC)
    ax.axis('off')

    return fig

def sumaYiqPromedio(imA, imB):
    
    yiqA = rgbToYiq(imA)
    yiqB = rgbToYiq(imB)
    
    yiqC = np.zeros(yiqA.shape)

    yiqC [:,:,0] = np.clip((yiqA[:,:,0] + yiqB[:,:,0]) / 2,0.,1.)

    yiqC [:,:,1] = ((yiqA[:,:,0] * yiqA[:,:,1]) + (yiqB[:,:,0] * yiqB[:,:,1])) / (yiqA [:,:,0] + yiqB [:,:,0])
    yiqC [:,:,2] = ((yiqA[:,:,0] * yiqA[:,:,2]) + (yiqB[:,:,0] * yiqB[:,:,2])) / (yiqA [:,:,0] + yiqB [:,:,0])
    
    rgbC = yiqToRgb(yiqC)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbC)
    ax.axis('off')

    return fig

def sumaIfLighter(imA, imB):
    
    yiqA = rgbToYiq(imA)
    yiqB = rgbToYiq(imB)
    
    yiqC = np.zeros(imA.shape)

    yiqC[:,:,0] = np.where(yiqA[:,:,0] > yiqB[:,:,0], yiqA[:,:,0], yiqB[:,:,0])
    yiqC[:,:,1] = np.where(yiqA[:,:,0] > yiqB[:,:,0], yiqA[:,:,1], yiqB[:,:,1])
    yiqC[:,:,2] = np.where(yiqA[:,:,0] > yiqB[:,:,0], yiqA[:,:,2], yiqB[:,:,2])
        
    rgbC = yiqToRgb(yiqC)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbC)
    ax.axis('off')

    return fig

def sumaIfDarker(imA, imB):
    
    yiqA = rgbToYiq(imA)
    yiqB = rgbToYiq(imB)
    
    yiqC = np.zeros(imA.shape)

    yiqC[:,:,0] = np.where(yiqA[:,:,0] < yiqB[:,:,0], yiqA[:,:,0], yiqB[:,:,0])
    yiqC[:,:,1] = np.where(yiqA[:,:,0] < yiqB[:,:,0], yiqA[:,:,1], yiqB[:,:,1])
    yiqC[:,:,2] = np.where(yiqA[:,:,0] < yiqB[:,:,0], yiqA[:,:,2], yiqB[:,:,2])
        
    rgbC = yiqToRgb(yiqC)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbC)
    ax.axis('off')

    return fig

# Crear la ventana principal
ventana = tkinter.Tk()
ventana.resizable(False, False)

# Crear un marco para la imagen A
tituloA = tkinter.Label(ventana, text="Imagen A")
frameImagenA = tkinter.Frame(ventana, width=350, height=350, bg="white")
botonCargarA = tkinter.Button(ventana, text="Cargar Imagen A", command=lambda:cargarImagen(canvasA, 'A', frameImagenA))

tituloA.grid(padx=5, pady=5, row=1, column=0)
frameImagenA.grid(padx=10, pady=10, row=2, column=0)
botonCargarA.grid(pady=5, row=3, column=0)

# Crear un marco para la imagen B
tituloB = tkinter.Label(ventana, text="Imagen B")
frameImagenB = tkinter.Frame(ventana, width=350, height=350, bg="white")
botonCargarB = tkinter.Button(ventana, text="Cargar Imagen B", command=lambda:cargarImagen(canvasB, 'B', frameImagenB))

tituloB.grid(padx=5, pady=5, row=1, column=1)
frameImagenB.grid(padx=10, pady=10, row=2, column=1)
botonCargarB.grid(pady=5, row=3, column=1)

# Crear un marco para la imagen C
tituloC = tkinter.Label(ventana, text="Imagen C")
frameImagenC = tkinter.Frame(ventana, width=350, height=350, bg="white")
botonCargarC = tkinter.Button(ventana, text="Procesar Imagen", command=lambda:procesarImagen(rutaImagenA, rutaImagenB, frameImagenC))

tituloC.grid(padx=5, pady=5, row=1, column=2)
frameImagenC.grid(padx=10, pady=10, row=2, column=2)
botonCargarC.grid(pady=5, row=3, column=2)

# Crear un marco para los desplegables
frameDesplegables = tkinter.Frame(ventana)
frameDesplegables.grid(padx=5, pady=5, row=4, columnspan=3)

# Menú desplegable para seleccionar el tipo de operación
tipoOperacion = StringVar(value="Suma")
opcionesOperacion = ["Suma", "Resta", "Producto", "División"]
menuOperacion = OptionMenu(frameDesplegables, tipoOperacion, *opcionesOperacion)
menuOperacion.grid(padx=5, pady=5, row=0, column=0)

# Menú desplegable para seleccionar el tipo de formato
tipoFormato = StringVar(value="Clampeo")
opcionesFormato = ["Clampeo", "Promedio", "YIQ Clampeo", "YIQ Promedio", "If Lighter", "If Darker"]
menuFormato = OptionMenu(frameDesplegables, tipoFormato, *opcionesFormato)
menuFormato.grid(padx=5, pady=5, row=0, column=1)

# Etiqueta para mostrar mensajes de estado
etiqueta = tkinter.Label(ventana, text="")
etiqueta.grid(padx=5, pady=5, row=0, columnspan=3)

ventana.mainloop()