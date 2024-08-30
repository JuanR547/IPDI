#python -m pip install -U pip
#python -m pip install -U matplotlib
#pip install imagio

import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import imageio.v2 as imageio

# Metodos
rutaImagen = None

def importarImagen():
    global rutaImagen
    rutaImagen = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
    )
    if rutaImagen:
        etiqueta["text"] = "Imagen importada correctamente!"

def mostrarImagen():
    global rutaImagen
    canvas = None
    if rutaImagen:
        imagen = imageio.imread(rutaImagen)
        
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.imshow(imagen)
        ax.set_title("Imagen Original")
        ax.axis('off')

        if canvas:
            canvas.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=frameImagenOriginal)
        canvas.get_tk_widget().pack(expand=True)
        canvas.draw()
         
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"
        
def procesarImagen():
    global rutaImagen
    canvasProcesado = None
    if rutaImagen:
        
        imagen = imageio.imread(rutaImagen)
        
        imagenRojo = imagen[:, :, 0]
        imagenVerde = imagen[:, :, 1]
        imagenAzul = imagen[:, :, 2]
        
        fig, axs = plt.subplots(1, 4, figsize = (12, 2))

        axs[0].imshow(imagen[:, :, 0], cmap='gray')
        axs[0].set_title("Blanco y Negro")
        axs[0].axis('off')
        
        axs[1].imshow(imagenRojo, cmap='Reds')
        axs[1].set_title("Canal Rojo")
        axs[1].axis('off')   
        
        axs[2].imshow(imagenVerde, cmap='Greens')
        axs[2].set_title("Canal Verde")
        axs[2].axis('off')
        
        axs[3].imshow(imagenAzul, cmap='Blues')
        axs[3].set_title("Canal Azul")
        axs[3].axis('off')
        
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

# Crear un botón para mostrar la imagen
botonMostrar = tkinter.Button(frameControles, text="Mostrar Imagen", command=mostrarImagen)
botonMostrar.grid(row=0, column=1, padx=10)

# Crear un botón para procesar la imagen
botonProcesar = tkinter.Button(frameControles, text="Procesar Imagen", command=procesarImagen)
botonProcesar.grid(row=0, column=2, padx=10)

# Etiqueta para mostrar mensajes de estado
etiqueta = tkinter.Label(frameControles, text="")
etiqueta.grid(row=1, columnspan=3, pady=3)

ventana.mainloop()