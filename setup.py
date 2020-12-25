import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='citeurl',
    version='1.0.0',
    description='an extensible tool to make legal citations into hyperlinks',
    author='Simon Raindrum Sherred',
    author_email='simonraindrum@gmail.com',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://raindrum.github.io",
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
        'Environment :: Console',
        'Environment :: Other Environment',
        'Operating System :: OS Independent',
    ],
)
