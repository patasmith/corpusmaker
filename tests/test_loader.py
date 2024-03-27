from corpusmaker.loader import Loader
from corpusmaker.model import RawText


def test_add_single_textfile_to_table(loader: Loader) -> None:
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


def test_add_multiple_texts_to_table(loader: Loader) -> None:
    raw_texts = loader.read_files(
        [
            "tests/files/test_file_1.txt",
            "tests/files/test_file_1.txt",
            "tests/files/test_file_1.txt",
        ]
    )
    assert raw_texts is not None
    assert len(raw_texts) == 3
    for raw_text in raw_texts:
        assert type(raw_text) is RawText
