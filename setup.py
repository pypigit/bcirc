import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bcirc",
    version="0.0.2",
    author="Tamas Hubai",
    author_email="python@htamas.net",
    description="Boolean circuits package for my students",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypigit/bcirc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

