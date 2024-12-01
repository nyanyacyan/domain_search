# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio

# 自作モジュール
from base.utils import Logger
from base.pyppeteer import PyppeteerUtils
from const_domain_search import SiteUrl, GssInfo
from .base.chrome import ChromeManager
from .base.gss_to_notify import GssToNotify


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class Flow:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # const
        self.url_1 = SiteUrl.HOME_URL.value
        self.sheet_url = GssInfo.SITE.value


        # インスタンス
        self.gss_to_notify = GssToNotify(sheet_url=self.sheet_url, chrome=self.chrome, debugMode=debugMode)


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        self.gss_to_notify.flowProcess()








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = Flow()
    asyncio.run(test_flow.process())