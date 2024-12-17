from inference import get_model
import supervision as sv
import cv2
import tkinter as tk
from tkinter import ttk

# Inicializar los modelos
ROBOFLOW_API_KEY = 'EnpsmyEnc9LOyrioXIMH'
MODEL_1_ID = 'colores-remeras/2'  # Primer modelo
MODEL_2_ID = 'colores-pantalones-cortos/1'  # Segundo modelo
model1 = get_model(MODEL_1_ID, ROBOFLOW_API_KEY)
model2 = get_model(MODEL_2_ID, ROBOFLOW_API_KEY)

# Crear los anotadores con la nueva clase BoxAnnotator y LabelAnnotator
color1 = sv.Color(255, 0, 0)  # Azul para el modelo 1
color2 = sv.Color(0, 255, 0)  # Verde para el modelo 2

box_annotator1 = sv.BoxAnnotator(thickness=2, color=color1)
label_annotator1 = sv.LabelAnnotator(color=color1)

box_annotator2 = sv.BoxAnnotator(thickness=2, color=color2)
label_annotator2 = sv.LabelAnnotator(color=color2)

# Función para mostrar la ventana de selección de color
def select_color():
    def on_color_selected():
        selected_color = color_combobox.get()
        # Guardar el color seleccionado
        color_mapping = {
            "Negra": "remera-negra",
            "Roja": "remera-roja",
            "Azul": "remera-azul",
            "Blanca": "remera-blanca",
            "Amarilla": "remera-amarilla",
            "Celeste": "remera-celeste",
            "Gris": "remera-gris",
            "Marron": "remera-marron",
            "Morada": "remera-morada",
            "Naranja": "remera-naranja",
            "Verde": "remera-verde",
            "Rosada": "remera-rosada"
        }
        selected_color_label = color_mapping.get(selected_color, "remera-negra")  # Valor por defecto
        root.destroy()  # Cierra la ventana de selección
        run_detection(selected_color_label)

    # Crear la ventana
    root = tk.Tk()
    root.title("Selecciona el color de la remera")

    # Crear un menú desplegable para seleccionar el color
    color_combobox = ttk.Combobox(root, values=["Negra", "Roja", "Azul", "Blanca", "Amarilla", "Celeste", 
                                                 "Gris", "Marron", "Morada", "Naranja", "Verde", "Rosada"])
    color_combobox.set("Negra")  # Establecer el color por defecto
    color_combobox.pack(padx=20, pady=20)

    # Botón para confirmar la selección
    select_button = tk.Button(root, text="Seleccionar", command=on_color_selected)
    select_button.pack(pady=10)

    # Mostrar la ventana
    root.mainloop()

# Función principal para la detección con el color seleccionado
def run_detection(selected_color_label):
    # Captura de video en tiempo real desde la cámara
    cap = cv2.VideoCapture(0)

    # Redimensionar la ventana a un tamaño más pequeño
    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 480

    cv2.namedWindow("Detecciones en tiempo real", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detecciones en tiempo real", WINDOW_WIDTH, WINDOW_HEIGHT)

    while True:
        # Leer fotograma de la cámara
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma")
            break

        # Realizar la inferencia con el primer modelo (remeras)
        results1 = model1.infer(frame)[0]
        detections1 = sv.Detections.from_inference(results1)

        # Realizar la inferencia con el segundo modelo (pantalones cortos)
        results2 = model2.infer(frame)[0]
        detections2 = sv.Detections.from_inference(results2)

        # Anotar el fotograma con las detecciones del primer modelo (remeras)
        annotated_frame = box_annotator1.annotate(scene=frame, detections=detections1)
        annotated_frame = label_annotator1.annotate(scene=annotated_frame, detections=detections1)

        # Anotar el fotograma con las detecciones del segundo modelo (pantalones cortos)
        annotated_frame = box_annotator2.annotate(scene=annotated_frame, detections=detections2)
        annotated_frame = label_annotator2.annotate(scene=annotated_frame, detections=detections2)

        # Comprobar si hay detecciones simultáneas de remera del color seleccionado y pantalones cortos
        for detection in detections1:
            # Extraer solo la etiqueta ('class_name') del diccionario
            label = detection[5]['class_name']
            
            # Normalizar la etiqueta de la detección y la etiqueta seleccionada
            label_normalized = label
            selected_color_label_normalized = selected_color_label

            # Verificar si la etiqueta de la remera coincide con la seleccionada
            if label_normalized == selected_color_label_normalized:
                if len(detections2) > 0:
                    alert_text = f"¡ALERTA: {selected_color_label} y pantalón corto detectados!"
                    print(alert_text)  # Mostrar en consola
                    # Superponer texto en el cuadro de video
                    cv2.putText(annotated_frame, alert_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Mostrar el fotograma anotado en la ventana redimensionada
        cv2.imshow("Detecciones en tiempo real", annotated_frame)

        # Salir del bucle al presionar la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar todas las ventanas
    cap.release()
    cv2.destroyAllWindows()

# Llamar a la función para seleccionar el color antes de comenzar la detección
select_color()
