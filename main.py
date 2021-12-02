import argparse

import cv2
from aiohttp import web

import helper
import v1


async def health(request):
    return web.Response(text='OK')


def test():
    image_name = 'alaa.jpg'
    image = cv2.imread(image_name)
    x = helper.SheetNormalizer(image, visual=True)
    helper.BubbleReader(x.frame, x.frame_tresh, visual=True)


def create_app():
    app = web.Application()
    # Routes
    app.add_routes([
        web.get('/api/health/check', health),

        web.get('/api/v1/scan/minio', v1.minio),
        web.post('/api/v1/scan/http', v1.http),
        web.get('/api/v1/scan/direct', v1.direct),
        web.get('/api/v1/scan/test', v1.test),
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
