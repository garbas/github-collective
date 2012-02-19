from setuptools import setup

version = '0.1.4'

setup(
    name='github-collective',
    version=version,
    description="Script to manage github account in a collective manner",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        #"Programming Language :: Python :: 2.7",
        #"Programming Language :: Python :: 3.2",
        ],
    keywords='github git permission collaboration collective',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/garbas/github-collective',
    license='BSD',
    packages=['githubcollective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'argparse',
        'requests',
        ],
    entry_points="""
        [console_scripts]
        github-collective = githubcollective:run
        """,
    )
