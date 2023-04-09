import re
import cv2
from google.cloud import vision
from google.oauth2 import service_account
from google.cloud.vision_v1 import types

#CLOUVISION
key_path = "MIRUTA/creds.json"
creds = service_account.Credentials.from_service_account_file(key_path)
client = vision.ImageAnnotatorClient(credentials=creds)

#WBECAM Y OPENCV
frame_frequency = 0.20
current_second = 0
cap = cv2.VideoCapture(0)


listaBits = []
numeroAnterior = 0
def bitsATexto(bits):
    groups = [bits[i:i+8] for i in range(0, len(bits), 8)]
    mensaje = "".join([chr(int(group, 2)) for group in groups])
    return mensaje

def encontrar_secreto(listaBits):
    secuencia = [0, 1, 0, 0, 0, 0, 0, 0]
    listaSecreto = []
    listaSecretoFinal = []
    i = 0
    secuenciaContador = 0
    while i + 7 < len(listaBits):
        if listaBits[i:i+8] == secuencia:
            if secuenciaContador == 0:
                listaSecreto.clear()
            elif secuenciaContador == 2:
                listaSecretoFinal.extend(listaSecreto)
                mensaje = ''.join(map(str, listaSecretoFinal))
                print(bitsATexto(mensaje))
                return True
            else:
                listaSecretoFinal.extend(listaSecreto)
                listaSecreto.clear()
                i += 8
            secuenciaContador += 1
        else:
            listaSecreto.append(listaBits[i])
            i += 1
    return False


while True:
    #CAM: Fotograma actual
    ret, frame = cap.read()

    if ret:
        # CAM: Fotograma actual en ventana
        cv2.imshow('Webcam', frame)
        cv2.waitKey(1)

        # Fotograma actual a formato JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        image = types.Image(content=buffer.tobytes())

        # Llamada a la API OCR
        response = client.text_detection(image=image)
        texto = response.text_annotations

        if len(texto) > 0:
            all_text = ""
            for text in texto[1:]:
                all_text += text.description + " "
            tag = "FPS"
            if tag in all_text:
                textoAbits = re.sub(r'[^0-9]', '', all_text)
                textoAbits = textoAbits[:2]
                numero = int(textoAbits)
                if numero<58 or numero>61:
                    numero = numeroAnterior
                if (numero != numeroAnterior):
                    numeroAnterior=numero
                    if numero % 2 == 0:
                        listaBits.append(0)
                    else:
                        listaBits.append(1)
                    #print(''.join(map(str, listaBits)))
                    if encontrar_secreto(listaBits):
                        exit()



    else:
        break

# Libera los recursos
cap.release()
cv2.destroyAllWindows()
