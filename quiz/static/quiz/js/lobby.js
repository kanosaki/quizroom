
(function(){
    var ws_url = 'ws://localhost:8000/ws/lobby/' + window.quiz.lobby_id;

    var socket = new WebSocket(ws_url);
    socket.onmessage = function(sock_msg){
        var msg = JSON.parse(sock_msg.data);
        if (msg.type == 'request_update') {
            // ...
        }
    };
})();