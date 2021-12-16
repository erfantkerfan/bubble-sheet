import argparse
import secrets

import cv2
from aiohttp import web
from redis.commands.json.path import Path
from tqdm import tqdm

import helper
import v1


async def health(request):
    return web.Response(text='OK')


def test():
    visual = True
    with_markers = True
    image_name = 'alaa.jpg'
    image = cv2.imread(image_name)

    sheet = helper.SheetNormalizer(image, visual=visual)
    frame, frame_tresh = sheet.get_adaptive_thresh()
    detctor = helper.BubbleReader(frame, frame_tresh, with_markers=with_markers, visual=visual)
    keypoints, keypoints_filled, keypoints_empty = detctor.detect_answers()
    choices = detctor.extract_choices(keypoints, keypoints_filled, keypoints_empty)
    sheet_with_choices = detctor.get_sheet_with_choices()

    print(len(sheet_with_choices))
    print(len(choices))
    print(choices)


def token():
    print(secrets.token_urlsafe(32))


def set_token():
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


def migrate():
    client = helper.establish_redis()
    from seeds import users
    for user in tqdm(users):
        token = user.pop('token')
        client.json().set(f'bubblesheet:token:{token}', Path.rootPath(), user)


def create_app():
    app = web.Application()
    # Routes
    app.add_routes([
        web.get('/api/health/check', health),

        web.post('/api/v1/scan/{type}', v1.process),
    ])
    return app


if __name__ == '__main__':
    VERSION = '0.4.0'

    parser = argparse.ArgumentParser(description='Process bubble sheets.')
    parser.add_argument('-v', '--version', action='version', version=f'{VERSION}')
    parser.add_argument('-t', '--test', help="show visual result for debug.", action="store_true")
    parser.add_argument('-T', '--token', help="generate a url_safe token.", action="store_true")
    parser.add_argument('-S', '--set', help="set up a token for minio endpoint", action="store_true")
    parser.add_argument('--migrate', help="export seeds folder to redis.", action="store_true")
    parser.add_argument('-p', '--port', help="accept port number defaults to 8080", default=8080, type=int)
    args = parser.parse_args()

    if args.test:
        test()
        exit()

    if args.token:
        token()
        exit()

    if args.migrate:
        migrate()
        exit()

    if args.set:
        set_token()
        exit()

    web.run_app(create_app(), port=args.port)
