import cv2
import mediapipe as mp
import os
import numpy as np

from time import sleep

from pynput.keyboard import Controller


BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (255, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (0, 0, 255)
AZUL_CLARO = (255, 255, 0)

teclas = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A','S','D','F','G','H','J','K','L'],
            ['Z','X','C','V','B','N','M', ',','.',' ']]
offset = 50

texto = '>'
contador = 0
teclado = Controller()

cor_pincel = AZUL

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


img_quadro = np.ones((resolucao_y,resolucao_x,3), np.uint8)*255

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



def imprime_botoes(img, posicao, letra, tamanho = 50, cor_retangulo = BRANCO):
    cv2.rectangle(img, posicao, (posicao[0]+tamanho, posicao[1]+tamanho), cor_retangulo, cv2.FILLED)
    cv2.rectangle(img, posicao, (posicao[0]+tamanho, posicao[1]+tamanho), AZUL, 1)
    cv2.putText(img, letra, (posicao[0]+15,posicao[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)
    return img



while True:
    try:
        sucesso, img = camera.read()

        # inverte horizontalmente a imagem [1]
        img = cv2.flip(img, 1)

        img, todas_maos = encontra_coordenadas_maos(img)

        # Gerando o teclado
        cv2.rectangle(img, (50,50), (100,100), BRANCO, cv2.FILLED)
        cv2.putText(img, 'Q', (65,85), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)


        if len(todas_maos) == 1:
            info_dedos_mao1 = dedos_levantados(todas_maos[0])
            print(info_dedos_mao1)

            # Imprime o teclado quando a mão esquerda está levantada
            if todas_maos[0]['lado'] == 'Left':
                # captura corrdenadas da ponta do indicador
                indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]
                cv2.putText(img, f'Distancia camera: {indicador_z}', (850, 50), cv2.FONT_HERSHEY_COMPLEX, 1, BRANCO, 2)

                # Imprime o teclado
                for indice_linha, linha_teclado in enumerate(teclas):
                    for indice, letra in enumerate(linha_teclado):
                        if sum(info_dedos_mao1) <= 1:
                            letra = letra.lower()
                        img = imprime_botoes(img, (offset+indice*80, offset+indice_linha*80),letra)

                        # Percebe quando o indicador está em cima de uma letra
                        if offset+indice*80 < indicador_x < 100+indice*80 and offset+indice_linha*80<indicador_y<100+indice_linha*80:
                            img = imprime_botoes(img, (offset+indice*80, offset+indice_linha*80),letra, cor_retangulo=VERDE)
                            if indicador_z < -100:
                                contador = 1
                                escreve = letra
                                img = imprime_botoes(img, (offset+indice*80, offset+indice_linha*80),letra, cor_retangulo=AZUL_CLARO)

                if contador:
                    contador += 1
                    if contador == 3:
                        texto+= escreve
                        contador = 0
                        teclado.press(escreve)


                # Imprime o texto digitado
                cv2.rectangle(img, (offset, 450), (830, 500), BRANCO, cv2.FILLED)
                cv2.rectangle(img, (offset, 450), (830, 500), AZUL, 1)
                cv2.putText(img, texto[-40:], (offset, 480), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)
                cv2.circle(img, (indicador_x, indicador_y), 7, AZUL, cv2.FILLED)

                # Apaga o último texto
                if info_dedos_mao1 == [False, False, False, True] and len(texto)>1:
                    texto = texto[:-1]
                    sleep(0.15)



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


        if len(todas_maos) == 2:
            info_dedos_mao1 = dedos_levantados(todas_maos[0])
            info_dedos_mao2 = dedos_levantados(todas_maos[1])

            indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]


            if sum(info_dedos_mao2)==1:
                cor_pincel = AZUL
            elif sum(info_dedos_mao2) ==2:
                cor_pincel = VERDE
            elif sum(info_dedos_mao2) == 3:
                cor_pincel = VERMELHO
            elif sum(info_dedos_mao2) == 4:
                cor_pincel = BRANCO
            else:
                img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8)*255

            espessura_pincel = int(abs(indicador_z))//3+5
            cv2.circle(img, (indicador_x, indicador_y), espessura_pincel, cor_pincel, cv2.FILLED)


            # Escreve no quadro com o indicador
            if info_dedos_mao1 == [True, False, False, False]:
                if x_quadro == 0 and y_quadro == 0:
                    x_quadro, y_quadro = indicador_x, indicador_y

                cv2.line(img_quadro, (x_quadro, y_quadro), (indicador_x, indicador_y), cor_pincel, espessura_pincel)

                x_quadro, y_quadro = indicador_x, indicador_y
            else:
                x_quadro, y_quadro = 0, 0

            
            # sobrepõem a imagem
            img = cv2.addWeighted(img, 1, img_quadro, 0.2, 0)


        cv2.imshow("Imagem", img)
        cv2.imshow('Quadro', img_quadro)


        tecla = cv2.waitKey(1)
        if tecla == 27:
            break

    except Exception as e:
        print("Error:", e)
        break

camera.release()
cv2.destroyAllWindows()

with open('texto.txt', 'w') as arquivo:
    arquivo.write(texto)

cv2.imwrite('quadro.png', img_quadro)