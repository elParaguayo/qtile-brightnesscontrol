from setuptools import setup

setup(
    name='qtile-brightnesscontrol',
    packages=['brightnesscontrol'],
    version='0.1.0',
    description='A module to control and display screen brightness',
    author='elParaguayo',
    url='https://github.com/elparaguayo/qtile-brightnesscontrol',
    license='MIT',
    install_requires=['qtile>0.14.2', 'pydbus']
)
