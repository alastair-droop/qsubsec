from setuptools import setup, find_packages
import os.path

# Get the version:
version = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'qsubsec', 'version.py')) as f: exec(f.read(), version)

setup(
    name = 'qsubsec',
    version = version['__version__'],
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
    # py_modules = ['tokens', 'sections', 'templates', 'sectionFormatter', 'sectionSubmitter', 'scripts', 'version'],
    packages = find_packages(),
    install_requires = [
        'pyparsing>=2.2.0'
    ],
    python_requires = '>=3',
    entry_points = {
        'console_scripts': [
            'qsubsec=qsubsec.scripts:qsmain',
            'parse-tff=qsubsec.scripts:parseTFF',
            'update-template=qsubsec.scripts:updateTemplate'
        ]
    }
)
