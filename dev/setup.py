from setuptools import setup

APP = ['GCS.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 
    'iconfile': 'mwp_icon.icns' }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
