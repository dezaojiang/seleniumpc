#-*- coding: utf-8 -*-
#!/usr/bin/env python

import distutils.core

distutils.core.setup(
    name = 'seleniumpc',
    version = '0.0.1',
    packages = ['seleniumpc'],
    install_requires = ['selenium', 'PyAutoIt', 'PIL'],
    author = 'dezaojiang',
    url = 'https://github.com/dezaojiang/seleniumpc'
    )