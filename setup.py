from setuptools import setup
import platform

requires = ["flask", "pathlib"]

if platform.python_implementation() != "Jython":
    requires += ['sarge', 'lxml']

setup(
    name='xcat_app',
    version='0.0.1',
    packages=['xcat_app'],
    url='',
    license='',
    author='tomforbes',
    author_email='',
    description='',
    install_requires=["flask", "requests"],
    entry_points={
        'console_scripts': [
            'xcat_app = xcat_app.run:run'
        ]
    },
)
