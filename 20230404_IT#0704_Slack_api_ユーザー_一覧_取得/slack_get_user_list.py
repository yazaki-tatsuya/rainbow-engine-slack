import json
import pandas as pd
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# 親フォルダパスを取得
file_path = Path(__file__).parent
# 「.env」ファイルのパスを設定
env_path = file_path/'.env'
# 「.env」ファイルのロード
load_dotenv(dotenv_path=env_path)

def main():

    # APIのURL
    url = os.environ['URL']

    # ヘッダー部
    headers = {
        "Content-Type":"application/json",
        "User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
        "Authorization":"Bearer "+os.environ['SLACK_BOT_TOKEN']
    }
    
    # POSTリクエスト
    # →ユーザー一覧を取得します。
    response = requests.post(url, headers=headers)
    
    # レスポンスの内容をtext形式で取得
    result = response.text

    # レスポンスのJSONを表形式データ（DataFrame）に変形する
    # JSONライブラリを用いて、JSONファイルのデータをJSONオブジェクトとしてロード
    json_object = json.loads(result)
    # pandasの「json_normalize」関数を用いてデータを正規化
    # 第１引数：json形式のオブジェクト
    # 第２引数：分解対象のデータのkey
    # 第３引数：その他、分解した明細に付与するデータ
    df = pd.json_normalize(json_object, record_path =['members'])
    # df = pd.json_normalize(json_object, record_path =['students'],meta=['school_name', 'class'])
 
    # 表形式データ（DataFrame）をcsv出力する
    # →日本語も含まれるため、エンコーディングはshift-jisを指定
    df.to_csv('./slack_get_user_list.csv', sep=',', encoding='shift-jis', header=True)

if __name__ == "__main__":
     main()
