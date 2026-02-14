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

This metadata is stored on github
[[hades-metadata]](https://github.com/legend-exp/hades-metadata).

:::{note}

The different measurements are described on
[[confluence]](https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/1826750480/Analysis+of+characterization+data+WIP)
(note this is a private page).

:::
