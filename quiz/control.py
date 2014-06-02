
import leveldb


class RobbyControl(object):

    # TODO: クライアントに参加者一覧の更新を通知したり
    def trigger_client_joined(self):
        pass

    # TODO: クライアントへクイズが次のものへ移ることを通知します
    def trigger_next_quiz(self):
        pass

    # TODO: 一連のクイズを終了し，スコア画面等に遷移します
    def trigger_room_closing(self):
        pass

