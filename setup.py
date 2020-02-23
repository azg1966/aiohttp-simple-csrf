import setuptools


setuptools.setup(
    name='aiohttp-simple-csrf',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=['cryptography',
                      'aiohttp',
                      'aiohttp_session'],
    description="Simple CSRF protection for aiohttp",
    test_suite="tests.test"
)
