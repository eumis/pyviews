from setuptools import setup, find_packages

setup(
    name='pyviews',
    version='0.5.0',
    description='tkinter MVVM tool',
    long_description='MVVM tool that allows to describe tkinter widgets with xml',
    author='me',
    license='MIT',
    classifiers=[
        #   2 - Pre-Alpha
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='mvvm tkinter pyviews',
    packages=find_packages(exclude=['sandbox']))
