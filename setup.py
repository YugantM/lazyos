from setuptools import setup, find_packages

setup(
    name="lazyos",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0",
    ],
    python_requires=">=3.7",
) 