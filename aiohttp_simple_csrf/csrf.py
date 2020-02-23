from cryptography.fernet import Fernet, InvalidToken
from aiohttp_session import get_session
from aiohttp import web
from secrets import token_urlsafe, compare_digest


# CSRF_SECRET = b'NIVu7AyqeWB0cXbY5q_RWp-kblc_2fYgM_eOgPzl8Jk='
CSRF_SECRET = Fernet.generate_key()
CSRF_SECRET_KEY = 'csrf_secret'
CSRF_FIELD_NAME = 'csrf_token'
CSRF_TIME_LIMIT = 3600
CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']


def setup(app,
          secret=CSRF_SECRET):

    app[CSRF_SECRET_KEY] = secret
    return app


async def generate_csrf_token(request):

    fernet = Fernet(request.config_dict[CSRF_SECRET_KEY])

    if CSRF_FIELD_NAME not in request:
        session = await get_session(request)
        if CSRF_FIELD_NAME not in session:
            session[CSRF_FIELD_NAME] = token_urlsafe()
        try:
            csrf_token = fernet.encrypt(
                session[CSRF_FIELD_NAME].encode('utf-8'))
        except TypeError:
            session[CSRF_FIELD_NAME] = token_urlsafe()
            csrf_token = fernet.encrypt(
                session[CSRF_FIELD_NAME].encode('utf-8'))
        request[CSRF_FIELD_NAME] = csrf_token.decode('utf-8')
    return request[CSRF_FIELD_NAME]


async def get_csrf_token(request):
    form = await request.post()

    # search CSRF token field in form
    csrf_token = form.get(CSRF_FIELD_NAME)
    if csrf_token:
        return csrf_token

    # search CSRF token field in form with prefix
    for fieldname in form.keys():
        if fieldname.endswith(CSRF_FIELD_NAME):
            csrf_token = form[fieldname]

            if csrf_token:
                return csrf_token

    # search CSRF token in headers
    for header in CSRF_HEADERS:
        csrf_token = request.headers.get(header)
        if csrf_token:
            return csrf_token

    return None


async def validate_csrf_token(request, csrf_token=None):
    if csrf_token is None:
        csrf_token = await get_csrf_token(request)

    # There is no CSRF token in form or in HTTP Headers
    if not csrf_token:
        raise web.HTTPBadRequest(reason='The CSRF token is missing')

    if isinstance(csrf_token, str):
        csrf_token = csrf_token.encode('utf-8')

    session = await get_session(request)
    session_csrf_token = session.get(CSRF_FIELD_NAME)

    # Missing or empty session csrf token
    if session_csrf_token is None:
        raise web.HTTPBadRequest(reason='The CSRF session token is missing')

    if isinstance(session_csrf_token, str):
        session_csrf_token = session_csrf_token.encode('utf-8')

    fernet = Fernet(request.config_dict[CSRF_SECRET_KEY])
    try:
        plain_csrf_token = fernet.decrypt(
            csrf_token,
            ttl=CSRF_TIME_LIMIT)
        if compare_digest(plain_csrf_token, session_csrf_token):
            return True
        else:
            # CSRF token in request not equal plain token saved in session
            raise web.HTTPBadRequest(reason='Invalid CSRF token')
    except InvalidToken:
        # Bad token data or token ttl expired
        raise web.HTTPBadRequest(reason='Invalid CSRF token')
