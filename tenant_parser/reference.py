"""US city/state/ZIP reference data used to validate extracted addresses.

The dataset is the GeoNames US postal-code export shipped in ``data/US.txt``.
It is ~40k rows, so it is loaded once and cached for the life of the process.
"""

from __future__ import annotations

import functools
from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).parent / "data" / "US.txt"

ZIP_COLUMN = "Zip Code"
CITY_COLUMN = "City"
STATE_NAME_COLUMN = "State Name"
STATE_ABBREVIATION_COLUMN = "State Abbreviation"


@functools.lru_cache(maxsize=1)
def reference_data() -> pd.DataFrame:
    """Normalised ZIP/city/state lookup table.

    Cities and state names are lower-cased and state abbreviations upper-cased
    so callers can compare without re-normalising on every row.
    """
    frame = pd.read_csv(DATA_FILE, header=None, sep="\t", usecols=[1, 2, 3, 4])
    frame.columns = [ZIP_COLUMN, CITY_COLUMN, STATE_NAME_COLUMN, STATE_ABBREVIATION_COLUMN]
    frame[ZIP_COLUMN] = frame[ZIP_COLUMN].astype(str).str.strip()
    frame[CITY_COLUMN] = frame[CITY_COLUMN].str.strip().str.lower()
    frame[STATE_NAME_COLUMN] = frame[STATE_NAME_COLUMN].str.strip().str.lower()
    frame[STATE_ABBREVIATION_COLUMN] = (
        frame[STATE_ABBREVIATION_COLUMN].fillna("").astype(str).str.strip().str.upper()
    )
    return frame
