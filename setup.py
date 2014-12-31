import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mashup',
    version='0.7.1',
    packages=['mashup'],
    include_package_data=True,
    license='GNU General Public License v3 (GPLv3)',
    description='Combine multiple views, strings of HTML, and/or ajax loaded urls into a single view.',
    long_description=README,
    install_requires=[
        'django>=1.6',
    ],
    url='http://www.sigmaeducation.com/',
    author='Sigma Education',
    author_email='dev@sigmaeducation.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
