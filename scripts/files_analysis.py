from pathlib import Path
from parse_bank_statement import read
import pandas as pd


def main():
    lbp_files = sorted(
        list(
            (Path.cwd().parent / "data" / "statements" / "LaBanquePostale_clean").glob(
                "*.pdf"
            )
        )
    )

    def get_statement(pdf):
        # try:
        return read.Statement(pdf=pdf)
        # except Exception:
        #     return None

    statements = [s for s in map(get_statement, lbp_files) if s]
    print(
        pd.DataFrame(
            {
                "headers": [len(s.headers) for s in statements],
                "filename": [s.pdf.stem for s in statements],
            },
            index=[s.emission_date for s in statements],
        )
        .sort_index()
        .groupby(["headers"])
        .count()
    )


if __name__ == "__main__":
    main()
