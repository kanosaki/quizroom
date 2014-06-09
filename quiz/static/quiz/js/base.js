// quiz/base.html scripts

(function () {
    window.quiz = window.quiz || {};

    window.quiz.notify_info = function (html) {
        notif({
            type: "info",
            msg: html,
            width: "all",
            position: "center"
        });
    };

    window.quiz.notify_error = function (html) {
        notif({
            type: "error",
            msg: html,
            position: "center",
            width: "all",
            autohide: false
        });
    };

    window.quiz.handle_ajax_response = function (res) {
        if (res.status != 'ok') {
            window.quiz.notify_error(res.message);
        } else if (res.status == 'ok' && res.message) {
            window.quiz.notify_info(res.message);
        }
    };
})();