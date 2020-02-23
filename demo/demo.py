from aiohttp import web
from aiohttp_session import setup as session_setup, SimpleCookieStorage
from aiohttp_simple_csrf import generate_csrf_token, validate_csrf_token


async def index(request):
    html = """
            <html>
              <head>
                <title>
                  Hello World
                </title>
              </head>
            </html>
            <body>
              <form method="POST">
                <input type="hidden" name="csrf_token" value="{csrf_token}"/>
                <input name="somefield" type="text" value=""/>
                <input type="submit" name="submit" value="Submit" />
              </form>
            </body>
            """

    csrf_token = await generate_csrf_token(request)
    html = html.format(csrf_token=csrf_token)
    if request.method == 'POST':
        if await validate_csrf_token(request):
            return web.Response(text='Token is valid')
    return web.Response(body=html.encode('utf-8'), content_type='text/html',)


app = web.Application()
session_setup(app, SimpleCookieStorage())
app.router.add_get('/', index)
app.router.add_post('/', index)
web.run_app(app)
