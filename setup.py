import setuptools

SHORT_DISCRIPTION = 'This is a library that bridges '\
    'server-side python and browser-side javascript.'
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='pynexumjs',
    version='0.0.0',
    description=SHORT_DISCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Malek Ali',
    author_email='malek.ali@yellow-sic.com',
    license='MIT',
    url='https://github.com/YellowSiC/PyNexumJS/',
    install_requires=[],
    extras_require={
        "full": [
            "graphene",
            "requests",
            "ujson",
            "websockets",
            "whichcraft",
            'aiofile'
            'annotated-types'
            'anyio'
            'bidict'
            'caio'
            'certifi'
            'click'
            'colorama'
            'fastapi'
            'h11'
            'httpcore'
            'httpx'
            'idna'
            'itsdangerous'
            'Jinja2'
            'MarkupSafe'
            'pydantic'
            'pydantic_core'
            'python-engineio'
            'python-multipart'
            'python-socketio'
            'PyYAML'
            'setuptools'
            'simple-websocket'
            'sniffio'
            'starlette'
            'typing_extensions'
            'uvicorn'
            'websockets'
            'whichcraft'
            'wsproto'
        ]
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP"
    ],
    python_requires='>=3.7'
)
