# Configuration

It is necessary to provide a configuration YAML file.

This should have a format similar to:

```yaml
hpge_name: V13049A # the detector name
daq_settings: # details about the data taking
  flashcam:
    card_interface: efb2
run: run0001 # the run number
measurement: th_HS2_top_psa # the measurement name
source_position: # the source position
  phi_in_deg: 0.0
  r_in_mm: 0.0
  z_in_mm: 38.0
```

:::{note}

The different measurements are described on
[[confluence]](https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/1826750480/Analysis+of+characterization+data+WIP)
(note this is a private page).

:::

This metadata is stored on github
[[hades-metadata]](https://github.com/legend-exp/hades-metadata).

This metadata can then be passed directly to `pygeomhades` either on the command
line, on in python.

For example:

```python
db = dbetto.TextDB("hades-metadata")  # load the metadata

# construct the geometry
reg = pygeomhades.core.construct(
    db.hardware.configuration.V07302A.c1.am_HS1_top_dlt.run0001
)

# visualise
pygeomtools.viewer.visualize(reg)
```
