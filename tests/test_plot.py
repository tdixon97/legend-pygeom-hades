from __future__ import annotations

from matplotlib.figure import Figure, Axes

from pygeomhades import plot

def test_plot():
    
    fig, ax = plot.plot_profiles(
        {
            "vol1": {"z": [0, 1, 2], "r": [0, 1, 0],"offset": 0},
            "vol2": {"z": [0, 1, 2], "r": [0, 0.5, 0],"offset": 0.5},
        },
        title="test plot",
        show=False,
    )

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)
