# coding: utf-8
# ----------------------------------------------------------------------------------
#! ここで定義して「Flow」で扱う
#! 引数はここで基本渡す。


# ----------------------------------------------------------------------------------
import os, time, asyncio
import pandas as pd
from typing import Any, Dict, List
from dotenv import load_dotenv


# 自作モジュール
from .spreadsheetRead import SpreadsheetRead
from .utils import Logger
from .seleniumBase import SeleniumBasicOperations
from .elementManager import ElementManager
from .notify import ChatworkNotify
from .path import BaseToPath

from ..const_domain_search import GssInfo, Extension, SubDir, SendMessage

load_dotenv()


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
        self.element = ElementManager(chrome=self.chrome, debugMode=debugMode)
        self.chatWork = ChatworkNotify(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)


# ----------------------------------------------------------------------------------


    async def flowProcess(self):
        df = self._get_df_to_gss()

        tasks = []
        for row in df.iterrows():
            tasks.append(self.row_process(row=row))

        await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# 行の処理

    async def row_process(self, row: pd.Series):
        id = self._get_row_ID(row=row)
        name = self._get_row_name(row=row)
        url = self._get_row_url(row=row)
        domain_list = self._get_row_value_list(row=row, key_list=GssInfo.DOMAIN_COL.value)
        xpath_list = self._get_row_value_list(row=row, key_list=GssInfo.XPATH_COL.value)
        self.logger.debug(f"\ndomain_list: {domain_list}\nxpath_list: {xpath_list}")

        search_input_element = xpath_list[0]
        search_bar_element = xpath_list[1]
        search_result = xpath_list[2]


        for domain in domain_list:
            await self.open_site(url=url)
            await self._search_bar_input(by='xpath', value=search_input_element, input_text=domain)
            await self._search_bar_click(by='xpath', value=search_bar_element)
            if await self._search_result_bool(by='xpath', value=search_result):
                photo_name = f"{name}_{domain}"
                message = SendMessage.CHATWORK.value.format(siteName=name, domain=domain)
                await self._exist_notify(photo_name=photo_name, message=message)
            else:
                self.logger.info(f"探しているドメインは {id} {name} サイトにはありませんでした: {domain}")


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


    def _get_row_ID(self, row: pd.Series):
        url_col = GssInfo.ID_COL.value
        return row[url_col]


# ----------------------------------------------------------------------------------

    def _get_row_name(self, row: pd.Series):
        url_col = GssInfo.NAME_COL.value
        return row[url_col]


# ----------------------------------------------------------------------------------

    def _get_row_url(self, row: pd.Series):
        url_col = GssInfo.URL_COL.value
        return row[url_col]


# ----------------------------------------------------------------------------------
# dfを辞書に直したリストデータにあるColumnからを特定行から値を抜き出す
# Noneだった場合には除外

    def _get_row_value_list(self, row: str, key_list: List):
        value_list = [row[key] for key in key_list if row[key] is not None]
        return value_list


# ----------------------------------------------------------------------------------


    def _search_bar_input(self, by: str, value: str, input_text: str):
        return self.element.clickClearInput(by=by, value=value, inputText=input_text)


# ----------------------------------------------------------------------------------


    def _search_bar_click(self, by: str, value: str):
        return self.element.clickElement(by=by, value=value)


# ----------------------------------------------------------------------------------


    def _search_result_bool(self, by: str, value: str, true_element: str):
        result_element = self.element.getElement(by=by, value=value)
        if result_element == true_element:
            return True
        else:
            return False


# ----------------------------------------------------------------------------------


    def _screenshot(self, photo_name: str):
        screenshot_path = self.path.writeFileNamePath(
            fileName=photo_name,
            subDirName=SubDir.SCREEN_SHOT.value,
            extension=Extension.PNG.value
        )
        self.chrome.save_screenshot(screenshot_path)
        return screenshot_path


# ----------------------------------------------------------------------------------


    def _exist_notify(self, photo_name: str, message: str):
        photo_path= self._screenshot(photo_name=photo_name)

        self.chatWork.chatwork_image_notify(
            chatwork_roomid=os.getenv('CHATWORK_ROOM_ID'),
            chatwork_notify_token=os.getenv('CHATWORK_TOKEN'),
            message=message,
            img_path=photo_path,
            resize_image_path=photo_path,
        )


# ----------------------------------------------------------------------------------

