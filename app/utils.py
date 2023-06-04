import numpy as np


def normalize(band):
    """Normalize min/max values on a given band."""
    band_min, band_max = (band.min(), band.max())
    return ((band-band_min)/((band_max - band_min)))

def brighten(band):
    """Increase brightness on a given band, hardcoded values."""
    alpha=0.1
    return np.clip(alpha*band, 0, 255)
