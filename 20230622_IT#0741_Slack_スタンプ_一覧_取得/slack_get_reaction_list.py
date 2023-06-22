import json
import pandas as pd
import requests
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

# 親フォルダパスを取得
file_path = Path(__file__).parent
# 「.env」ファイルのパスを設定
env_path = file_path/'.env'
# 「.env」ファイルのロード
load_dotenv(dotenv_path=env_path)

def main():
    stamp_num = 1
    #####################################
    # スタンプを押したユーザーIDの一覧を取得
    #####################################
    # APIのURL
    url_1 = os.environ['URL_1']
    # クエリパラメータ
    channel = ("?channel="+os.environ['CHANNEL']) if os.environ['CHANNEL'] != "" else ""
    ts = ("&timestamp="+os.environ['TIMESTAMP']) if os.environ['TIMESTAMP'] != "" else ""
    full = ("&full="+os.environ['FULL']) if os.environ['FULL'] != "" else ""
    url_1 = url_1 + channel + ts + full

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
    #   ネストされている場合
    # df = pd.json_normalize(json_object,record_path=['message'])   # エラー：https://stackoverflow.com/questions/72478216/type-error-for-path-data-must-be-list-or-null
    df_1 = pd.json_normalize(json_object_1["message"],record_path=['reactions'])
    # df_1 = pd.json_normalize(json_object_1, record_path =['students'],meta=['school_name', 'class'])
    df_users = pd.DataFrame(df_1["users"][stamp_num],columns=["user_id"])

    #####################################
    # ユーザーIDからユーザー名を取得
    #####################################

    # APIのURL
    url_2 = os.environ['URL_2']
    # ユーザーの一覧をループ
    display_names = []
    for index, row in df_users.iterrows():
        # print(row['user_id'])

        # 各IDのユーザー情報を取得
        user = ("&user="+row['user_id']) if row['user_id'] != "" else ""
        url_2 = url_2 + user
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
        df_2 = pd.json_normalize(json_object_2['user']['profile'])

        # display_nameが空の場合、real_nameから取得する
        if df_2['display_name'].to_string(index=False, header=False) == "":
            display_names.append(df_2['real_name_normalized'].to_string(index=False, header=False))
        else :
            display_names.append(df_2['display_name_normalized'].to_string(index=False, header=False))

    # df_usersに列を追加
    df_users['display_name'] = display_names
    # 表形式データ（DataFrame）をcsv出力する
    df_users.to_csv('./'+df_1["name"][stamp_num]+'.csv', sep=',', encoding='shift-jis', header=True)
    

if __name__ == "__main__":
     main()