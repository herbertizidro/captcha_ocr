import PIL
import cv2
import pytesseract
import numpy as np
from PIL import Image
from io import BytesIO
from selenium import webdriver


#acessa o site, localiza o captcha e printa a tela
browser = webdriver.Chrome(r"C:\Users\<USER>\Downloads\chromedriver_win32\chromedriver.exe")
browser.get('<SITE>')
browser.maximize_window()

captcha = browser.find_element_by_xpath('<XPATH>')
localizacao = captcha.location
tamanho = captcha.size
png = browser.get_screenshot_as_png()

img = Image.open(BytesIO(png)) #abre a imagem na memória


#corta a imagem de acordo com as coordenadas obtidas
esquerda = localizacao["x"]
superior = localizacao["y"]
direita = localizacao["x"] + tamanho["width"]
inferior = localizacao["y"] + tamanho["height"]

img = img.crop((esquerda, superior, direita, inferior)) #corte
img.save("screenshot.png")


#redimensiona
altura = 150
img = Image.open('screenshot.png')
a_percent = (altura / float(img.size[1]))
largura = int((float(img.size[0]) * float(a_percent)))
img = img.resize((largura, altura), Image.ANTIALIAS)
img.save('screenshot.png')


#binariza
img = cv2.imread("screenshot.png", 0)
limiar, img_limiar = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
#aplica desfoque na imagem
img_limiar = cv2.GaussianBlur(img_limiar,(5,5), cv2.BORDER_DEFAULT)
#img_limiar = cv2.bilateralFilter(img_limiar, 11, 17, 17)
cv2.imwrite("screenshot.png", img_limiar)


#OCR
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
txt_captcha = pytesseract.image_to_string("screenshot.png", config="--oem 3 --psm 11 tessedit_char_whitelist=ABCDEFGHIJLMNOPQRSTUVXZYW0123456789")


#input captcha
captcha_txt_input = browser.find_element_by_xpath('XPATH')
txt_captcha = txt_captcha.replace(" ", "")
captcha_txt_input.send_keys(txt_captcha.upper())

browser.quit()
