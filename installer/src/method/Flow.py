# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio

# 自作モジュール
from base.utils import Logger
from base.pyppeteer import PyppeteerUtils
from const_domain_search import SiteUrl

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class Flow:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.chrome = PyppeteerUtils(debugMode=debugMode)

        # const
        self.url_1 = SiteUrl.HOME_URL.value




####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        page = await self.chrome.new_page()
        await self.chrome.goto_page(page=page, url=self.url_1)








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = Flow()
    asyncio.run(test_flow.process())