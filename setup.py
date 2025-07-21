from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bugmark",
    version="0.1.5",
    author="Aarav Maloo",
    author_email="aaravmaloo06@email.com",
    description="A command-line bug marker utility for programmers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaravmaloo/bugmark",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "bugmark=bugmark.bugmark:main",
        ],
    },
)
