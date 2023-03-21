import cv2
import mediapipe as mp
import os

# instancia as variáveis do mediapipe
mp_maos = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils
maos = mp_maos.Hands()

# Captura a câmera
camera = cv2.VideoCapture(0)
if not (camera.isOpened()):
    print("Could not open video device")

# Seta o tamanho da imagem
resolucao_x = 1280
resolucao_y = 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)


# Aplicações abertas
bloco_notas_aberto = False


def encontra_coordenadas_maos(img, lado_invertido = False):
    # O método process() espera que sejam utilizadas imagens em RGB, portanto, caso a leitura das imagens tenha sido feita com o OpenCV, será necessário fazer uma conversão das imagens para RGB antes de realizar o processamento.
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # processa a imagem com o mediapipe para identificar os pontos da mão na imagem
    # O método tem como resultado o MULTI_HAND_LANDMARKS, MULTI_HAND_WORLD_LANDMARKS e MULTI_HANDEDNESS.
    resultado = maos.process(img_rgb)

    todas_maos = []

    # se houver uma mão na imagem, desenha ela na img
    if resultado.multi_hand_landmarks:

        for lado_mao, marcacao_maos in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):

            info_mao = {}
            coordenadas = []


            # salva as variáveis de cordenada de cada ponto da mão em pixels na imagem
            for marcacao in marcacao_maos.landmark:
                coord_x, coord_y, coord_z = int(marcacao.x * resolucao_x), int(marcacao.y * resolucao_y), int(marcacao.z * resolucao_x)
                coordenadas.append((coord_x, coord_y, coord_z))


            # define qual lado da mão foi encontarado
            info_mao['coordenadas'] = coordenadas

            if lado_invertido:
                if lado_mao.classification[0].label == 'Left':
                    info_mao['lado'] = 'Right'
                else:
                    info_mao['lado'] = 'Left'

            else:
                info_mao['lado'] = lado_mao.classification[0].label



            todas_maos.append(info_mao)

            # aplica o desenho da mão na imagem
            mp_desenho.draw_landmarks(img,
                                        marcacao_maos,
                                        mp_maos.HAND_CONNECTIONS)
            
            # cada uma das marcações está presente dentro da variável marcação_maos
            # print(marcacao_maos)

    return img, todas_maos


# Confere se o polegar está levantado
# def dedos_levantados(mao):
#     dedos = []
#     if mao['lado'] == 'Right': 
#         if mao['coordenadas'][4][0] < mao['coordenadas'][3][0]:
#             dedos.append(True)
#         else:
#             dedos.append(False)
#     else:
#         if mao['coordenadas'][4][0] > mao['coordenadas'][3][0]:
#             dedos.append(True)
#         else:
#             dedos.append(False)
#     for ponta_dedo in [8,12,16,20]:
#         if mao['coordenadas'][ponta_dedo][1] < mao['coordenadas'][ponta_dedo-2][1]:
#             dedos.append(True)
#         else:
#             dedos.append(False)
#     return dedos




def dedos_levantados(mao):
    dedos = []
    for ponta_dedo in [8, 12, 16, 20]:
        # confere se o dedo está levantado
        if mao['coordenadas'][ponta_dedo][1] < mao['coordenadas'][ponta_dedo - 2][1]:
            dedos.append(True)
        else:
            dedos.append(False)

    return dedos




while True:
    try:
        sucesso, img = camera.read()

        # inverte horizontalmente a imagem [1]
        img = cv2.flip(img, 1)

        img, todas_maos = encontra_coordenadas_maos(img)


        if len(todas_maos) == 1:
            info_dedos_mao1 = dedos_levantados(todas_maos[0])
            print(info_dedos_mao1)

            if todas_maos[0]['lado'] == 'Right':
                # Abre o notepad
                if info_dedos_mao1 == [True, False, False, False] and bloco_notas_aberto == False:
                    os.startfile(r'C:\Windows\System32\notepad.exe')
                    bloco_notas_aberto = True

                # Fecha o notepad
                if info_dedos_mao1 == [False, False, False, False] and bloco_notas_aberto == True:
                    os.system('TASKKILL /IM notepad.exe')
                    bloco_notas_aberto = False


                # Encerra o programa
                if info_dedos_mao1 == [True, False, False, True]:
                    break



        cv2.imshow("Imagem", img)
        tecla = cv2.waitKey(1)
        if tecla == 27:
            break

    except Exception as e:
        print("Error:", e)
        break

camera.release()
cv2.destroyAllWindows()