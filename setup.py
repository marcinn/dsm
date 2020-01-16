import os
from setuptools import setup, find_packages


with open(
    os.path.join(os.path.dirname(__file__), 'README.md'),
    encoding='utf-8'
) as fh:
    long_description = fh.read()


setup(name='dsm',
      version='0.5.2',
      description='Damn simple finite state machine ',
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        ],
      author='Marcin Nowak',
      author_email='marcin.j.nowak@gmail.com',
      url='https://github.com/marcinn/dsm',
      install_requires=['observable', 'six'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages('.'),
      keywords='fsm state machine',
      zip_safe=True,
      )
