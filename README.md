<h1 align="center">
  <br>
  <a href="https://atlas.cern/"><img src="https://raw.githubusercontent.com/joeycarter/atlas-plots/master/img/logo.png" alt="ATLAS Plots" width="200"></a>
  <br>
  ATLAS Plots
  <br>
</h1>

![License](https://img.shields.io/github/license/joeycarter/atlas-plots)
[![Documentation Status](https://readthedocs.org/projects/atlas-plots/badge/?version=latest)](https://atlas-plots.readthedocs.io/en/latest/?badge=latest)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/atlasplots)

**ATLAS Plots** provides a simple interface to produce plots in [ROOT](https://root.cern/) following the standard [ATLAS](https://atlas.cern/) style guidelines. It uses [matplotlib](https://matplotlib.org/)-like syntax and idioms while still giving access to the underlying ROOT objects.

**Behold, the simplicity of ATLAS Plots:**

```python
import atlasplots as aplt

aplt.set_atlas_style()

fig, ax = aplt.subplots(1, 1)
ax.set_xlabel("X [GeV]")
ax.set_ylabel("Events")
ax.set_xlim(0, 100)
ax.set_ylim(0, 10)

fig.savefig("figure.png")
```

<p align="center">
  <img src="https://raw.githubusercontent.com/joeycarter/atlas-plots/master/img/figure.png" alt="Figure"/>
</p>

Compare with the equivalent PyROOT code:

```python
import ROOT
import atlasplots as aplt

aplt.set_atlas_style()

canv = ROOT.TCanvas("canv", "", 800, 600)
frame = ROOT.TH1F("frame", "", 1, 0, 1)
frame.GetXaxis().SetTitle("X [GeV]")
frame.GetYaxis().SetTitle("Events")
frame.GetXaxis().SetLimits(0, 100)
frame.GetYaxis().SetLimits(0, 10)
frame.Draw("AXIS")

canv.SaveAs("figure.png")
```

## Installing

```console
$ pip install atlasplots
```

You can also install in editable mode if you need a quick-and-dirty way to make changes to the source code:

```console
$ git clone <project-url>
$ cd atlas-plots
$ pip install [--user] -e .
```

## Examples

*For those who learn by example*

Several examples of more complex plots, such as histogram fits, ratio and fit-residual panels, Data/MC plots, etc., are available under the `examples/` directory.

## Documentation

The **ATLAS Plots** documentation is available at https://atlas-plots.readthedocs.io.