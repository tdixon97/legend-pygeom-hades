# Description of the geometry

The geometry of the HADES test stand consists of the HPGe detector in a vacuum
cryostat, with various possible sources and an outer lead shield (in some
measurements).

During detector characterisation a very large number of measurements are
performed. This package allows to easily generate the geometry for any
measurement and run (see {doc}`configuration`).

A more detailed description can be found in
[[link]](https://www.research.unipd.it/retrieve/aaa7ce91-013d-4975-8827-c0eff2fb37af/Thesis_Valentina_Biancacci.pdf).

## Physical volumes

- The HPGe detector physical volume is the name of the detector,
- The active component of the source is named "Source".

::: {tip}

In _remage_ the physical volume "Source" should usually be set as the volume for
vertex confinement to simulate the calibration source.

Other volume names can be found by inspecting the GDML file, but are not
expected to be needed for simulations.

:::
