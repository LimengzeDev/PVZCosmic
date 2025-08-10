from PIL import Image

# 打开一张图片
img = Image.open("Dave.gif")

# 显示图片
img.show()

# 获取图片信息
print("图片格式:", img.format)  # JPEG, PNG, etc.
print("图片大小:", img.size)    # (width, height)
print("图片模式:", img.mode)   # RGB, L, etc.