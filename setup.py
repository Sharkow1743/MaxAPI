from setuptools import setup, find_packages

version = ""

setup(
    name='MaxBridge',
    version=version,
    author='Sharkow1743',
    author_email='sharkow1743@gmail.com',
    description='An API wrapper for Max.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Sharkow1743/MaxAPI',
    download_url=f'https://github.com/Sharkow1743/MaxAPI/archive/v{version}.zip',
    packages=find_packages(),
    install_requires=[
        'tornado>=6.0.4',
        'requests>=2.31.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
