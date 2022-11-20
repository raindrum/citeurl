import setuptools

with open('README.md', 'r') as f:
    readme = f.read()

setuptools.setup(
    name = 'citeurl',
    version = '11.0.6',
    description = 'an extensible tool to process legal citations in text',
    author = 'Simon Raindrum Sherred',
    author_email = 'simonraindrum@gmail.com',
    license = 'MIT',
    long_description = readme,
    long_description_content_type = "text/markdown",
    url="https://raindrum.github.io/citeurl",
    packages = setuptools.find_packages(),
    entry_points = {
        'console_scripts': ['citeurl=citeurl.cli:main'],
        'markdown.extensions': ['citeurl=citeurl.mdx:CiteURLExtension'],
    },
    include_package_data = True,
    install_requires = ['pyyaml'],
    extras_require = {
        'web': ['flask'],
        'config': ['appdirs'],
        'full': ['flask', 'appdirs'],
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Legal Industry',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
