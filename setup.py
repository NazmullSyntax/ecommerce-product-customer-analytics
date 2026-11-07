"""
Setup configuration for local package installation in editable mode.
"""

from setuptools import find_packages, setup

setup(
    name="ecommerce_analytics",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)