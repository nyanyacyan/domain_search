#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
from enum import Enum


# ----------------------------------------------------------------------------------


class XserverXpath(Enum):
    SEARCH_INPUT="//div[@class='search-domain__flex']//input[@type='text']"
    SEARCH_BAR="//div[@class='search-domain__send']//input[@type='submit']"
    SEARCH_RESULT=""


# ----------------------------------------------------------------------------------


class ConohaWingXpath(Enum):
    SEARCH_INPUT="//div[@class='boxDomainForm_input']//input[@type='text']"
    SEARCH_BAR="//div[@class='boxDomainForm_submit']//button[@type='submit']"
    SEARCH_RESULT=""


# ----------------------------------------------------------------------------------


class OnamaeXpath(Enum):
    SEARCH_INPUT="//div[@class='searchWithoutPulldown']//input[@type='text']"
    SEARCH_BAR="//div[@class='searchWithoutPulldown']//button[@type='submit']"
    SEARCH_RESULT=""


# ----------------------------------------------------------------------------------