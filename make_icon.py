from PIL import Image, ImageDraw

img = Image.new("RGBA", (256, 256), (0, 0, 0, 255))
draw = ImageDraw.Draw(img)

# Box outline
draw.rectangle([50, 80, 206, 200], outline="white", width=10)
# Middle divider line
draw.line([50, 140, 206, 140], fill="white", width=8)
# Trend line going up
draw.line([70, 185, 110, 150, 150, 168, 200, 105], fill="white", width=8)
# Dot at peak
draw.ellipse([188, 93, 212, 117], fill="white")

img.save("icon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(256,256)])
print("icon.ico created successfully!")