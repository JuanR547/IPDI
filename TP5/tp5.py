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
import math
from skimage.morphology import skeletonize
from skimage import data
from skimage.util import invert

# Variables globales
imagen = None
imagenProcesada = None
canvasOriginal = None
canvasProcesado = None
canvasHistogramaOriginal = None
canvasHistogramaProcesado = None

# Metodos
def cargarImagen(canvas, frame):
    global imagen
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    
    if ruta:
        etiqueta["text"] = "Imagen importada correctamente!"
        
        imagenOriginal = imageio.imread(ruta)
        imagenOriginal = np.clip(imagenOriginal / 255., 0., 1.)
        
        if len(imagenOriginal.shape) == 3 and imagenOriginal.shape[2] == 3:
            imagen = rgb2Gray(imagenOriginal)            
        else:
            imagen = imagenOriginal 
        
        mostrarImagen(imagen, canvas, frame)
    else:
        etiqueta["text"] = "No se ha cargado ninguna imagen."
        
        mostrarImagen(imagen, canvas, frame)

def mostrarImagen(imagen, canvas, frame):
    global canvasOriginal, canvasHistogramaOriginal

    # Limpiar canvas anteriores si existen
    if canvas:
        canvas.get_tk_widget().destroy()
    if canvasHistogramaOriginal:
        canvasHistogramaOriginal.get_tk_widget().destroy()

    # Mostrar la imagen en el canvas
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagen, cmap="gray")
    ax.axis('off')

    canvasOriginal = FigureCanvasTkAgg(fig, master=frame)
    canvasOriginal.get_tk_widget().pack(expand=True)
    canvasOriginal.draw()

    # Mostrar el histograma en el canvas correspondiente
    canvasHistogramaOriginal = mostrarHistograma(imagen, histogramaA)

def copiarImagen(imagenProcesada):
    global canvasOriginal, frameImagenOriginal, imagen
    
    if imagenProcesada is not None:
        imagen = imagenProcesada
        
        mostrarImagen(imagen, canvasOriginal, frameImagenOriginal)
    else:
        etiqueta["text"] = "No hay ninguna imagen procesada para copiar!"

        
def guardarImagen(imagenProcesada):
    if imagenProcesada is not None:
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp"), ("GIF", "*.gif")],
            title="Guardar imagen procesada"
        )
        
        if ruta_guardado:
            imagen_guardar = np.clip(imagenProcesada * 255, 0, 255).astype(np.uint8)
            
            imageio.imwrite(ruta_guardado, imagen_guardar)
            etiqueta["text"] = f"Imagen procesada guardada en {ruta_guardado}!"
        else:
            etiqueta["text"] = "No se ha guardado la imagen procesada."
    else:
        etiqueta["text"] = "No hay ninguna imagen procesada para guardar."

def procesarImagen(frame):
    global canvasProcesado, imagenProcesada, imagen

    if imagen is not None:  # Asegurarse de que la imagen ha sido cargada
        # Realizar la operación según selección
        if tipoOperacion.get() == "Binarizar":
            umbral = slider.get()
            fig = binarizar(imagen, umbral)
        elif tipoOperacion.get() == "Erosionar":
            fig = erosion(imagen)
        elif tipoOperacion.get() == "Dilatar":
            fig = dilatacion(imagen)
        elif tipoOperacion.get() == "Apertura":
            fig = apertura(imagen)
        elif tipoOperacion.get() == "Cierre":
            fig = cierre(imagen)
        elif tipoOperacion.get() == "Borde":
            fig = bordeMorfologico(imagen)
        elif tipoOperacion.get() == "Mediana":
            fig = mediana(imagen)
        elif tipoOperacion.get() == "Esqueletonizar":
            fig = skeleton(imagen)
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
                
def rgb2Gray(imagen):
    return np.dot(imagen[..., :3], [0.2989, 0.5870, 0.1140])

def mostrarHistograma(imagen, frame):
    hist, bins = np.histogram(imagen.flatten(), bins=10, range=(0, 1))
    
    hist_normalized = hist / np.sum(hist)

    fig, ax = plt.subplots(figsize=(4, 4))
    hist, bins = np.histogram(imagen.flatten(), bins=10, range=(0, 1))
    hist_normalized = hist / np.sum(hist)
    
    ax.bar(bins[:-1], hist_normalized, width=(bins[1] - bins[0]), edgecolor='black')
    ax.set_title('Histograma')
    ax.set_xlabel('Luminancia')
    ax.set_ylabel('Frecuencia (%)')
    
    canvasHistograma = FigureCanvasTkAgg(fig, master=frame)
    canvasHistograma.get_tk_widget().pack(expand=True)
    canvasHistograma.draw()
    
    return canvasHistograma
    
def binarizar(imagen, umbral):
    global imagenProcesada
    
    imBin = np.where(imagen >= umbral, 0, 1)
        
    imagenProcesada = imBin
        
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imBin, cmap="gray")
    ax.axis('off')
    
    return fig

def detectarFondo(imagen):
    
  cantidad_blancos = np.sum(imagen == 1)
  cantidad_negros = np.sum(imagen == 0)

  if cantidad_blancos > cantidad_negros:
    return 1
  else:
    return 0

def erosionar(imagen):
    fondo = detectarFondo(imagen)
    
    # Invertir la imagen si el fondo es blanco (para que la figura siempre sea blanca)
    if fondo == 1:
        imagen_invertida = 1 - imagen
    else:
        imagen_invertida = imagen

    kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    filas, columnas = imagen_invertida.shape
    filas_est, columnas_est = kernel.shape
    imagenErosionada = np.zeros((filas, columnas))

    for i in range(filas_est // 2, filas - filas_est // 2):
        for j in range(columnas_est // 2, columnas - columnas_est // 2):
            vecindario = imagen_invertida[i - filas_est // 2: i + filas_est // 2 + 1,
                                          j - columnas_est // 2: j + columnas_est // 2 + 1]
            if np.array_equal(vecindario * kernel, kernel):
                imagenErosionada[i, j] = 1

    # Restaurar la imagen si fue invertida
    if fondo == 1:
        imagenErosionada = 1 - imagenErosionada
        
    return imagenErosionada

def dilatar(imagen):    
    fondo = detectarFondo(imagen)
    
    # Invertir la imagen si el fondo es blanco (para que la figura siempre sea blanca)
    if fondo == 1:
        imagen_invertida = 1 - imagen
    else:
        imagen_invertida = imagen

    kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    filas, columnas = imagen_invertida.shape
    filas_est, columnas_est = kernel.shape
    imagenDilatada = np.zeros((filas, columnas))

    for i in range(filas_est // 2, filas - filas_est // 2):
        for j in range(columnas_est // 2, columnas - columnas_est // 2):
            vecindario = imagen_invertida[i - filas_est // 2: i + filas_est // 2 + 1,
                                          j - columnas_est // 2: j + columnas_est // 2 + 1]
            if np.sum(vecindario * kernel) > 0:
                imagenDilatada[i, j] = 1

    # Restaurar la imagen si fue invertida
    if fondo == 1:
        imagenDilatada = 1 - imagenDilatada
        
    return imagenDilatada

def erosion(imagen):
    global imagenProcesada
        
    imagenProcesada = erosionar(imagen)

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagenProcesada, cmap="gray")
    ax.axis('off')

    return fig

def dilatacion(imagen):
    global imagenProcesada
        
    imagenProcesada = dilatar(imagen)  

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagenProcesada, cmap="gray")
    ax.axis('off')

    return fig

def apertura(imagen):
    global imagenProcesada

    imagenErosionada = erosionar(imagen)
    imagenApertura = dilatar(imagenErosionada)

    imagenProcesada = imagenApertura
            
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagenApertura, cmap="gray")
    ax.axis('off')
    
    return fig

def cierre(imagen):
    global imagenProcesada

    imagenDilatada = dilatar(imagen)
    imagenCierre = erosionar(imagenDilatada)

    imagenProcesada = imagenCierre
            
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagenCierre, cmap="gray")
    ax.axis('off')
    
    return fig

def bordeMorfologico(imagen):
    global imagenProcesada
    
    imagenErosionada = erosionar(imagen)
    imagenBorde = imagen - imagenErosionada
    
    imagenProcesada = imagenBorde
            
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagenBorde, cmap="gray")
    ax.axis('off')
    
    return fig

def obtener_mediana(lista):
    lista_ordenada = sorted(lista)
    longitud = len(lista_ordenada)
    if longitud % 2 == 1:
        return lista_ordenada[longitud // 2]
    else:
        mitad = longitud // 2
        return (lista_ordenada[mitad - 1] + lista_ordenada[mitad]) // 2

def mediana(imagen):
    
    altura = len(imagen)
    ancho = len(imagen[0])
    tamaño_kernel=3
    
    padding = tamaño_kernel // 2
    
    imagenFiltrada = [[0] * ancho for _ in range(altura)]
    
    for i in range(padding, altura - padding):
        for j in range(padding, ancho - padding):
            vecindad = []
            for ki in range(-padding, padding + 1):
                for kj in range(-padding, padding + 1):
                    vecindad.append(imagen[i + ki][j + kj])
            
            imagenFiltrada[i][j] = obtener_mediana(vecindad)
    
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(imagenFiltrada, cmap="gray")
    ax.axis('off')
    
    return fig

def skeleton(imagen):
    
    skeleton = skeletonize(imagen)
    
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(skeleton, cmap="gray")
    ax.axis('off')
    
    return fig

        
# Crear la ventana principal
ventana = tkinter.Tk()
ventana.resizable(False, False)

# Etiqueta para mostrar mensajes de estado
etiqueta = tkinter.Label(ventana, text="")
etiqueta.grid(padx=5, pady=5, row=0, columnspan=4)

# Crear un marco para la imagen A
tituloA = tkinter.Label(ventana, text="Imagen Original")
frameImagenOriginal = tkinter.Frame(ventana, width=250, height=250, bg="white")
histogramaA = tkinter.Frame(ventana, width=200, height=200, bg="white")
botonCargarA = tkinter.Button(ventana, text="Cargar Imagen", command=lambda:cargarImagen(canvasOriginal, frameImagenOriginal))

tituloA.grid(padx=5, pady=5, row=1, column=0)
frameImagenOriginal.grid(padx=10, pady=10, row=2, column=0)
histogramaA.grid(padx=10, pady=10, row=2, column=1)
botonCargarA.grid(pady=5, row=3, column=0)

# Crear un marco para los Procesar y Copiar
tituloB = tkinter.Label(ventana, text="Controles")
controlesVariables = tkinter.Frame(ventana, width=250, height=250, bg="white")

botonProcesar = tkinter.Button(controlesVariables, text="Procesar Imagen -->", command=lambda:procesarImagen(frameProcesada))
botonCopiar = tkinter.Button(controlesVariables, text="<-- Copiar Imagen", command=lambda:copiarImagen(imagenProcesada))
slider = Scale(controlesVariables, from_=0, to=1, orient=HORIZONTAL, label="Umbral", resolution=0.1)
slider.set(0)

tituloB.grid(padx=5, pady=5, row=1, column=2)
controlesVariables.grid(padx=10, pady=10, row=2, column=2)

botonProcesar.pack(pady=5)
botonCopiar.pack(pady=5)
slider.pack(side="top", padx=20, pady=10)

# Crear un marco para la imagen Procesada
tituloProcesado = tkinter.Label(ventana, text="Imagen Procesada")
frameProcesada = tkinter.Frame(ventana, width=250, height=250, bg="white")
botonGuardar = tkinter.Button(ventana, text="Guardar Imagen", command=lambda:guardarImagen(imagenProcesada))

tituloProcesado.grid(padx=5, pady=5, row=1, column=3)
frameProcesada.grid(padx=10, pady=10, row=2, column=3)
botonGuardar.grid(pady=5, row=3, column=3)

# Crear un marco para los desplegables
frameDesplegables = tkinter.Frame(ventana)
frameDesplegables.grid(padx=5, pady=5, row=4, columnspan=4)

# Menú desplegable para seleccionar el tipo de operación
tipoOperacion = StringVar(value="Binarizar")
opcionesOperacion = ["Binarizar",
                     "Erosionar",
                     "Dilatar",
                     "Apertura",
                     "Cierre",
                     "Borde",
                     "Mediana",
                     "Esqueletonizar"]
menuOperacion = OptionMenu(frameDesplegables, tipoOperacion, *opcionesOperacion)
menuOperacion.grid(padx=5, pady=5, row=0, column=0)

ventana.mainloop()