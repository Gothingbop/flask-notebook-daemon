import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

with open('requirements.txt', 'r') as file:
    requirements = [line.strip() for line in file]

setuptools.setup(
    name="flask-notebook-daemon",
    version="0.0.1",
    author="Jacob Thompson",
    author_email="Gothingbop@gmail.com",
    description="A simple package for running a flask app in the background of a Jupyter Notebook",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gothingbop/flask-notebook-daemon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires='>=3',
    data_files=[
        ('.', ['requirements'])
    ]
)
