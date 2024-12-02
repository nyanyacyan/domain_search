# coding: utf-8
# ----------------------------------------------------------------------------------
#! ここで定義して「Flow」で扱う
#! 引数はここで基本渡す。


# ----------------------------------------------------------------------------------
import os, time, asyncio
import pandas as pd
from typing import Any, Dict, List
from dotenv import load_dotenv
from datetime import datetime


# 自作モジュール
from .spreadsheetRead import GSSReadNoID
from .utils import Logger
from .seleniumBase import SeleniumBasicOperations
from .elementManager import ElementManager
from .notify import ChatworkNotify
from .path import BaseToPath
from .fileWrite import AppendWrite

from ..const_domain_search import GssInfo, Extension, SubDir, SendMessage, FileName
from ..const_element_domain import XserverXpath, ConohaWingXpath, OnamaeXpath, BoolTextList, 
load_dotenv()


####################################################################################
# **********************************************************************************


class GssToNotify:
    def __init__(self, sheet_url, chrome, debugMode=True) -> None:
        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.sheet_url = sheet_url
        self.chrome = chrome

        # インスタンス化
        self.gss_read = GSSReadNoID(sheet_url=self.sheet_url, chrome=self.chrome, debugMode=debugMode)
        self.selenium = SeleniumBasicOperations(chrome=self.chrome, debugMode=debugMode)
        self.element = ElementManager(chrome=self.chrome, debugMode=debugMode)
        self.chatWork = ChatworkNotify(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)
        self.currentDate = datetime.now().strftime('%y%m%d_%H%M%S')
        self.append_write = AppendWrite(debugMode=debugMode)

# ----------------------------------------------------------------------------------


    async def flowProcess(self):
        df = self._get_df_to_gss()

        tasks = []
        for index, row in df.iterrows():
            tasks.append(self.row_process(row=row))
            self.logger.debug(f'{index} 個目のtaskを追加')

        self.logger.debug(f"tasks: {tasks}")
        await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# 行の処理

    async def row_process(self, row: pd.Series):
        id = self._get_row_ID(row=row)
        site_name = self._get_row_name(row=row)
        url = self._get_row_url(row=row)
        domain_list = self._get_row_value_list(row=row, key_list=GssInfo.DOMAIN_COL.value)
        search_xpath_list = self._get_row_value_list(row=row, key_list=GssInfo.SEARCH_XPATH_COL.value)
        true_xpath_list = self._get_row_value_list(row=row, key_list=GssInfo.TRUE_XPATH.value)
        false_xpath_list = self._get_row_value_list(row=row, key_list=GssInfo.FALSE_XPATH.value)
        self.logger.debug(f"\ndomain_list: {domain_list}\nsearch_xpath_list: {search_xpath_list}\ntrue_xpath_list: {true_xpath_list}\nfalse_xpath_list: {false_xpath_list}")

        search_input_element = search_xpath_list[0]
        search_bar_element = search_xpath_list[1]
        self.logger.debug(f"\nsearch_input_element: {search_input_element}\nsearch_bar_element: {search_bar_element}\nsearch_result: {search_result}")


        for domain in domain_list:
            domain_extension = await self._get_domain_tail(domain=domain)
            self.logger.debug(f"\nurl: {url}\nid: {id}\nsite_name: {site_name}\ndomain: {domain}")
            await self.open_site(url=url)
            await self._search_bar_input(by='xpath', value=search_input_element, input_text=domain)
            await self._search_bar_click(by='xpath', value=search_bar_element)
            if await self._search_result_bool(domain_extension=domain_extension, true_xpath_list=true_xpath_list, false_xpath_list=false_xpath_list, domain=domain):
                photo_name = f"{site_name}_{domain}"
                message = SendMessage.CHATWORK.value.format(siteName=site_name, domain=domain)
                self.logger.debug(f"\nphoto_name: {photo_name}\nmessage: {message}")

                await self._exist_notify(photo_name=photo_name, message=message)
            else:
                self.logger.info(f"探しているドメインは {id} {site_name} サイトにはありませんでした: {domain}")


# ----------------------------------------------------------------------------------
# 正と負、それぞれの要素をのワードを検知して真偽値を返す

    def _search_result_bool(self, domain_extension: str, site_name: str, true_xpath_list: List, false_xpath_list: List, domain: str):
        # xpathのリストを渡してあるものをリスト化
        true_elements = self._get_exists_elements(xpath_list=true_xpath_list, domain_extension=domain_extension)
        false_elements = self._get_exists_elements(xpath_list=false_xpath_list, domain_extension=domain_extension)

        self.logger.debug(f"\ntrue_elements: {true_elements}\nfalse_elements: {false_elements}")

        if true_elements:
            true_comment = f"{site_name} に {domain} にあることを検知しました\n{true_elements}"
            self.logger.debug(f'true_comment: {true_comment}')
            # 検知履歴に追記
            self.append_write.append_result_text(data=true_comment, subDirName=site_name, fileName=FileName.TRUE_HISTORY.value)
            return True

        elif false_elements:
            false_comment = self.logger.info(f"{site_name} に {domain} はありません。\n{false_elements}\n")
            # 検知履歴に追記
            self.append_write.append_result_text(data=false_comment, subDirName=site_name, fileName=FileName.FALSE_HISTORY.value)
            return False

        else:
            none_comment = f"※確認必要\n{site_name} にある {domain} は通常とは違うステータスです\n（※サイト修正された可能性があります）: {self.currentDate}"
            self.append_write.append_result_text(data=none_comment, subDirName=site_name, fileName=FileName.FALSE_HISTORY.value)
            return True



# ----------------------------------------------------------------------------------
# xpathのリストを渡してあるものをリスト化

    def _get_exists_elements(self, xpath_list: List, domain_extension: str):
        elements = []
        for true_element_format in xpath_list:
            # スプシにあるxpathのFormatにdomain_tailを入れてPathにする
            true_element_xpath = true_element_format.format(extension=domain_extension)
            # 要素の検索
            true_element = self.element.getElement(true_element_xpath)
            if true_element:
                elements.append(true_element)
        return elements


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
        df = self.gss_read.spreadsheet_to_df()
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

    def _get_row_value_list(self, row: pd.Series, key_list: List):
        value_list = [row[key] for key in key_list if row[key] is not None]
        return value_list


# ----------------------------------------------------------------------------------


    def _search_bar_input(self, by: str, value: str, input_text: str):
        return self.element.clickClearInput(by=by, value=value, inputText=input_text)


# ----------------------------------------------------------------------------------


    def _search_bar_click(self, by: str, value: str):
        return self.element.clickElement(by=by, value=value)


# ----------------------------------------------------------------------------------



    def _screenshot(self, photo_name: str):
        return self.selenium.screenshot_limit(photo_name=photo_name)


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
# 親要素から絞り込んだ要素からtextを取得

    def _get_sort_element_text(self, parent_path: str, child_path: str):
        scope_element = self.element._get_sort_element(parent_path=parent_path, child_path=child_path)
        text = self.element._get_text(element=scope_element)
        self.logger.debug(f"\nscope_element: {scope_element}\ntext: {text}")
        return text


# ----------------------------------------------------------------------------------
# const_formatに代入してxpathを完成させる

    def _domain_xpath_form(self, domain: str, result_xpath: str):
        domain_split = domain.split('.')
        domain_extension = domain_split[1]

        element_xpath = result_xpath.format(domain_extension=domain_extension)
        self.logger.debug(f"\ndomain_extension: {domain_extension}\nelement_xpath: {element_xpath}")
        return element_xpath


# ----------------------------------------------------------------------------------


    def _get_domain_tail(self, domain: str):
        # 取得した要素をテキスト化してリストにする
        domain_split = domain.split('.')
        extension = domain_split[1]
        domain_extension = f".{extension}"
        self.logger.debug(f"domain_extension: {domain_extension}")
        return domain_extension


# ----------------------------------------------------------------------------------

