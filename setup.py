import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-management",
    version="0.0.1",
    author="Sam Toolan",
    author_email="stoolan@telegeography.com",
    description="Wrappers for managing AWS resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stoolan/plotly2js.git",
    packages=["aws_management"],
    install_requires=["boto3", "dotmap", "jsonschema"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
