from __future__ import annotations

import matplotlib.pyplot as plt
from pyg4ometry import geant4
from matplotlib.figure import Figure, Axes


def plot_profiles(profiles: dict,title:str = "", show: bool = False) -> tuple[Figure,Axes]:
    """Plot the profiles of the volumes in the geometry using matplotlib.
    
    Parameters
    ----------
    profiles
        A dictionary mapping volume names to their profiles, where each profile is a 
        dictonary with 3 fields `r`, `z` and `offset`.
        The `r` and `z` fields are lists of the same length, containing the radius and z
        coordinates of the profile, respectively. The `offset` field is a single number
        representing the offset of the profile from the center of the geometry.

    """
    fig, ax = plt.subplots(figsize=(6, 8))
    plt.rcParams["font.size"] = 14
    
    for name, profile in profiles.items():
        ax.plot(profile["r"], [-(zt+profile["offset"]) for zt in profile["z"]], label=name)

    ax.set_ylabel("height (mm)")
    ax.set_xlabel("radius (mm)")
    ax.set_title(title)
    ax.legend(fontsize=12)
    
    return fig, ax