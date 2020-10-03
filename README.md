<h1 align="center">
  <br>
  <a href="https://atlas.cern/"><img src="img/logo.png" alt="ATLAS Plots" width="200"></a>
  <br>
  ATLAS Plots
  <br>
</h1>

![License](https://img.shields.io/github/license/joeycarter/atlas-plots)

**ATLAS Plots** provides a simple interface to produce plots in ROOT following the standard ATLAS style guidelines. It uses [matplotlib](https://matplotlib.org/)-like syntax and idioms while still giving access to the underlying ROOT objects.

**Behold, the simplicity of ATLAS Plots:**

```python
>>> import atlasplots as aplt
>>> aplt.set_atlas_style()
Applying ATLAS style settings
>>> fig, ax = aplt.subplots(1, 1)
>>> ax.set_xlabel("X [GeV]")
>>> ax.set_ylabel("Events")
>>> ax.set_xlim(0, 100)
>>> ax.set_ylim(0, 10)
>>> fig.savefig("figure.png")
Info in <TCanvas::Print>: file figure.png has been created
```

<p align="center">
  <img src="img/figure.png" alt="Figure"/>
</p>

Compare with the equivalent PyROOT code:

```python
>>> import ROOT
>>> import atlasplots as aplt
>>> aplt.set_atlas_style()
Applying ATLAS style settings
>>> canv = ROOT.TCanvas("canv", "", 800, 600)
>>> frame = ROOT.TH1F("frame", "", 1, 0, 1)
>>> frame.GetXaxis().SetTitle("X [GeV]")
>>> frame.GetYaxis().SetTitle("Events")
>>> frame.GetXaxis().SetLimits(0, 100)
>>> frame.GetYaxis().SetLimits(0, 10)
>>> frame.Draw("AXIS")
>>> canvas.SaveAs("figure.png")
Info in <TCanvas::Print>: file figure.png has been created
```

## Installing

**ATLAS Plots** isn't in PyPI (yet) so for now it's best to clone the source and install as editable:

```bash
$ cd atlas-plots
$ pip install [--user] -e .
```