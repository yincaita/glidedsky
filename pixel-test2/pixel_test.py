from PIL import Image
import pytesseract

img = Image.open('sprite.jpg')
# 简体中文
content = pytesseract.image_to_string(img)

print(content)
