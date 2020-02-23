import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

from aiohttp_session import (SimpleCookieStorage,
                             setup as setup_session)

from aiohttp_simple_csrf import (generate_csrf_token,
                                 validate_csrf_token,
                                 setup as setup_csrf,
                                 CSRF_FIELD_NAME,
                                 CSRF_METHODS,
                                 CSRF_HEADERS)


class TestCSRFCase(AioHTTPTestCase):

    async def get_application(self):
        async def index(request):
            csrf_token = await generate_csrf_token(request)
            if request.method in CSRF_METHODS:
                await validate_csrf_token(request)
                return web.Response()
            return web.Response(text=csrf_token)

        app = web.Application()
        setup_session(app, SimpleCookieStorage())
        setup_csrf(app)
        app.router.add_get('/', index)
        for method in CSRF_METHODS:
            app.router.add_route(method, '/', index)
        return app

    @unittest_run_loop
    async def test_generate_token(self):
        resp = await self.client.request('GET', '/')
        assert resp.status == 200
        token = await resp.text()
        assert len(token) > 0

    @unittest_run_loop
    async def test_request_body_token(self):
        resp = await self.client.request('GET', '/')
        token = await resp.text()

        # test methods
        for method in CSRF_METHODS:

            data = {CSRF_FIELD_NAME: token}
            resp = await self.client.request(method, '/', data=data)
            assert resp.status == 200

            data = {CSRF_FIELD_NAME: 'invalid_token'}
            resp = await self.client.request(method, '/', data=data)
            assert resp.status == 400

    @unittest_run_loop
    async def test_request_header_token(self):
        resp = await self.client.request('GET', '/')
        token = await resp.text()

        for method in CSRF_METHODS:
            for header in CSRF_HEADERS:
                headers = {header: token}
                resp = await self.client.request(method, '/', headers=headers)
                assert resp.status == 200
                headers = {header: 'Invalid token'}
                resp = await self.client.request(method, '/', headers=headers)
                assert resp.status == 400


if __name__ == '__main__':
    unittest.main()
