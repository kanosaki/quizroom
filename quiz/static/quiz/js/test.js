QUnit.test("Conduit test", function (assert) {
    // WebSocketの代わりをするSourceオブジェクト
    var DummySource = function () {
        this.onNext = undefined;
    };

    var source = new DummySource();
    var conduit = new Conduit(source);
    var results = {};
    conduit.on('message_a', function (data) {
        results['message_a'] = data;
    });
    conduit.missingHandler = function (msg_type, msg_content) {
        results['missing-' + msg_type] = msg_content;
    };

    source.onNext({'type': 'message_a', 'content': {'foo': 'bar'}});
    source.onNext({'type': 'unknown_hogehoge', 'content': "foobar"});

    assert.deepEqual(results['message_a'], {'foo': 'bar'});
    assert.deepEqual(results['missing-unknown_hogehoge'], "foobar");
    // We should add more tests...
});