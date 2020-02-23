
# Usage #

This package needs aiohttp-session

``` python
from aiohttp_simple_csrf import generate_csrf_token, validate_csrf_token, setup
...
setup(app, secret=b'32 urlsafe base64-encoded bytes')
```

### Generate token ###

``` python
@aiohttp_jinja2.template('index.jinja2')
async def index(request):
	csrf_token = await generate_csrf_token(request)
	return {'csrf_token': csrf_token}

```

### Validate token ###

``` python
async def handler(request):
	if request.method == 'POST':
		await validate_csrf_token(request)
```

or

with WTForms

``` python

async def handler(request):
	form = SomeForm(await request.post())
	await validate_csrf_token(request,
	                          csrf_token=form.field.data)
```
