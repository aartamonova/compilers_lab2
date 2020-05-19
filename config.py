import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    grammars_dir = root_dir + '/grammars/'

    EPSILON_SYMBOL = 'ε'
    EPSILON_SIGN = ':eps:'
    HATCH_SYMBOL = "'"


class TestConfig:
    grammars_dir = root_dir + '/tests/grammars/'
