(function () {
    // -----------------------------------
    // Ajax utilities
    // From: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
    // -----------------------------------
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
            }
        }
    });


    // ------------------------------------
    // WebSocket utilities
    // NOTE: 具体的な使用法に関してはquiz/js/test.jsのConduit testを参照
    // ------------------------------------
    /**
     * WebSocket等のをラップしてメッセージを受け渡しするためのクラス
     * @param source 上流
     * @constructor
     */
    var Conduit = function (source) {
        this.source = source;
        this.handlers = {};

        var self = this;
        source.onNext = function (data) {
            var msg_type = data['type'];
            var msg_content = data['content'];
            if (!_.isUndefined(msg_type)) {
                self.dispatch(msg_type, msg_content);
            } else {
                self.onUnknown(data);
            }
        };
    };

    Conduit.prototype = {
        /**
         * (内部用メソッド)
         * 登録されたメッセージハンドラへメッセージを配信します
         * @param msg_type
         * @param msg_content
         * @returns {Conduit}
         */
        dispatch: function (msg_type, msg_content) {
            var callback = this.handlers[msg_type];
            if (!_.isUndefined(callback)) {
                callback(msg_content);
            } else {
                this.missingHandler(msg_type, msg_content);
            }
            return this;
        },
        /**
         *
         * @param msg_type
         * @param callback
         * @returns {Conduit}
         */
        on: function (msg_type, callback) {
            if (!_.isUndefined(this.handlers[msg_type])) {
                // 複数ディスパッチはしないので，上書きするときは警告
                console.warn('Overriding conduit handler for message ' + msg_type);
            }
            this.handlers[msg_type] = callback;
            return this;
        },
        /**
         * このConduitを通して上流へメッセージを送信します
         * @param msg_type メッセージタイプ．文字列
         * @param data 送るデータ．オブジェクト
         * @returns {Conduit} チェイン用に自分を帰します
         */
        send: function (msg_type, data) {
            var sending_data = {
                type: msg_type,
                content: data
            };
            this.source.send(sending_data);
            return this;
        },
        /**
         * ディスパッチが出来ない不正なフォーマットを持ったデータを受け取ったときに呼び出されるハンドラ
         * @param sock_msg 受け取ったデータ
         * @returns {Conduit} チェイン用に自分を帰します
         */
        onUnknown: function (sock_msg) {
            return this;
        },
        /**
         * メッセージハンドラが登録されていないメッセージを受け取ったときに呼び出されるデフォルトのハンドラ
         * @param msg_type メッセージタイプ．文字列
         * @param msg_content メッセージの内容．オブジェクト
         * @returns {Conduit} チェイン用に自分を帰します
         */
        missingHandler: function (msg_type, msg_content) {
            console.log("Channel :: Unknown message type" + msg_type);
            return this;
        }
    };
    window.Conduit = Conduit;

    var WebSocketSource = function (ws_addr) {
        this.onNext = function (json_data) {
        };
        this.sock = new WebSocket(ws_addr);
        var self = this;
        this.sock.onmessage = function (sock_msg) {
            var data = JSON.parse(sock_msg.data);
            self.onNext(data);
        };
    };

    WebSocketSource.prototype = {
        send: function (json_data) {
            var data = JSON.stringify(json_data);
            this.sock.send(data);
        }
    };
    window.WebSocketSource = WebSocketSource;
})();

