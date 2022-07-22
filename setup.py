#
#     blendfig - Python plots for Blender
#     Copyright (C) 2022 Stanislav Rusak
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import pathlib
from setuptools import setup, find_packages, find_namespace_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="blendfig",
    version="0.1.0",
    description="Python plotting library for Blender",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/stanrusak/blendfig",
    author="Stanislav Rusak",
    author_email="stanislav.rusak@gmail.com",
    license="GPLv3+",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
    ],
    packages= find_namespace_packages(),
    include_package_data=True,
)
