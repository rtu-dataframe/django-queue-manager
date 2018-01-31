import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-queue-manager',
    version='1.0.5',
    packages=find_packages(),
    include_package_data=True,
    license='GNU GPLv3',
    description='A simple app that provides a Message Queue System using a socket as broker, this app, '
                'make you able to manage an ordered queue of tasks (with calling a simple queuing function form API).'
                'Simple to setup, easy to manage and scalable, the queue can be remotized to another server,'
                'you can use multiple istance of the application, and easly manage multiple broker and relatives queues.'
                'This app, will integrate into your DB backend and serves three table with the states of the queue.',
    long_description=README,
    url='http://www.fardellasimone.com/',
    author='Fardella Simone',
    author_email='fardella.simone@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
	    'Programming Language :: Python',
	    'Programming Language :: Python :: 3.4',
	    'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)