import argparse

from aiohttp import web

import commands
import v1


async def health(request):
    return web.Response(text='OK')


def create_app():
    app = web.Application()
    # Routes
    app.add_routes([
        web.get('/api/health/check', health),

        web.post('/api/v1/scan/{type}', v1.scan),
        web.post('/api/v1/generate/minio', v1.generate),
        web.post('/api/v1/detect/{type}', v1.detect),
    ])
    return app


if __name__ == '__main__':
    VERSION = 'v1.2.2'

    parser = argparse.ArgumentParser(description='Process bubble sheets.')
    parser.add_argument('-v', '--version', action='version', version=f'{VERSION}')
    parser.add_argument('-t', '--test', help="show visual result for debug.", action="store_true")
    parser.add_argument('-T', '--token', help="generate a url_safe token.", action="store_true")
    parser.add_argument('-s', '--set', help="set up a token for minio endpoint", action="store_true")
    parser.add_argument('-l', '--dump', help="show available credentials and tokens", action="store_true")
    parser.add_argument('--migrate', help="export seeds folder to redis.", action="store_true")
    parser.add_argument('-p', '--port', help="accept port number defaults to 8080", default=8080, type=int)
    args = parser.parse_args()

    command_list = ['test', 'token', 'set', 'dump', 'migrate']
    for command in command_list:
        if getattr(args, command, None):
            getattr(commands, command)()
            exit()
    print(f'server starting {VERSION}')
    web.run_app(create_app(), port=args.port)
