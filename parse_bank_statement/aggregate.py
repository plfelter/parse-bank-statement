from pathlib import Path
import logging
import pandas as pd

from parse_bank_statement.read import get_emission_date


def get_data_availability(inputs: list[Path]):
    dates = pd.Series(sorted([d for d in map(get_emission_date, inputs) if d]))
    logging.info(f"Following statements found:\n{dates.groupby(dates.dt.year).count()}")


# TODO: aggregate all statements transactions and export to Kresus
