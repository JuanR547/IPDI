#python -m pip install -U pip
#python -m pip install -U matplotlib
#pip install imagio

import tkinter
from tkinter import HORIZONTAL, VERTICAL, Scale, filedialog, StringVar, OptionMenu
from tkinter import simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import imageio.v2 as imageio
import numpy as np

# Variables globales
rutaImagen = None
canvasOriginal = None
canvasProcesado = None
canvasHistogramaOriginal = None
canvasHistogramaProcesado = None

# Metodos
def cargarImagen(canvas, frame):
    global rutaImagen
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    
    if ruta:
        etiqueta["text"] = "Imagen importada correctamente!"
        rutaImagen = ruta
        mostrarImagen(ruta, canvas, frame)

def mostrarImagen(ruta, canvas, frame):
    global canvasOriginal, canvasHistogramaOriginal
    if ruta:
        imagen = imageio.imread(ruta)
        imagen = np.clip(imagen / 255., 0., 1.)

        if canvas:
            canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 2))
        ax.imshow(imagen)
        ax.axis('off')

        canvasOriginal = FigureCanvasTkAgg(fig, master=frame)
        canvasOriginal.get_tk_widget().pack(expand=True)
        canvasOriginal.draw()

        # Limpiar el canvas previo
        if canvasHistogramaOriginal:
            canvasHistogramaOriginal.get_tk_widget().destroy()
            canvasHistogramaOriginal = None

        # Mostrar histograma de la imagen original
        canvasHistogramaOriginal = mostrarHistograma(imagen, canvasHistogramaOriginal, histogramaA)
         
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"

def procesarImagen(ruta, frame):
    global canvasProcesado
    if ruta:
        imagen = imageio.imread(ruta)
        imagen = np.clip(imagen / 255., 0., 1.)

        # Realizar la operación según selección
        if tipoOperacion.get() == "Raiz Cuadrada":
            fig = raizCuadrada(imagen)
        elif tipoOperacion.get() == "Cuadratica":
            fig = cuadratica(imagen)    
        elif tipoOperacion.get() == "Lineal a trozos":
            fig = linealTrozos(imagen)    
        else:
            etiqueta["text"] = "No es posible realizar esa selección!"
            return

        # Limpiar el canvas previo
        if canvasProcesado:
            canvasProcesado.get_tk_widget().destroy()
            
        # Mostrar el resultado en el canvas
        canvasProcesado = FigureCanvasTkAgg(fig, master=frame)
        canvasProcesado.get_tk_widget().pack(expand=True)
        canvasProcesado.draw()

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

def mostrarHistograma(imagen, canvas, frame):
    yiq = rgbToYiq(imagen)
    hist, bins = np.histogram(yiq[:,:,0].flatten(), bins=10, range=(0, 1))
    hist_porcentaje = (hist / hist.sum()) * 100

    if canvas:
        canvas.get_tk_widget().destroy()

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.bar(bins[:-1], hist_porcentaje, width=(bins[1] - bins[0]), edgecolor='black')
    ax.set_title('Histograma')
    ax.set_xlabel('Luminancia')
    ax.set_ylabel('Frecuencia (%)')
    
    ax.set_ylim(0, 100)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(expand=True)
    canvas.draw()

    return canvas

def linealTrozos(imagen):
    global canvasHistogramaProcesado
    
    yiq = rgbToYiq(imagen)
    yiq2 = np.zeros(imagen.shape)

    # Obtener valores de los sliders
    yMin = sliderMin.get()
    yMax = sliderMax.get()

    yiq2[:,:,0] = np.where(yiq[:,:,0] < yMin, 0, np.where(yiq[:,:,0] > yMax, 1, (yiq[:,:,0] - yMin) / (yMax - yMin)))
    yiq2[:,:,1] = yiq[:,:,1]
    yiq2[:,:,2] = yiq[:,:,2]

    rgbLinealTrozos = np.zeros(yiq.shape)
    rgbLinealTrozos = yiqToRgb(yiq2)
    
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbLinealTrozos)
    ax.axis('off')
    
    # Limpiar el canvas previo
    if canvasHistogramaProcesado:
        canvasHistogramaProcesado.get_tk_widget().destroy()
        canvasHistogramaProcesado = None

    
    # Mostrar histograma de la imagen procesada
    canvasHistogramaProcesado = mostrarHistograma(rgbLinealTrozos, canvasHistogramaProcesado, histogramaProcesado)

    return fig

def raizCuadrada(imagen):
    global canvasHistogramaProcesado
    
    yiq = np.zeros(imagen.shape)
    yiq = rgbToYiq(imagen)
    
    yRaiz = np.sqrt(yiq[:,:,0])
    
    rgbRaiz = np.zeros(yiq.shape)
    rgbRaiz[:,:,0] = np.clip(1 * yRaiz +  0.9663 * yiq[:,:,1] + 0.6210 * yiq[:,:,2],0,1)
    rgbRaiz[:,:,1] = np.clip(1 * yRaiz + -0.2721 * yiq[:,:,1] + -0.6474 * yiq[:,:,2],0,1)
    rgbRaiz[:,:,2] = np.clip(1 * yRaiz + -1.1070 * yiq[:,:,1] + 1.7046 * yiq[:,:,2],0,1)
    
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbRaiz)
    ax.axis('off')
    
    # Limpiar el canvas previo
    if canvasHistogramaProcesado:
        canvasHistogramaProcesado.get_tk_widget().destroy()
        canvasHistogramaProcesado = None
    
    # Mostrar histograma de la imagen procesada
    canvasHistogramaProcesado = mostrarHistograma(rgbRaiz, canvasHistogramaProcesado, histogramaProcesado)
    
    return fig

def cuadratica(imagen):
    global canvasHistogramaProcesado
    
    yiq = np.zeros(imagen.shape)
    yiq = rgbToYiq(imagen)
    
    yCuadratica = np.clip((yiq[:,:,0] * yiq[:,:,0]), 0, 1)

    rgbCuadratico = np.zeros(yiq.shape)

    rgbCuadratico[:,:,0] = np.clip(1 * yCuadratica +  0.9663 * yiq[:,:,1] + 0.6210 * yiq[:,:,2],0,1)
    rgbCuadratico[:,:,1] = np.clip(1 * yCuadratica + -0.2721 * yiq[:,:,1] + -0.6474 * yiq[:,:,2],0,1)
    rgbCuadratico[:,:,2] = np.clip(1 * yCuadratica + -1.1070 * yiq[:,:,1] + 1.7046 * yiq[:,:,2],0,1)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.imshow(rgbCuadratico)
    ax.axis('off')
    
    # Limpiar el canvas previo
    if canvasHistogramaProcesado:
        canvasHistogramaProcesado.get_tk_widget().destroy()
        canvasHistogramaProcesado = None
    
    # Mostrar histograma de la imagen procesada
    canvasHistogramaProcesado = mostrarHistograma(rgbCuadratico, canvasHistogramaProcesado, histogramaProcesado)
    
    return fig

# Crear la ventana principal
ventana = tkinter.Tk()
ventana.resizable(False, False)

# Crear un marco para la imagen A
tituloA = tkinter.Label(ventana, text="Imagen Original")
frameImagenOriginal = tkinter.Frame(ventana, width=250, height=250, bg="white")
histogramaA = tkinter.Frame(ventana, width=200, height=200, bg="white")
botonCargarA = tkinter.Button(ventana, text="Cargar Imagen", command=lambda:cargarImagen(canvasOriginal, frameImagenOriginal))

tituloA.grid(padx=5, pady=5, row=1, column=0)
frameImagenOriginal.grid(padx=10, pady=10, row=2, column=0)
histogramaA.grid(padx=10, pady=10, row=3, column=0)
botonCargarA.grid(pady=5, row=4, column=0)

# Crear un marco para los controles
tituloB = tkinter.Label(ventana, text="Controles")
controlesVariables = tkinter.Frame(ventana, width=250, height=250, bg="white")

tituloB.grid(padx=5, pady=5, row=1, column=1)
controlesVariables.grid(padx=10, pady=10, row=2, column=1)

# Crear un marco para la imagen Procesada
tituloProcesado = tkinter.Label(ventana, text="Imagen Procesada")
frameProcesada = tkinter.Frame(ventana, width=250, height=250, bg="white")
histogramaProcesado = tkinter.Frame(ventana, width=200, height=200, bg="white")
botonProcesar = tkinter.Button(ventana, text="Procesar Imagen", command=lambda:procesarImagen(rutaImagen, frameProcesada))

tituloProcesado.grid(padx=5, pady=5, row=1, column=2)
frameProcesada.grid(padx=10, pady=10, row=2, column=2)
histogramaProcesado.grid(padx=10, pady=10, row=3, column=2)
botonProcesar.grid(pady=5, row=4, column=2)

# Crear un marco para los desplegables
frameDesplegables = tkinter.Frame(ventana)
frameDesplegables.grid(padx=5, pady=5, row=4, columnspan=3)

# Menú desplegable para seleccionar el tipo de operación
tipoOperacion = StringVar(value="Raiz Cuadrada")
opcionesOperacion = ["Raiz Cuadrada", "Cuadratica", "Lineal a trozos"]
menuOperacion = OptionMenu(frameDesplegables, tipoOperacion, *opcionesOperacion)
menuOperacion.grid(padx=5, pady=5, row=0, column=0)

# Etiqueta para mostrar mensajes de estado
etiqueta = tkinter.Label(ventana, text="")
etiqueta.grid(padx=5, pady=5, row=0, columnspan=3)

# Slider para ajustar yMin
sliderMin = Scale(controlesVariables, from_=0, to=1, orient=HORIZONTAL, label="Corte inferior", resolution=0.1)
sliderMin.set(0)
sliderMin.pack(side="top", padx=20, pady=10)

# Slider para ajustar yMax
sliderMax = Scale(controlesVariables, from_=0, to=1, orient=HORIZONTAL, label="Corte superior", resolution=0.1)
sliderMax.set(1)
sliderMax.pack(side="bottom", padx=20, pady=10)

ventana.mainloop()