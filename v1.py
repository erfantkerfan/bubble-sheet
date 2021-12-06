import urllib

import cv2
import numpy as np
from aiohttp import web
from minio import Minio

import helper


async def minio(request):
    body = await request.post()
    token = body.get('token')
    path = body.get('path')

    client = helper.establish_redis()
    credentials = client.json().get(f'bubblesheet:token:{token}')

    try:
        client = Minio(credentials['endpoint'])
        response = client.get_object(credentials['bucket'], path)
    except:
        raise Exception("path is not valid")
    file_str = response.read()
    np_img = np.frombuffer(file_str, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    return image


async def url(request):
    body = await request.post()
    file_url = body.get('url')
    try:
        req = urllib.request.urlopen(file_url)
    except:
        raise Exception("path is not valid")
    image = cv2.imdecode(np.asarray(bytearray(req.read()), dtype=np.uint8), -1)
    return image


async def direct(request):
    post = await request.post()
    image = post.get("image")
    img_content = image.file.read()
    image = cv2.imdecode(np.asarray(bytearray(img_content), dtype=np.uint8), -1)
    return image


async def test(request):
    image_name = 'alaa.jpg'
    image = cv2.imread(image_name)
    return image


async def process(request: web.Request) -> web.Response:
    type = request.match_info['type']
    try:
        if type == 'minio':
            image = await minio(request)
        elif type == 'url':
            image = await url(request)
        elif type == 'direct':
            image = await direct(request)
        elif type == 'test':
            image = await test(request)
        else:
            status = 404
            return web.Response(status=status)
    except:
        status = 500
        text = "Some thing was wrong with source of image"
        return web.Response(status=status, text=text)


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
        choices = [{'q_n': question, 'c_n': choice} for (question, choice) in enumerate(choices, start=1)]
        response = {'choices': choices}
        return web.json_response(response)
