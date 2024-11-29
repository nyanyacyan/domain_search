# coding: utf-8
# ----------------------------------------------------------------------------------
#! ここで定義して「Flow」で扱う
#! 引数はここで基本渡す。


# ----------------------------------------------------------------------------------
import time
import pandas as pd
from typing import Any, Dict, List

# 自作モジュール
from .spreadsheetRead import SpreadsheetRead
from .utils import Logger
from .seleniumBase import SeleniumBasicOperations
from ..const_domain_search import GssColumnsName


####################################################################################
# **********************************************************************************


class GssLogin:
    def __init__(self, sheet_url, chrome, debugMode=True) -> None:
        self.chrome = chrome

        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.sheet_url = sheet_url
        self.chrome = chrome

        # インスタンス化
        self.gss_read = SpreadsheetRead(sheet_url=self.sheet_url, account_id=self.account_id, chrome=self.chrome, debugMode=debugMode)
        self.selenium = SeleniumBasicOperations(chrome=self.chrome, debugMode=debugMode)


# ----------------------------------------------------------------------------------


    def flowProcess(self):
        pass


# ----------------------------------------------------------------------------------
# サイトを開く（jsWaitあり）

    def open_site(self, url: str):
        return self.selenium.openSite(url=url)


# ----------------------------------------------------------------------------------
# DataFrameを辞書に変換

    def _get_dict_to_df(self):
        df = self._get_df_to_gss()
        data_dict = df.to_dict(orient='list')
        self.logger.info(f"url_dict: {data_dict}")
        return data_dict


# ----------------------------------------------------------------------------------
# スプシのDataFrameを取得

    def _get_df_to_gss(self):
        df = self.gss_read.load_spreadsheet()
        return df


# ----------------------------------------------------------------------------------
# dfを辞書に直したリストデータにあるColumnからを特定行から値を抜き出す
# Noneだった場合には除外

    def _get_row_value_list(self, row: str, key_list: List):
        value_list = [row[key] for key in key_list is not None]
        return value_list

# ----------------------------------------------------------------------------------
