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
    quiz.default_ajax_handler = function (res) {
        if (res.status != 'ok') {
            quiz.notify.error(res.message);
        } else if (res.status == 'ok' && res.message) {
            quiz.notify.info(res.message);
        }
    };

    // ------------------------------------------
    // Navbar
    // ------------------------------------------
    // Navbarはテンプレートページ(quiz/base.html)で初期化
    quiz.Navbar.prototype = {

    }
})();