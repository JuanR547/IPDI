import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
import imageio

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
        print(rutaImagen)

def mostrarImagen():
    global rutaImagen
    print(rutaImagen)
    if rutaImagen:
        imagen = imageio.imread(rutaImagen)
        
        plt.imshow(imagen)
        plt.show()
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"
        
def procesarImagen():
    global rutaImagen
    if rutaImagen:
        imagen = imageio.imread(rutaImagen)

        imagenGris = imageio.core.util.Array(imagen.mean(axis=-1))
        
        imagenRojo = imagen[:, :, 0]
        imagenVerde = imagen[:, :, 1]
        imagenAzul = imagen[:, :, 2]
        
        fig, axs = plt.subplots(1, 4, figsize=(16, 4))

        axs[0].imshow(imagenGris, cmap='gray')
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
        
        plt.show()
    else:
        etiqueta["text"] = "Primero debes cargar una imagen!"

# Tkinter
ventana = tkinter.Tk()

# Crear un botón para cargar la imagen
botonCargar = tkinter.Button(ventana, text="Cargar Imagen", command=importarImagen)
botonCargar.pack()

# Crear un botón para mostrar la imagen 
botonMostrar = tkinter.Button(ventana, text="Mostrar Imagen", command=mostrarImagen)
botonMostrar.pack()

# Crear un botón para procesar la imagen
botonProcesar = tkinter.Button(ventana, text="Procesar Imagen", command=procesarImagen)
botonProcesar.pack()

# Etiqueta
etiqueta = tkinter.Label(ventana)
etiqueta.pack()

ventana.mainloop()