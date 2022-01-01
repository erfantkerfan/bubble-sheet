import os

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '15'))

# only place where png is allowed
SHEET_PLAIN = 'sample images/original.png'
SHEET_TEST = 'sample images/test.jpg'

QRCODE_X_OFFSET = 155
QRCODE_Y_OFFSET = 165
QRCODE_SIZE = 310

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
