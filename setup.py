# pylint: disable=missing-docstring
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="amphipod-game",
    version="0.1.0",
    description="Amphipod game simulator from Advent of Code 2021 day 23",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.github.com/mjip/amphipod-game",
    packages=["amphipod_game"],
    install_requires=[],
    scripts=["scripts/amphipod-game"],
    keywords=[
        "amphipod game",
    ],
)
