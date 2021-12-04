import argparse

import cv2
from aiohttp import web

import helper
import v1


async def health(request):
    return web.Response(text='OK')


def test():
    visual = True
    image_name = 'alaa.jpg'
    image = cv2.imread(image_name)

    sheet = helper.SheetNormalizer(image, visual=visual)
    frame, frame_tresh = sheet.get_adaptive_thresh()
    detctor = helper.BubbleReader(frame, frame_tresh, visual=visual)
    keypoints, keypoints_filled, keypoints_empty = detctor.detect_answers()
    choices = detctor.extract_choices(keypoints, keypoints_filled, keypoints_empty)

    print(choices)


def create_app():
    app = web.Application()
    # Routes
    app.add_routes([
        web.get('/api/health/check', health),

        web.post('/api/v1/scan/minio', v1.minio),
        web.post('/api/v1/scan/http', v1.http),
        web.post('/api/v1/scan/direct', v1.direct),
        web.post('/api/v1/scan/test', v1.test),
    ])
    return app


if __name__ == '__main__':
    version = '0.1.0'
    parser = argparse.ArgumentParser(description='Process bubble sheets.')
    parser.add_argument('-v', '--version', action='version', version=f'{version}')
    parser.add_argument('-t', '--test', help="show visual result for debug.", action="store_true")
    parser.add_argument('-p', '--port', help="accept port number defaults to 8080", default=8080, type=int)
    args = parser.parse_args()

    if args.test:
        test()
        exit()

    web.run_app(create_app(), port=args.port)
