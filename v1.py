import urllib

import cv2
import numpy as np
from aiohttp import web
from minio import Minio

import helper


async def minio(request):
    client = Minio('nodes.alaatv.com')
    response = client.get_object('test', 'alaa.jpg')
    file_str = response.read()
    np_img = np.frombuffer(file_str, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    try:
        sheet = helper.SheetNormalizer(image)
        frame, frame_tresh = sheet.get_adaptive_thresh()
    except:
        status = 500
        text = "Could not load the image properly"
        return web.Response(status=status, text=text)
    else:
        detctor = helper.BubbleReader(frame, frame_tresh)
        try:
            keypoints, keypoints_filled, keypoints_empty = detctor.detect_answers()
        except:
            status = 500
            text = "number of keypoints not valid"
            return web.Response(status=status, text=text)
        else:
            choices = detctor.extract_choices(keypoints, keypoints_filled, keypoints_empty)
        choices = {index: x for index, x in enumerate(choices, start=1)}
        return web.json_response(choices)


async def http(request):
    body = await request.post()
    url = body.get('url')
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
    image_name = 'alaa.jpg'
    image = cv2.imread(image_name)
    try:
        sheet = helper.SheetNormalizer(image)
        frame, frame_tresh = sheet.get_adaptive_thresh()
    except:
        status = 500
        text = "Could not load the image properly"
        return web.Response(status=status, text=text)
    else:
        detctor = helper.BubbleReader(frame, frame_tresh)
        try:
            keypoints, keypoints_filled, keypoints_empty = detctor.detect_answers()
        except:
            status = 500
            text = "number of keypoints not valid"
            return web.Response(status=status, text=text)
        else:
            choices = detctor.extract_choices(keypoints, keypoints_filled, keypoints_empty)
        choices = [{'q_n': question, 'c_n': choice} for (question, choice) in enumerate(choices)]
        response = {'choices': choices}
        return web.json_response(response)
