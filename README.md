まだうごかないよ


環境構築
--------
1. 事前の準備
以下のプログラムを入れておく

* Python 3.4 
* bower

Pythonを入れたら，virtualenvを作っておくのがおすすめ

2. クローン
	
	```sh
    $ git clone https://github.com/kanosaki/quizroom
    $ cd quizroom
    ```

3. 初期設定
	
	```sh
    $ make init
    # ユーザー作る？みたいに聞かれるのでおのおの管理者ユーザーを
    # 作るといいと思う 
	```
	
4. 実行

	```sh
    $ ./run.py
    ```

URLの構造
---------
### Djangoが処理するもの
`/lobby/{{lobby_id}}`
出題したりするメインのページ

`/lobby/control/{{lobby_id}}`
ロビー制御用のページ

`/user/`
ユーザーを登録したり

`/admin`
Django組み込みのDBいじるページ

`/control`


### Tornadoが処理するもの
`/ws` -- WebSocket関連
