from pathlib import Path

from parse_bank_statement.read import get_emission_date


def test_get_emission_date():
    lbp_files = sorted(
        list(
            (Path.cwd().parent / "data" / "statements" / "LaBanquePostale").glob(
                "Relevé de compte*.pdf"
            )
        )
    )
    print(list(map(get_emission_date, lbp_files)))


if __name__ == "__main__":
    test_get_emission_date()
