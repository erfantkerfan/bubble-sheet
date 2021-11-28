import urllib

import cv2
import numpy as np
from aiohttp import web
from minio import Minio

import helper


async def minio(request):
    client = Minio('nodes.alaatv.com')
    response = client.get_object('test', 'alaa.png')
    file_str = response.read()
    np_img = np.frombuffer(file_str, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    sheet = helper.SheetNormalizer(img)

    text = 'minio'
    return web.Response(text=text)


async def http(request):
    url = 'https://nodes.alaatv.com/test/alaa.png'
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    sheet = helper.SheetNormalizer(img)

    text = 'http'
    return web.Response(text=text)


async def direct(request):
    text = 'direct'
    return web.Response(text=text)


async def test(request):
    image_name = 'alaa.png'
    image = cv2.imread(image_name)
    sheet = helper.SheetNormalizer(image)
    # ////////
    text = 'test'
    return web.Response(text=text)
