import os
import cv2
import PIL
import time
import numpy as np
import pytesseract
from PIL import Image
from io import BytesIO
from selenium import webdriver


while True:
    #acessa o site e maximiza a tela
    browser = webdriver.Chrome(r"C:\Users\<-USER->\Downloads\chromedriver_win32\chromedriver.exe")
    browser.get("<-SITE->")
    browser.maximize_window()
    
    
    #login
    cpf = "<-CPF->"
    cpf_input = browser.find_element_by_xpath('<-XPATH->')
    for i in cpf:
        time.sleep(0.2)
        cpf_input.send_keys(i)
    senha_input = browser.find_element_by_xpath('<-XPATH->')
    senha_input.send_keys("<-SENHA->")
    #login


    #localiza a imagem e recorta de acordo com coordenadas obtidas
    captcha = browser.find_element_by_xpath('<-XPATH->')
    localizacao = captcha.location
    tamanho = captcha.size
    
    png = browser.get_screenshot_as_png()
    img = Image.open(BytesIO(png)) #abre a imagem na memória
    
    esquerda = localizacao["x"]
    superior = localizacao["y"]
    direita = localizacao["x"] + tamanho["width"]
    inferior = localizacao["y"] + tamanho["height"]
    
    img = img.crop((esquerda, superior, direita, inferior)) #corte
    img.save("screenshot.png")


    #redimensiona
    altura = 400
    img = Image.open('screenshot.png')
    a_percent = (altura / float(img.size[1]))
    largura = int((float(img.size[0]) * float(a_percent)))
    img = img.resize((largura, altura), Image.ANTIALIAS)
    img.save('screenshot.png')


    #binariza
    img = cv2.imread("screenshot.png", 0)
    _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
    thresh = cv2.bilateralFilter(thresh, 11, 17, 17)
    cv2.imwrite("screenshot.png", thresh)


    #tratamento para encontrar os contornos
    img = cv2.imread("screenshot.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _,thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV) #o fundo deve ser preto e o objeto branco
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3)) #https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
    dilatacao = cv2.dilate(thresh, kernel, iterations = 13)
    contornos, h = cv2.findContours(dilatacao, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)


    #organiza as coordenadas de acordo com a posição de cada caractere no eixo X
    #ou seja, não importa a posição do caractere no eixo Y, o que estiver
    #mais à esquerda será o primeiro
    coordenadas = []
    posicao_x = []  #array para o X de cada coordenada
    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)
        coordenadas.append([x, y, w, h])
        posicao_x.append(x)
    posicao_x = sorted(posicao_x, key=int)  #ordena o array
    #ordena as coordenadas de acordo com a ordem do array "posicao_x"
    coordenadas_ordenadas = []
    for pos in posicao_x:
        for coor in coordenadas:
            if pos == coor[0]:
                coordenadas_ordenadas.append(coor)


    #recorta as letras e salva na pasta "letras"
    if os.path.isdir("./letras") == False:
        os.mkdir("./letras")
    if len(coordenadas_ordenadas) == 3: #nesse caso serão sempre 3 caracteres
        aux = 0   
        for coor in coordenadas_ordenadas:
            aux += 1
            x, y, w, h = coor
            recorte_letra = img[y:y + h, x:x + w]
            cv2.imwrite("./letras/" + str(aux) + ".png", recorte_letra)
    else:
       browser.quit()
       continue


    #OCR
    txt_captcha = []
    letras_dir = os.listdir("./letras")
    for letra in letras_dir:
        letra = os.getcwd() + "\\letras\\" + letra
        pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
        ocr = pytesseract.image_to_string(Image.open(letra), config = "--psm 10")
        txt_captcha.append(ocr)


    #limpa o resultado
    txt_captcha = [i for i in txt_captcha if i.isalnum()] #só o que for letra ou número
    txt_captcha = str(txt_captcha).strip("[]").replace(",", "").replace("'", "").replace(" ", "")
    

    #input captcha
    captcha_txt_input = browser.find_element_by_xpath('<-XPATH->')
    captcha_txt_input.send_keys(txt_captcha.upper())

    
    #clica em 'entrar'
    browser.find_element_by_xpath('<-XPATH->').click()
    browser.implicitly_wait(60)


    try:
        mensagem_modal = browser.find_element_by_class_name("<-CLASS_NAME->").text
        browser.quit()
    except:
        #
        # MAIS ALGUMA COISA AQUI ...
        #
        browser.quit()
        break
    



'''
Page segmentation modes(psm):
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR.
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.
 11    Sparse text. Find as much text as possible in no particular order.
 12    Sparse text with OSD.
 13    Raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific.
'''
