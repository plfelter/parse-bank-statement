from pathlib import Path

from parse_bank_statement import read


lbp_files = sorted(
    list(
        (
            Path(__file__).resolve().parent.parent
            / "data"
            / "statements"
            / "LaBanquePostale_clean"
        ).glob("Relevé de compte*.pdf")
    )
)


def test_get_emission_date():
    print(list(map(read.get_emission_date, lbp_files)))


def test_get_transaction_tables():
    print(list(map(read.get_transaction_tables, lbp_files)))


def test_get_transactions_headers():
    print(list(map(read.get_transactions_headers, lbp_files)))


def test_statement():
    for f in lbp_files:
        s = read.Statement(pdf=f)
        assert "Ancien solde" in s.table_content
        assert "Nouveau solde" in s.table_content


if __name__ == "__main__":
    # test_get_emission_date()
    # test_get_transaction_tables()
    # test_get_transactions_headers()
    test_statement()
