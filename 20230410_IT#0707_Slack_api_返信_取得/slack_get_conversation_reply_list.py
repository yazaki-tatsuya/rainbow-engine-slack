import json
import pandas as pd
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# 親フォルダパスを取得
file_path = Path(__file__).parent.parent
# 「.env」ファイルのパスを設定
env_path = file_path/'.env'
# 「.env」ファイルのロード
load_dotenv(dotenv_path=env_path)

def main():

    ### 全投稿を取得 ###
    # APIのURL組み立て
    url_1 = os.environ['URL_MESSAGE']
    channel = ("?channel="+os.environ['CHANNEL']) if os.environ['CHANNEL'] != "" else ""
    url_1 = url_1 + channel

    # ヘッダー部
    headers = {
        "Content-Type":"application/json",
        "User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
        "Authorization":"Bearer "+os.environ['SLACK_BOT_TOKEN']
    }
    
    # POSTリクエスト
    response_1 = requests.post(url_1, headers=headers)
    
    # レスポンスの内容をtext形式で取得
    result_1 = response_1.text

    # レスポンスのJSONを表形式データ（DataFrame）に変形する
    # JSONライブラリを用いて、JSONファイルのデータをJSONオブジェクトとしてロード
    json_object_1 = json.loads(result_1)
    # pandasの「json_normalize」関数を用いてデータを正規化
    # 第１引数：json形式のオブジェクト
    # 第２引数：分解対象のデータのkey
    # 第３引数：その他、分解した明細に付与するデータ
    df_1 = pd.json_normalize(json_object_1, record_path =['messages'])
    # df = pd.json_normalize(json_object_1, record_path =['students'],meta=['school_name', 'class'])
 
    ### 返信取得処理 ###
    # dfを1件ずつループ
    for index, row in df_1.iterrows():

        # 返信がある場合
        if row['reply_count'] > 0:

            ### 返信を取得 ###
            # APIのURL組み立て
            url_2 = os.environ['URL_REPLY']
            channel = ("?channel="+os.environ['CHANNEL']) if os.environ['CHANNEL'] != "" else ""
            ts = ("&ts="+os.environ['TS']) if os.environ['TS'] != "" else ""
            url_2 = url_2 + channel + ts

            # POSTリクエスト
            response_2 = requests.post(url_2, headers=headers)
            
            # レスポンスの内容をtext形式で取得
            result_2 = response_2.text

            # レスポンスのJSONを表形式データ（DataFrame）に変形する
            # JSONライブラリを用いて、JSONファイルのデータをJSONオブジェクトとしてロード
            json_object_2 = json.loads(result_2)
            # pandasの「json_normalize」関数を用いてデータを正規化
            # 第１引数：json形式のオブジェクト
            # 第２引数：分解対象のデータのkey
            # 第３引数：その他、分解した明細に付与するデータ
            df_2 = pd.json_normalize(json_object_2, record_path =['messages'])
            print(df_2)

            # df_2をdf_1に追加（マージ）
            df_1 = pd.concat([df_1,df_2],ignore_index=True).drop_duplicates(['client_msg_id'], keep='last')

    # 表形式データ（DataFrame）をcsv出力する
    df_1.to_csv('./slack_get_conversation_reply_list.csv', sep=',', encoding='shift-jis', header=True)

if __name__ == "__main__":
     main()