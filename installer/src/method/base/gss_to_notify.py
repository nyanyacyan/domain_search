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
from .spreadsheetRead import SpreadsheetRead
from .utils import Logger
from .seleniumBase import SeleniumBasicOperations
from .elementManager import ElementManager
from .notify import ChatworkNotify
from .path import BaseToPath
from .fileWrite import AppendWrite

from ..const_domain_search import GssInfo, Extension, SubDir, SendMessage, FileName
from ..const_element_domain import OnamaeXpath, BoolTextList
load_dotenv()


####################################################################################
# **********************************************************************************


class GssToNotify:
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
        self.currentDate = datetime.now().strftime('%y%m%d_%H%M%S')
        self.append_write = AppendWrite(debugMode=debugMode)

# ----------------------------------------------------------------------------------


    async def flowProcess(self):
        df = self._get_df_to_gss()

        tasks = []
        for row in df.iterrows():
            tasks.append(self.row_process(row=row))

        self.logger.debug(f"tasks: {tasks}")
        await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# 行の処理

    async def row_process(self, row: pd.Series):
        id = self._get_row_ID(row=row)
        site_name = self._get_row_name(row=row)
        url = self._get_row_url(row=row)
        domain_list = self._get_row_value_list(row=row, key_list=GssInfo.DOMAIN_COL.value)
        xpath_list = self._get_row_value_list(row=row, key_list=GssInfo.XPATH_COL.value)
        self.logger.debug(f"\ndomain_list: {domain_list}\nxpath_list: {xpath_list}")

        search_input_element = xpath_list[0]
        search_bar_element = xpath_list[1]
        search_result = xpath_list[2]
        result_sub_dir_name = SubDir.RESULT_SUMMARY.value
        result_file_name = FileName.RESULT_FILE.value
        self.logger.debug(f"\nsearch_input_element: {search_input_element}\nsearch_bar_element: {search_bar_element}\nsearch_result: {search_result}")


        for domain in domain_list:
            self.logger.debug(f"\nurl: {url}\nid: {id}\nsite_name: {site_name}\ndomain: {domain}")
            await self.open_site(url=url)
            await self._search_bar_input(by='xpath', value=search_input_element, input_text=domain)
            await self._search_bar_click(by='xpath', value=search_bar_element)
            if await self._search_result_bool(by='xpath', value=search_result, domain=domain, subDirName=result_sub_dir_name, fileName=result_file_name):
                photo_name = f"{site_name}_{domain}"
                message = SendMessage.CHATWORK.value.format(siteName=site_name, domain=domain)
                self.logger.debug(f"\nphoto_name: {photo_name}\nmessage: {message}")

                await self._exist_notify(photo_name=photo_name, message=message)
            else:
                self.logger.info(f"探しているドメインは {id} {site_name} サイトにはありませんでした: {domain}")


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


    def _site_name_branch(self, site_name: str, domain: str, result_xpath_format: str, child_path: str, true_text_list: List, false_text_list: List, subDirName: str, fileName: str):
        # フォーマットにdomainの詳細を入れ込んでpathを形成する
        result_xpath = self._domain_xpath_form(domain=domain, result_xpath=result_xpath_format)

        # 絞り込んで判定部分のtextを出力
        # お名前ドットコム
        if site_name == OnamaeXpath.SITE_NAME.value:
            result_text = self.element._get_sort_element_text(parent_path=result_xpath, child_path=child_path)



# ----------------------------------------------------------------------------------
# 正と負それぞれのワードを検知して真偽値を返す

    def _search_result_bool(self, site_name: str, result_text: str, domain: str, true_text_list: List, false_text_list: List, subDirName: str, fileName: str):
        for false_text in false_text_list:
            if result_text == false_text:
                none_comment = f"{domain} は {site_name} にはありません\nFalse_text: {false_text} を検知。{self.currentDate} "
                self.logger.warning(none_comment)
                self.append_write.append_result_text(data=none_comment, subDirName=subDirName, fileName=fileName)
                return False

        for true_text in true_text_list:
            if result_text == true_text:
                current_url = self.chrome.current_url
                true_comment = f"{site_name} に {domain} を検知しました!: {self.currentDate}\nurl: {current_url}"
                self.logger.info(true_comment)
                return True

        true_comment = f"※確認必要\n{site_name} にある {domain} は通常とは違うステータスです\n（※サイト修正された可能性があります）: {self.currentDate}\nurl: {current_url}"
        self.logger.info(true_comment)
        return True


# ----------------------------------------------------------------------------------