import io
import pathlib
import urllib
import zipfile
from zipfile import ZipFile

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageFont, ImageDraw
from aiohttp import web
from minio import Minio

import helper
from constants import *


async def minio_put(request, image):
    body = await request.post()
    token = body.get('token')
    path_choices = body.get('path_choices', None)
    if path_choices:
        client = helper.establish_redis()
        credentials = client.json().get(f'bubblesheet:token:{token}')

        extension = pathlib.Path(path_choices).suffix
        is_success, buffer = cv2.imencode(extension, image)
        io_buf = io.BytesIO(buffer)
        client = Minio(credentials['endpoint'], credentials['accessKey'], credentials['secretKey'])
        client.put_object(credentials['bucket'], path_choices, io_buf, -1, part_size=10 * 1024 * 1024)

    return path_choices


async def load_image_minio(request):
    body = await request.post()
    token = body.get('token')
    path = body.get('path')

    client = helper.establish_redis()
    credentials = client.json().get(f'bubblesheet:token:{token}')

    try:
        client = Minio(credentials['endpoint'], credentials['accessKey'], credentials['secretKey'])
        response = client.get_object(credentials['bucket'], path)
    except:
        raise Exception("path is not valid")
    file_str = response.read()
    print(type(file_str))
    np_img = np.frombuffer(file_str, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    return image


async def load_image_url(request):
    body = await request.post()
    file_url = body.get('url')
    try:
        req = urllib.request.urlopen(file_url)
    except:
        raise Exception("path is not valid")
    image = cv2.imdecode(np.asarray(bytearray(req.read()), dtype=np.uint8), -1)
    return image


async def load_image_direct(request):
    post = await request.post()
    image = post.get("image")
    img_content = image.file.read()
    image = cv2.imdecode(np.asarray(bytearray(img_content), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    return image


async def load_image_sample(request):
    image_name = SHEET_TEST
    image = cv2.imread(image_name)
    return image


async def scan(request: web.Request) -> web.Response:
    type = request.match_info['type']
    try:
        if type == 'minio':
            image = await load_image_minio(request)
        elif type == 'url':
            image = await load_image_url(request)
        elif type == 'direct':
            image = await load_image_direct(request)
        elif type == 'test':
            image = await load_image_sample(request)
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
        detctor = helper.BubbleReader(frame, frame_tresh, with_markers=True)
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

        if type == 'minio':
            try:
                await minio_put(request, detctor.get_sheet_with_choices())
            except:
                raise Exception("something went wrong when saving file")

        return web.json_response(response)


async def generate(request: web.Request) -> web.Response:
    # load initial values
    body = await request.json()
    token = body['token']
    output_path = body['path']
    data_list = body['data']

    # simple input validation
    if not output_path.endswith('zip'):
        return web.Response(status=422)

    # create a zip file in memory
    in_memory = io.BytesIO()
    zip_file = ZipFile(in_memory, compression=zipfile.ZIP_DEFLATED, compresslevel=9, mode="w")

    # load empty bubble sheet
    bare_sheet = cv2.imread(SHEET_PLAIN)

    # load font for typing in pics
    font_large = ImageFont.truetype('IRANYekanRegularFaNum.ttf', 35, encoding='unic')
    font_medium = ImageFont.truetype('IRANYekanRegularFaNum.ttf', 30, encoding='unic')
    font_small = ImageFont.truetype('IRANYekanRegularFaNum.ttf', 25, encoding='unic')

    # loop through requested files
    for i, data in enumerate(data_list):
        # get a new instance of sheet
        sheet = bare_sheet.copy()

        # load image from cv2 to pil
        bare_sheet_in_pil = Image.fromarray(cv2.cvtColor(sheet, cv2.COLOR_BGR2RGB))
        # draw text on image
        draw = ImageDraw.Draw(bare_sheet_in_pil)
        # TODO: validation for all fields
        if len(data['name']) <= 20:
            draw.text(xy=(870, 268), text=data['name'], fill=(0, 0, 0), font=font_large, anchor='rm')
        elif len(data['name']) <= 25:
            draw.text(xy=(870, 268), text=data['name'], fill=(0, 0, 0), font=font_medium, anchor='rm')
        else:
            draw.text(xy=(870, 268), text=data['name'][:30], fill=(0, 0, 0), font=font_small, anchor='rm')

        if len(data['ostan']) <= 10:
            draw.text(xy=(1015, 370), text=data['ostan'], fill=(0, 0, 0), font=font_large, anchor='rm')
        elif len(data['ostan']) <= 15:
            draw.text(xy=(1015, 370), text=data['ostan'], fill=(0, 0, 0), font=font_medium, anchor='rm')
        else:
            draw.text(xy=(1015, 370), text=data['ostan'][:19], fill=(0, 0, 0), font=font_small, anchor='rm')

        if len(data['shahr']) <= 7:
            draw.text(xy=(700, 370), text=data['shahr'], fill=(0, 0, 0), font=font_large, anchor='rm')
        elif len(data['shahr']) <= 12:
            draw.text(xy=(700, 370), text=data['shahr'], fill=(0, 0, 0), font=font_medium, anchor='rm')
        else:
            draw.text(xy=(700, 370), text=data['shahr'][:16], fill=(0, 0, 0), font=font_small, anchor='rm')

        draw.text(xy=(1320, 343), text=data['duration'], fill=(0, 0, 0), font=font_medium, anchor='rm')

        draw.text(xy=(1665, 343), text=data['date'], fill=(0, 0, 0), font=font_medium, anchor='rm')

        draw.text(xy=(1650, 400), text=data['start'], fill=(0, 0, 0), font=font_medium, anchor='rm')

        draw.text(xy=(1780, 263), text=data['exam_description'], fill=(0, 0, 0), font=font_medium, anchor='rm')
        # convert pil image back to  cv2 mode
        sheet = np.asarray(bare_sheet_in_pil)

        # generate qr code object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=1,
        )
        # TODO: validation for qrcode
        qr.add_data(data['qrcode'])
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='#000000', back_color='#FFFFFF').convert('RGB')
        # load qr code in opencv
        open_cv_qr_image = cv2.resize(np.array(qr_img)[:, :, ::-1].copy(), (QRCODE_SIZE, QRCODE_SIZE))
        # replace desired pixels with qrcode
        sheet = cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR)
        sheet[QRCODE_Y_OFFSET:QRCODE_Y_OFFSET + open_cv_qr_image.shape[0],
        QRCODE_X_OFFSET:QRCODE_X_OFFSET + open_cv_qr_image.shape[1]] = open_cv_qr_image

        # write qrcode to memory and add it to zip file
        retval, buffer = cv2.imencode('.jpg', sheet)
        zip_file.writestr(f'{data["name"]}.jpg', buffer)

    # Close the zip file
    zip_file.close()

    # Go to beginning of zip file in memory
    in_memory.seek(0)

    client = helper.establish_redis()
    credentials = client.json().get(f'bubblesheet:token:{token}')

    client = Minio(credentials['endpoint'], credentials['accessKey'], credentials['secretKey'])
    client.put_object(credentials['bucket'], output_path, in_memory, -1, part_size=10 * 1024 * 1024)
    return web.Response(status=200)


async def detect(request: web.Request) -> web.Response:
    type = request.match_info['type']
    try:
        if type == 'minio':
            image = await load_image_minio(request)
        elif type == 'url':
            image = await load_image_url(request)
        elif type == 'direct':
            image = await load_image_direct(request)
        elif type == 'test':
            image = await load_image_sample(request)
        else:
            status = 404
            return web.Response(status=status)
    except:
        status = 500
        text = "Some thing was wrong with source of image"
        return web.Response(status=status, text=text)

    try:
        # initialize the cv2 QRCode detector
        detector = cv2.QRCodeDetector()
        # detect and decode
        temp = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        frame_tresh = cv2.adaptiveThreshold(temp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 95,
                                                 7)
        data, vertices_array, binary_qrcode = detector.detectAndDecode(frame_tresh)
        # if there is a QR code
        if vertices_array is not None and len(data) != 0:
            status = 200
            text = data
        else:
            status = 500
            text = "qr code could not be obtained"
        return web.json_response(status=status, text=text)
    except:
        status = 500
        text = "qrcode data could not be obtained"
        return web.json_response(status=status, text=text)
