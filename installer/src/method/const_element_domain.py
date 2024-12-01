#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
from enum import Enum


# ----------------------------------------------------------------------------------


class XserverXpath(Enum):
    SITE_NAME='Xserver'
    SEARCH_INPUT="//div[@class='search-domain__flex']//input[@type='text']"
    SEARCH_BAR="//div[@class='search-domain__send']//input[@type='submit']"
    PARENT_ELEMENT=""
    CHILD_ELEMENT=""


# ----------------------------------------------------------------------------------


class ConohaWingXpath(Enum):
    SITE_NAME='Conoha Wing'
    SEARCH_INPUT="//div[@class='boxDomainForm_input']//input[@type='text']"
    SEARCH_BAR="//div[@class='boxDomainForm_submit']//button[@type='submit']"
    PARENT_ELEMENT=""
    CHILD_ELEMENT=""


# ----------------------------------------------------------------------------------


class OnamaeXpath(Enum):
    SITE_NAME='お名前.com'
    SEARCH_INPUT="//div[@class='searchWithoutPulldown']//input[@type='text']"
    SEARCH_BAR="//div[@class='searchWithoutPulldown']//button[@type='submit']"
    PARENT_ELEMENT="//td[@class='result-ribon-checkbox' and @data-tld='{extension}']']"
    CHILD_ELEMENT=".//button/span[@class='search-result-item__name__icon']"



# ----------------------------------------------------------------------------------


class BoolTextList(Enum):
    TRUE_TEXT_LIST=[
        '通常',
        '可能性あり',
    ]

    FALSE_TEXT_LIST=[
        'メール通知',
        '登録不可',
    ]


# ----------------------------------------------------------------------------------
