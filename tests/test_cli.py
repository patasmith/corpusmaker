from corpusmaker.cli import Cli
from sqlmodel import Session


def test_add_textfiles_to_database(cli: Cli) -> None:
    filename = "tests/files/test_file_2.txt"
    separator = "* * * * *"
    cli.import_files([filename], separator)
    with open(filename) as f:
        content = f.read()
    with Session(cli.db.engine) as session:
        raw_text = cli.db.read_raw_text(session, 1)
        assert raw_text.content == content
        assert raw_text.separator == separator
        