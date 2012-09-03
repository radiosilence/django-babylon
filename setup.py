from setuptools import setup, find_packages

VERSION = '0.0.2'
APPLICATION = 'django-babylon'

setup(
    name=APPLICATION,
    version=VERSION,
    description='Django infinite caching for mandems.',
    long_description=open('README.rst').read(),
    url='https://github.com/radiosilence/django-babylon',
    author='James Cleveland',
    author_email='jamescleveland@gmail.com',
    py_modules=['babylon'],
    include_package_data=True,
    license="LICENSE.txt",
    install_requires=open('requirements.txt').read().split("\n")
)
