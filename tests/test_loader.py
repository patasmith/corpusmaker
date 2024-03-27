from corpusmaker.loader import Loader


# Can add single textfile to table
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


# Multiple textfiles can be added at once
# Each textfile will be a separate entry
def test_add_multiple_texts_to_table() -> None:
    pass


# Separator can be specified for textfile(s) when added
def test_associate_separator_with_text() -> None:
    pass
