from setuptools import setup, find_packages

setup(
    name="bugmark",
    version="0.1.0",  # Increment for future releases
    author="Aarav Maloo",
    description="A CLI tool for resolving and maintaining all bugs in your code.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bugmark=bugmark.__main__:main",  # Update path if needed
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Adjust if needed
)
