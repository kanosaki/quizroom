(function () {
    var server_host = window.location.host;
    var ws_url = 'ws://' + server_host + '/ws/lobby/' + window.quiz.lobby_id;

    var socket = new WebSocket(ws_url);
    socket.send(JSON.stringify({
        "type": "join",
        "token": quiz.lobby_token
    }));
    socket.onmessage = function (sock_msg) {
        var msg = JSON.parse(sock_msg.data);
        if (msg.type == 'request_update') {
            // ...
        }
    };
})();