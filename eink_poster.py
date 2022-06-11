import configparser
import logging
import math
from os import listdir
import os
import random
from PIL import Image

logger = logging.getLogger(__name__)

EPD_WIDTH       = 480
EPD_HEIGHT      = 800

def main():

    config = configparser.ConfigParser()
    config.read('conf.ini')
    Debug_Mode = int(config['General']['DebugMode'])
    
    if Debug_Mode == 0:
        import epd7in5_V2
        epd = epd7in5_V2.EPD()
    else:
        logger.info('-= Debug Mode =-')

    print('-= Updating ePaper... =-')

    posters = listdir(os.path.join(os.getcwd(), "posters"))

    orig_image = Image.open(os.path.join(os.getcwd(), "posters", random.choice(posters)))

    aspect_ratio = orig_image.height / orig_image.width 

    new_width = EPD_WIDTH
    new_height = math.floor(new_width * aspect_ratio)

    resized_image = orig_image.resize((new_width, new_height), Image.ANTIALIAS)

    base_image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 0)  # 255: clear the frame
    y = round((EPD_HEIGHT - new_height) / 2)
    base_image.paste(resized_image, (0,y))

    if Debug_Mode == 1:
        logger.info('-= Viewing ePaper Frames... =-')
        base_image.save("poster_debug.png")
        logger.info('-= ...Done =-')
    else:
        logger.info('-= Updating ePaper... =-')
        epd.init()
        epd.display(epd.getbuffer(base_image))
        epd.sleep()
        logger.info('-= ...Done =-')
        

if __name__ == '__main__':
    main()