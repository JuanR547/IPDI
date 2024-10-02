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

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.imshow(imagen)
        ax.axis('off')

        canvasOriginal = FigureCanvasTkAgg(fig, master=frame)
        canvasOriginal.get_tk_widget().pack(expand=True)
        canvasOriginal.draw()

        # Limpiar el canvas previo
        if canvasHistogramaOriginal:
            canvasHistogramaOriginal.get_tk_widget().destroy()
            canvasHistogramaOriginal = None
                     
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"

def procesarImagen(ruta, frame):
    global canvasProcesado
    if ruta:
        imagen = imageio.imread(ruta)
        imagen = np.clip(imagen / 255., 0., 1.)
        imagenGris = np.zeros(imagen.shape)
        imagenGris = rgb2Gray(imagen)

        # Realizar la operación según selección
        if tipoOperacion.get() == "Plano":
            kernel = generarKernelId(3)
            fig = convolucion(imagenGris, kernel)
        elif tipoOperacion.get() == "Barlett 3x3":
            kernel = generarKernelBarlett(3)
            fig = convolucion(imagenGris, kernel)   
        elif tipoOperacion.get() == "Barlett 5x5":
            kernel = generarKernelBarlett(5)
            fig = convolucion(imagenGris, kernel)  
        elif tipoOperacion.get() == "Barlett 7x7":
            kernel = generarKernelBarlett(7)
            fig = convolucion(imagenGris, kernel)     
        elif tipoOperacion.get() == "Gaussiano 5x5":
            kernel = generarKernelGaussiano(5)
            fig = convolucion(imagenGris, kernel)    
        elif tipoOperacion.get() == "Gaussiano 7x7":
            kernel = generarKernelGaussiano(7)
            fig = convolucion(imagenGris, kernel)
        elif tipoOperacion.get() == "Laplaciano V4":
            kernel = generarKernelLaplaceV4()
            fig = convolucionLaplaciana(imagenGris, kernel)
        elif tipoOperacion.get() == "Laplaciano V8":
            kernel = generarKernelLaplaceV8()
            fig = convolucionLaplaciana(imagenGris, kernel)
        elif tipoOperacion.get() == "Sahrpening V4":
            kernel = generarKernelLaplaceV4()
            fig = convolucionSharpening(imagenGris, kernel)
        elif tipoOperacion.get() == "Sahrpening V8":
            kernel = generarKernelLaplaceV8()
            fig = convolucionSharpening(imagenGris, kernel)
        elif tipoOperacion.get() == "Sobel Norte":
            kernel = generarKernelSobel("N")
            fig = convolucionLaplaciana(imagenGris, kernel)   
        elif tipoOperacion.get() == "Sobel Sur":
            kernel = generarKernelSobel("S")
            fig = convolucionLaplaciana(imagenGris, kernel)     
        elif tipoOperacion.get() == "Sobel Este":
            kernel = generarKernelSobel("E")
            fig = convolucionLaplaciana(imagenGris, kernel)     
        elif tipoOperacion.get() == "Sobel Oeste":
            kernel = generarKernelSobel("O")
            fig = convolucionLaplaciana(imagenGris, kernel)  
        elif tipoOperacion.get() == "Sobel Noreste":
            kernel = generarKernelSobel("NE")
            fig = convolucionLaplaciana(imagenGris, kernel)   
        elif tipoOperacion.get() == "Sobel Noroeste":
            kernel = generarKernelSobel("NO")
            fig = convolucionLaplaciana(imagenGris, kernel)     
        elif tipoOperacion.get() == "Sobel Sureste":
            kernel = generarKernelSobel("SE")
            fig = convolucionLaplaciana(imagenGris, kernel)     
        elif tipoOperacion.get() == "Sobel Suroeste":
            kernel = generarKernelSobel("SO")
            fig = convolucionLaplaciana(imagenGris, kernel)       
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
    if len(imagen.shape) == 3 and imagen.shape[2] == 3:
        return np.dot(imagen[..., :3], [0.2989, 0.5870, 0.1140])
    else:
        raise ValueError("La imagen no tiene los 3 canales necesarios para RGB.")

def generarKernelId(n):
    k = np.ones((n,n))
    k = k/sum(k)
    return k

def generarKernelBarlett(n):
    kernel = np.zeros((n, n))
    centro = n // 2

    for i in range(n):
        for j in range(n):
            kernel[i, j] = (centro - abs(i - centro)) + 1
            kernel[i, j] *= (centro - abs(j - centro)) + 1

    kernel = kernel / np.sum(kernel)

    return kernel

def generarKernelGaussiano(n):
    if n % 2 == 0:
        raise ValueError("El tamaño del kernel debe ser un número impar.")
    
    pascal1d = np.array([math.comb(n - 1, i) for i in range(n)])
    kernel2d = np.outer(pascal1d, pascal1d)
    kernel2d = kernel2d / np.sum(kernel2d)
    
    return kernel2d

def generarKernelLaplaceV4():
    laplaceV4 = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
    return laplaceV4

def generarKernelLaplaceV8():
    laplaceV8 = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    return laplaceV8

def generarKernelSobel(sentido):
    if sentido == "N":
        kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    elif sentido == "S":
        kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    elif sentido == "E":
        kernel = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
    elif sentido == "O":
        kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    elif sentido == "NO":
        kernel = np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]])
    elif sentido == "NE":
        kernel = np.array([[0, -1, -2], [1, 0, -1], [2, 1, 0]])
    elif sentido == "SO":
        kernel = np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]])
    elif sentido == "SE":
        kernel = np.array([[2, 1, 0], [1, 0, -1], [0, -1, -2]])

    return kernel

def convolucion(imagen, kernel):
    global canvasHistogramaProcesado
    
    conv = np.zeros((imagen.shape[0] - kernel.shape[0] + 1, imagen.shape[1] - kernel.shape[1] + 1))

    for y in range(conv.shape[0]):
        for x in range(conv.shape[1]):
            conv[y, x] = np.sum(imagen[y:y+kernel.shape[0], x:x+kernel.shape[1]] * kernel)
            
    fig, ax = plt.subplots(figsize=(4, 4))  # Aumenté el tamaño para mejor visualización
    ax.imshow(conv, cmap="gray")  # Especificar el mapa de colores a gris
    ax.axis('off')
    
    # Limpiar el canvas previo
    if canvasHistogramaProcesado:
        canvasHistogramaProcesado.get_tk_widget().destroy()
        canvasHistogramaProcesado = None
        
    return fig

def convolucionLaplaciana(imagen, kernel):
    global canvasHistogramaProcesado
    
    conv = np.zeros((imagen.shape[0] - kernel.shape[0] + 1, imagen.shape[1] - kernel.shape[1] + 1))

    for y in range(conv.shape[0]):
        for x in range(conv.shape[1]):
            valor = np.sum(imagen[y:y + kernel.shape[0], x:x + kernel.shape[1]] * kernel)
            conv[y, x] = np.clip(valor, 0, 1)
            
    fig, ax = plt.subplots(figsize=(4, 4))  # Aumenté el tamaño para mejor visualización
    ax.imshow(conv, cmap="gray")  # Especificar el mapa de colores a gris
    ax.axis('off')
    
    # Limpiar el canvas previo
    if canvasHistogramaProcesado:
        canvasHistogramaProcesado.get_tk_widget().destroy()
        canvasHistogramaProcesado = None
        
    return fig
            
def convolucionSharpening(imagen, kernelLaplaciano):
  global canvasHistogramaProcesado

  x = sliderMin.get()
  kernelIdentidad = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
  kernelCombinado = x * kernelLaplaciano + (1 - x) * kernelIdentidad

  conv = np.zeros((imagen.shape[0] - kernelCombinado.shape[0] + 1, imagen.shape[1] - kernelCombinado.shape[1] + 1))

  for y in range(conv.shape[0]):
      for x in range(conv.shape[1]):
          valor = np.sum(imagen[y:y + kernelCombinado.shape[0], x:x + kernelCombinado.shape[1]] * kernelCombinado)
          conv[y, x] = np.clip(valor, 0, 1)

  fig, ax = plt.subplots(figsize=(4, 4))  # Aumenté el tamaño para mejor visualización
  ax.imshow(conv, cmap="gray")  # Especificar el mapa de colores a gris
  ax.axis('off')
    
  # Limpiar el canvas previo
  if canvasHistogramaProcesado:
    canvasHistogramaProcesado.get_tk_widget().destroy()
    canvasHistogramaProcesado = None
        
  return fig


# Crear la ventana principal
ventana = tkinter.Tk()
ventana.resizable(False, False)

# Crear un marco para la imagen A
tituloA = tkinter.Label(ventana, text="Imagen Original")
frameImagenOriginal = tkinter.Frame(ventana, width=250, height=250, bg="white")
botonCargarA = tkinter.Button(ventana, text="Cargar Imagen", command=lambda:cargarImagen(canvasOriginal, frameImagenOriginal))

tituloA.grid(padx=5, pady=5, row=1, column=0)
frameImagenOriginal.grid(padx=10, pady=10, row=2, column=0)
botonCargarA.grid(pady=5, row=4, column=0)

# Crear un marco para los controles
tituloB = tkinter.Label(ventana, text="Controles")
controlesVariables = tkinter.Frame(ventana, width=250, height=250, bg="white")

tituloB.grid(padx=5, pady=5, row=1, column=1)
controlesVariables.grid(padx=10, pady=10, row=2, column=1)

# Crear un marco para la imagen Procesada
tituloProcesado = tkinter.Label(ventana, text="Imagen Procesada")
frameProcesada = tkinter.Frame(ventana, width=250, height=250, bg="white")
botonProcesar = tkinter.Button(ventana, text="Procesar Imagen", command=lambda:procesarImagen(rutaImagen, frameProcesada))

tituloProcesado.grid(padx=5, pady=5, row=1, column=2)
frameProcesada.grid(padx=10, pady=10, row=2, column=2)
botonProcesar.grid(pady=5, row=4, column=2)

# Crear un marco para los desplegables
frameDesplegables = tkinter.Frame(ventana)
frameDesplegables.grid(padx=5, pady=5, row=4, columnspan=3)

# Menú desplegable para seleccionar el tipo de operación
tipoOperacion = StringVar(value="Plano")
opcionesOperacion = ["Plano",
                     "Barlett 3x3", "Barlett 5x5", "Barlett 7x7",
                     "Gaussiano 5x5", "Gaussiano 7x7",
                     "Laplaciano V4", "Laplaciano V8",
                     "Sahrpening V4", "Sahrpening V8",
                     "Sobel Norte", "Sobel Sur", "Sobel Este", "Sobel Oeste",
                     "Sobel Noreste", "Sobel Noroeste", "Sobel Sureste", "Sobel Suroeste"]
menuOperacion = OptionMenu(frameDesplegables, tipoOperacion, *opcionesOperacion)
menuOperacion.grid(padx=5, pady=5, row=0, column=0)

# Etiqueta para mostrar mensajes de estado
etiqueta = tkinter.Label(ventana, text="")
etiqueta.grid(padx=5, pady=5, row=0, columnspan=3)

# Slider para ajustar yMin
sliderMin = Scale(controlesVariables, from_=0, to=1, orient=HORIZONTAL, label="Porcentaje Sharpening", resolution=0.1)
sliderMin.set(0)
sliderMin.pack(side="top", padx=20, pady=10)

ventana.mainloop()