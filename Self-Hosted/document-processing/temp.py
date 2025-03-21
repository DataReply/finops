from PIL import Image
import pytesseract

# Create a test image with text
img = Image.new('RGB', (200, 100), color=(255, 255, 255))
text = pytesseract.image_to_string(img)
print(text)
