import PIL
import cv2
import pytesseract
import numpy as np
from PIL import Image


altura = 150
img = Image.open("imgTeste.jpg")
a_percent = (altura / float(img.size[1]))
largura = int((float(img.size[0]) * float(a_percent)))
img = img.resize((largura, altura), Image.ANTIALIAS)
img.save("imgTeste.png")


img = cv2.imread("imgTeste.png", 0)
limiar, img_limiar = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
img_limiar = cv2.bilateralFilter(img_limiar, 11, 17, 17)
#img_limiar = cv2.GaussianBlur(img_limiar,(5,5), cv2.BORDER_DEFAULT)
cv2.imwrite("imgTeste.png", img_limiar)


#OCR
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
txt_captcha = pytesseract.image_to_string("imgTeste.jpg", lang = "Arial+Comic")

print(txt_captcha)

#com a adição de Arial.traineddata e Comic.traineddata em C:\Program Files (x86)\Tesseract-OCR\tessdata
#observei uma melhora significativa na precisão, porém O ainda é confundido com 0 e Q com O, por exemplo.
#se preciso reconhecer "7BS0" em uma imagem, obtenho "7BSO" como resultado. a adição de modelos ao método
#image_to_string é uma boa opção quando sabemos quais são as fontes utilizadas na imagem em questão.
