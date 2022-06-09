from PIL import ImageFont
import random

global font_quote_text; font_quote_text = ImageFont.truetype('fonts/tahoma.ttf', 18)
global font_quote_marks; font_quote_marks = ImageFont.truetype('fonts/IMFellDWPicaSC-Regular.ttf', 60)

EPD_WIDTH       = 480

def render_quotes(draw_black):
    line_location = 735
    quotes_file = open("quotes.txt", "r")
    quotes = quotes_file.readlines()
    draw_black.text((10, 720), "“", font = font_quote_marks, fill = 0)
    quote_text = bytearray(random.choice(quotes), 'utf-8').decode('unicode_escape').splitlines()
    for quote_text_line in quote_text:
        w, h = draw_black.textsize(quote_text_line, font=font_quote_text)
        draw_black.text(((EPD_WIDTH-w)/2, line_location), quote_text_line, font = font_quote_text, fill = 0)
        line_location += h
    draw_black.text((440, 760), "”", font = font_quote_marks, fill = 0)