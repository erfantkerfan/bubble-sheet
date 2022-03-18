import secrets
from pprint import pprint

import cv2
from redis.commands.json.path import Path
from tqdm import tqdm

import helper
from constants import *


def test():
    visual = True
    with_markers = True
    image_name = SHEET_TEST
    image = cv2.imread(image_name)

    sheet = helper.SheetNormalizer(image, visual=visual)
    frame, frame_tresh = sheet.get_adaptive_thresh()
    detctor = helper.BubbleReader(frame, frame_tresh, with_markers=with_markers, visual=visual)
    keypoints, keypoints_filled, keypoints_empty = detctor.detect_answers()
    choices = detctor.extract_choices(keypoints, keypoints_filled, keypoints_empty)
    sheet_with_choices = detctor.get_sheet_with_choices()

    print(choices)
    print()
    print(f'{len(choices)} questions')
    print()
    print(f'{len(sheet_with_choices)} px')


def token():
    print(secrets.token_urlsafe(32))


def set():
    data = {
        "endpoint": input('please enter an endpoint like "nodes.alaatv.com":'),
        "bucket": input('please enter your desired bucket like "pictures":'),
        "accessKey": input('please enter accessKey:'),
        "secretKey": input('please enter secretKey:'),
    }
    token = secrets.token_urlsafe(32)
    client = helper.establish_redis()
    client.json().set(f'bubblesheet:token:{token}', Path.rootPath(), data)

    print(f'your token is "{token}" keep this it safe.')


def dump():
    client = helper.establish_redis()
    for key in client.scan_iter("bubblesheet:token:*"):
        user = client.json().get(key, Path.rootPath())
        user['token'] = str(key.decode('utf8'))
        pprint(user)
