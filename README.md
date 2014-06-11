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

3. 依存ライブラリを入れる
	
	```sh
    $ pip install -r etc/requirements.txt
    ```

4. テスト環境用初期設定
	
	```sh
    $ make resetdb_test  # DBを初期化
    # ユーザー作る？みたいに聞かれるので no で
    $ make bower_update  # 使っているJavaScript関連のライブラリを準備
	```
	
5. 実行

	```sh
    $ ./run.py
    ```
