from setuptools import setup, find_packages

setup(name='dsm',
      version='0.2',
      description='Damn simple finite state machine ',
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        ],
      author='Marcin Nowak',
      author_email='marcin.j.nowak@gmail.com',
      url='https://github.com/marcinn/dsm',
      install_requires = ['observable'],
      py_modules=['dsm'],
      keywords='fsm state machine',
      zip_safe=True,
      )
