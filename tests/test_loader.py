from corpusmaker.loader import Loader


# Can add single textfile to table
def test_add_single_textfile_to_table(loader: Loader) -> None:
    loader.read_file("tests/test_file_1.txt")
    pass


# Multiple textfiles can be added at once
# Each textfile will be a separate entry
def test_add_multiple_texts_to_table() -> None:
    pass


# Separator can be specified for textfile(s) when added
def test_associate_separator_with_text() -> None:
    pass
