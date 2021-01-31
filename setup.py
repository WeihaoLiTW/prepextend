# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:25:34 2021

@author: weiha
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prepextension", # 
    version="2020.2.1",
    author="Weihao Li",
    author_email="weihao.li.tw@gmail.com",
    description="to expand the functionality of Tableau prep",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)