import numpy as np


def normalize(band):
    band_min, band_max = (band.min(), band.max())
    return ((band-band_min)/((band_max - band_min)))

def brighten(band):
    alpha=0.1
    return np.clip(alpha*band, 0, 255)
