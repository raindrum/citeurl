import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='citeurl',
    version='4.0.5',
    description='an extensible tool to process legal citations in text',
    author='Simon Raindrum Sherred',
    author_email='simonraindrum@gmail.com',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raindrum/citeurl",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['citeurl=citeurl.__main__:main'],
        'markdown.extensions': ['citeurl=citeurl.mdx:CiteURLExtension'],
    },
    include_package_data=True,
    install_requires=['pyyaml', 'markdown'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Legal Industry',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: Markdown',
    ],
)
