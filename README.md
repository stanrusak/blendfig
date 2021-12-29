# blendfig

![](https://github.com/stanrusak/stanrusak.github.io/blob/main/files/projects/blendfig/banner.png?raw=true)

## Overview

blendfig is a Python module to be used with the 3D modeling software Blender. With blendfig you can create surface plots in Blender similarly to the usual Python plotting libraries such as plotly and matplotlib. You can then use Blender's powerful shading, modeling etc. features to create beautiful plots and animations.

## Installation

Blender comes with its own Python installation so the easiest way is to add `blendfig.py`  to its scripts directory. On Windows this is `C:\Program Files\Blender Foundation\Blender <version>\<version>\scripts\modules`.

## Usage

Syntax is similar to that of plotly. 

```python
import blendfig as bf
import numpy as np

x, y = np.mgrid[-1:1:51j, -1:1:51j]
z =(x**2+y**2-1)**2

fig = bf.Figure()
fig.add_trace(bf.Surface(x=x, y=y, z=z))
fig.create()

```

![Example](https://github.com/stanrusak/stanrusak.github.io/blob/main/files/projects/blendfig/example.png?raw=true)