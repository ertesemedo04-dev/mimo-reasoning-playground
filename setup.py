"""MiMo Reasoning Playground — setup."""

from setuptools import setup, find_packages

setup(
    name="mimo-reasoning-playground",
    version="1.0.0",
    description="Interactive reasoning exploration with Xiaomi MiMo v2.5 Pro",
    author="gameover1212001",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27",
        "gradio>=4.0",
        "python-dotenv>=1.0",
    ],
    entry_points={
        "console_scripts": [
            "mimo-playground=mimo_playground.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
