import epd7in5_V2
import math
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os

def main():
    epd = epd7in5_V2.EPD()
    epd.init()
    print('-= Updating ePaper... =-')
    orig_image = Image.open('motivational_picture.png')

    aspect_ratio = orig_image.height / orig_image.width 

    new_width = 480
    new_height = math.floor(new_width * aspect_ratio)

    resized_image = orig_image.resize((new_width, new_height), Image.ANTIALIAS)

    base_image = Image.new('1', (epd.height, epd.width), 0)  # 255: clear the frame
    base_image.paste(resized_image, (0,0))

    epd.display(epd.getbuffer(base_image))
    print('-= ...Done =-')
    epd.sleep()

if __name__ == '__main__':
    main()