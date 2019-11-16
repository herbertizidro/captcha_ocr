import io
import os
import PIL
import cv2
import time
#import pytesseract
import numpy as np
from PIL import Image
from io import BytesIO
from selenium import webdriver
from google.cloud import vision
from google.cloud.vision import types

while True:

    browser = webdriver.Chrome(r"C:\Users\<USER>\Downloads\chromedriver_win32\chromedriver.exe")
    browser.get("<SITE>")
    browser.maximize_window()

    cpf = "<CPF>"

    #login
    cpf_input = browser.find_element_by_xpath('<XPATH>')
    for i in cpf:
        time.sleep(1) #evitar problemas com - e . adicionados automaticamente no input
        cpf_input.send_keys(i)

    senha_input = browser.find_element_by_xpath('<XPATH>')
    senha_input.send_keys("<SENHA>")
    #login


    captcha = browser.find_element_by_xpath('<XPATH>')
    localizacao = captcha.location
    tamanho = captcha.size
    png = browser.get_screenshot_as_png()

    img = Image.open(BytesIO(png)) #abre a imagem na memória

    #corta a imagem de acordo com coordenadas obtidas
    esquerda = localizacao["x"]
    superior = localizacao["y"]
    direita = localizacao["x"] + tamanho["width"]
    inferior = localizacao["y"] + tamanho["height"]

    img = img.crop((esquerda, superior, direita, inferior)) #corte
    img.save("screenshot.png")


    #redimensiona
    altura = 150
    img = Image.open("screenshot.png")
    a_percent = (altura / float(img.size[1]))
    largura = int((float(img.size[0]) * float(a_percent)))
    img = img.resize((largura, altura), Image.ANTIALIAS)
    img.save("screenshot.png")


    #binariza
    img = cv2.imread("screenshot.png", 0)
    limiar, img_limiar = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    #img_limiar = cv2.bilateralFilter(img_limiar, 11, 17, 17)
    cv2.imwrite("screenshot.png", img_limiar)


    #VISION API
    #https://cloud.google.com/vision/?hl=pt-br
    #https://googleapis.github.io/google-cloud-python/latest/vision/index.html
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "<...>.json"
    client = vision.ImageAnnotatorClient()
    file_name = os.path.join(os.path.dirname(__file__), "screenshot.png")
    with io.open(file_name, "rb") as image_file:
        content = image_file.read()
    image = types.Image(content = content)
    response = client.text_detection(image = image)

    aux = []
    for text in response.text_annotations:
        aux.append(text.description)
    #VISION API


    print(aux)
    aux = aux[0]
    aux = str(aux)
    ruido = ["\n", ".", " "] #caracteres indesejados 
    for i in aux:
        if i in ruido:
            aux = aux.replace(i, "")


    #input captcha
    captcha_txt_input = browser.find_element_by_xpath('<XPATH>')
    captcha_txt_input.send_keys(aux.upper())

    #clicar em 'entrar'
    browser.find_element_by_xpath('<XPATH>').click()
    browser.implicitly_wait(60)


    try:
        mensagem_erro = browser.find_element_by_class_name("<CLASS>").text
        browser.quit()
    except:
        #
        # MAIS ALGUMA COISA AQUI
        #
        browser.quit()
        break
