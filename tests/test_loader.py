from sqlmodel import Session
from corpusmaker.loader import Loader
from corpusmaker.model import RawText


def test_read_single_textfile(loader: Loader) -> None:
    raw_text = loader.read_file("tests/files/test_file_1.txt")
    assert raw_text is not None
    with open("tests/files/test_file_1.txt") as f:
        assert raw_text.content == f.read()
    raw_text = loader.read_file("tests/files/test_file_2.txt", "* * * * *")
    assert raw_text is not None
    with open("tests/files/test_file_2.txt") as f:
        assert raw_text.content == f.read()
        assert raw_text.separator == "* * * * *"
    raw_text = loader.read_file("tests/files/test_file_3.txt", "^\n*.*[^.!?]\n^\n")
    assert raw_text is not None
    with open("tests/files/test_file_3.txt") as f:
        assert raw_text.content == f.read()
        assert raw_text.separator == "^\n*.*[^.!?]\n^\n"


def test_import_single_textfile(loader: Loader, session: Session) -> None:
    loader.import_file("tests/files/test_file_1.txt")
    raw_text = loader.db.read_raw_text(session=session, text_id=1)
    with open("tests/files/test_file_1.txt") as f:
        assert raw_text.content == f.read()


def test_import_multiple_textfiles(loader: Loader, session: Session) -> None:
    textfiles = [
        "tests/files/test_file_1.txt",
        "tests/files/test_file_2.txt",
        "tests/files/test_file_3.txt",
    ]
    separator = "test separator"
    loader.import_files(textfiles, separator)
    raw_texts = [
        loader.db.read_raw_text(session=session, text_id=n) for n in range(1, 4)
    ]
    assert raw_texts is not None
    assert len(raw_texts) == 3
    for raw_text, textfile in zip(raw_texts, textfiles):
        assert type(raw_text) is RawText
        assert raw_text.separator == separator
        with open(textfile) as f:
            assert raw_text.content == f.read()
