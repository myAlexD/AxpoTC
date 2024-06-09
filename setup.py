from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="aemet_client",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python client for retrieving historical weather data from AEMET for wind farm feasibility studies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/myAlexD/AxpoTC",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests",
        "pandas",
        "pytz",
    ],
)
