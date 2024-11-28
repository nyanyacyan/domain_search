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
        try:
            self.logger.info(f"***** {self.account_id} process 開始 *****")

            # スプシから情報を取得
            brand_name = self.gss_read._sort_brand_name()
            site_url = self.gss_read._sort_site_url()

            self.logger.debug(f"brand_name: {brand_name}, site_url: {site_url} ")

            time.sleep(2)

            # サイトを開く
            self.auto_login.open_site(site_url)
            self.logger.debug(f"brand_name: {brand_name}, site_url: {site_url} ")


            self.logger.info(f"***** {self.account_id} process 終了 *****")


        except Exception as e:
            self.logger.error(f"{self.account_id} process: 処理中にエラーが発生{e}")


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
        return self.gss_read.load_spreadsheet()


# ----------------------------------------------------------------------------------


    def df_to_xpath_list(self, row: str, xpath_keys: List):
        return [row[key] for key in xpath_keys]


# ----------------------------------------------------------------------------------




# ----------------------------------------------------------------------------------

