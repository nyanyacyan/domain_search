# coding: utf-8
#* 流れ  【非同期処理して並列処理】検索ワードを含んだURLにて検索→サイトを開く→解析→ブランド名、商品名、価格のリスト作成→バイナリデータへ保存→保存されてるバイナリデータ（保存した過去データ）を復元→現在のデータと突き合わせる→今までと違うものをリスト化→通知する
# ----------------------------------------------------------------------------------
import os, time


from .base.utils import Logger


# ----------------------------------------------------------------------------------
####################################################################################
# 一連の流れ

class Flow:
    def __init__(self, sheet, debug_mode=False):
        self.sheet = sheet
        self.logger = self.setup_logger(debug_mode=debug_mode)


####################################################################################
# ----------------------------------------------------------------------------------

# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# ここから処理を記載
#! 処理を書く前に詳細設計をコメントに残すことから始める（TODOを使う）


# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    def process(self, ):
        self.logger.debug(f"***** Flow.process 開始 *****")





        self.logger.debug(f"***** Flow.process 終了 *****")

# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = Flow()
    test_flow.process()