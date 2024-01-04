# Slack
from slack_bolt import App
from slack_sdk import WebClient
# Flask
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
# ソケットモード用
from slack_bolt.adapter.socket_mode import SocketModeHandler
# 環境変数読み込み
import env

# モードに応じて書き換え
BOT_USER_ID = env.get_env_variable('BOT_USER_ID')
# Botトークン（Flask）
WEBAPPS_SLACK_TOKEN = env.get_env_variable('WEBAPPS_SLACK_TOKEN')
WEBAPPS_SIGNING_SECRET = env.get_env_variable('WEBAPPS_SIGNING_SECRET')

# Botトークン（ソケットモード）
SOCK_SLACK_BOT_TOKEN = env.get_env_variable('SOCK_SLACK_BOT_TOKEN')
SOCK_SLACK_APP_TOKEN = env.get_env_variable('SOCK_SLACK_APP_TOKEN')

# モード入れ替え（WebAPサーバ実行＝Flask／ローカル実行＝ソケットモード)
def app_mode_change(i_name):
    if i_name == "__main__":
        return App(token=SOCK_SLACK_BOT_TOKEN)
    else:
        return App(token=WEBAPPS_SLACK_TOKEN, signing_secret=WEBAPPS_SIGNING_SECRET)

# グローバルオブジェクト
s_app = app_mode_change(__name__)
# Flaskクラスのインスタンス生成
app = Flask(__name__)
#app.config['JSON_AS_ASCII'] = False
handler_flask, handler_socket = None,None

#ソケットーモードの場合のハンドラ設定
if __name__ == "__main__":
    handler_socket = SocketModeHandler(app=s_app, app_token=SOCK_SLACK_APP_TOKEN, trace_enabled=True)
#Flaskでのハンドラー設定
else:
    handler_flask = SlackRequestHandler(s_app)

# Flask httpエンドポイント
# 疎通確認用1
@app.route('/', methods=['GET', 'POST'])
def home():
    return "Hello World Rainbow 2!!"
# 疎通確認用2
@app.route("/test", methods=['GET', 'POST'])
def hello_test():
    return "Hello, This is test.2!!"

#イベント登録されたリクエストを受け付けるエンドポイント
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler_flask.handle(request)

#Interactiveなリクエストを受け付けるエンドポイント
@app.route("/slack/interactive", methods=["POST"])
def slack_interactive():
    return handler_flask.handle(request)


# ホーム画面が開かれたイベントを処理するリスナーを定義
@s_app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:

        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Welcome to the registration form! Please enter your name:"
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "name_input",  # action_idはコールバックに使用されます
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter your name"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Name"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Submit"
                                },
                                "value": "submit_btn",
                                "action_id": "submit_action"  # action_idはコールバックに使用されます
                            }
                        ]
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

# ボタンのアクションを処理するリスナーを定義
@s_app.action("submit_action")
def handle_submit_action(ack, body, client, view, logger):
    # 最初にackを呼び出して、Slackに対してリクエストを受け取ったことを確認する応答を送信します。
    ack()
    try:
        # action_idがsubmit_actionであるボタンが押されたときに送られるpayloadから、
        # 入力された名前を取得します。この場合、inputブロックにblock_idを追加して、 そのblock_idを使って値を取得します。
        action = body['actions'][0]
        if action['action_id'] == 'submit_action':
            # ユーザーが入力した名前を取得するために、inputブロックのblock_idを使用します。
            user_name = body['user']['username']
            user_id = body['user']['id']

            # ユーザーに応答メッセージを送信
            client.chat_postMessage(
                channel=user_id,
                text=f"Thank you for registering, <@{user_id}>!"
            )
    except Exception as e:
        logger.error(f"Error sending message: {e}")

# __name__はPythonにおいて特別な意味を持つ変数です。
# 具体的にはスクリプトの名前を値として保持します。
# この記述により、Flaskがmainモジュールとして実行された時のみ起動する事を保証します。
# （それ以外の、例えば他モジュールから呼ばれた時などは起動しない）
if __name__ == '__main__':
    EXEC_MODE = "SLACK_SOCKET_MODE"
    # Slack ソケットモード実行
    if EXEC_MODE == "SLACK_SOCKET_MODE":
        handler_socket.start()
    # Flask Web/APサーバ 実行
    elif EXEC_MODE == "FLASK_WEB_API":
        # Flaskアプリの起動
        # →Webサーバが起動して、所定のURLからアクセス可能になります。
        # →hostはFlaskが起動するサーバを指定しています（今回はローカル端末）
        # →portは起動するポートを指定しています（デフォルト5000）
        app.run(port=8000, debug=True)