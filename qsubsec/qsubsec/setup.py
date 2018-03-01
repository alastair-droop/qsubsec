from setuptools import setup

setup(
    name = 'qsubsec',
    version = '3.0a1',
    description = 'A simple Python-based preprocessor system for SGE job templates',
    author = 'Alastair Droop',
    author_email = 'alastair.droop@gmail.com',
    url = 'https://github.com/alastair.droop/qsubsec',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Pre-processors',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3'
    ],
    py_modules = ['tokens', 'sections', 'templates', 'sectionFormatter', 'qsubsec', 'parseTFF'],
    install_requires = [
        'pyparsing>=2.2.0'
    ],
    python_requires = '>=3',
    entry_points = {
        'console_scripts': [
            'qsubsec=qsubsec:main',
            'parse-tff=parseTFF:main'
        ]
    }
)

