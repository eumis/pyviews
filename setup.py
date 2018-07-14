from setuptools import setup, find_packages

def setup_package():
    setup(
        name='pyviews',
        version='1.0.0',
        description='Base package for xml views',
        url='https://github.com/eumis/pyviews',
        author='eumis(Eugen Misievich)',
        author_email='misievich@gmail.com',
        license='MIT',
        classifiers=[
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6'
        ],
        python_requires='>=3.6',
        keywords='binding tkviews tk tkinter pyviews python mvvm',
        packages=find_packages(exclude=['tests', 'tests.*']))

if __name__ == '__main__':
    setup_package()
