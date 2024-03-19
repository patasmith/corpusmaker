from corpusmaker import hello


def test_greeting():
    assert hello.greeting() == "hello!"
