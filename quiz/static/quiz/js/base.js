// quiz/base.html scripts

(function () {
    // ------------------------------------------
    // Notifications
    // ------------------------------------------
    var Notify = function () {
    };

    Notify.prototype = {
        info: function (html) {
            notif({
                type: "info",
                msg: html,
                width: "all",
                position: "center"
            });
        },
        error: function (html) {
            notif({
                type: "error",
                msg: html,
                position: "center",
                width: "all",
                autohide: false
            });
        }
    };

    quiz.notify = new Notify();

    // ------------------------------------------
    // Ajax utilities
    // ------------------------------------------
    quiz.default_ajax_handler = function (data) {
        if (data.status != 'ok') {
            quiz.notify.error(data.message);
        } else if (data.status == 'ok' && data.message) {
            quiz.notify.info(data.message);
        }
    };

    // ------------------------------------------
    // Navbar
    // ------------------------------------------
    // Navbarはテンプレートページ(quiz/base.html)で初期化
    quiz.Navbar.prototype = {

    }
})();
