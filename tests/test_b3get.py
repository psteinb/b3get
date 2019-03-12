
from b3get.cli import main


def test_main_help():
    assert main(["b3get", "help"]) == 1


def test_main_list():
    assert main(["b3get", "list"]) == 0

#def # test_main_list_help():
    # assert main(["b3get", "list", "--help"]) == 1


def test_main_pull_dryrun():
    assert main(["b3get", "pull", "-n", "8"]) == 0


def test_main_show():
    assert main(["b3get", "show", "8"]) == 0


def test_main_show_24():
    assert main(["b3get", "show", "24"]) == 0


def test_main_show_many():
    assert main(["b3get", "show", "24", "8"]) == 0
