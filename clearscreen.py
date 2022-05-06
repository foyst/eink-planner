#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import epd7in5_V2

logging.basicConfig(level=logging.DEBUG)

try:
    epd = epd7in5_V2.EPD()

    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)