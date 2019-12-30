odoo.define("website_channel_messages.channels", function (require) {
    "use strict";

    var ajax = require("web.ajax");
    var core = require("web.core");
    var _t = core._t;
    var toastr = require('website_utilities.notifications').toastr;

    $(function () {

        $(".select2").select2();

        toastr.options = {
            "positionClass": "toast-bottom-center",
            "closeButton": true,
            "debug": false,
            "preventDuplicates": true,
            "onclick": null,
            "showDuration": "100",
            "hideDuration": "1000",
            "timeOut": "0",
            "extendedTimeOut": "1000",
            "tapToDismiss": false,
            "showMethod": "fadeIn",
            "hideMethod": "fadeOut",
        };

        $(document).on("click", "#create_channel_confirm", function () {
            var partner_ids = $("#recipients").select2("val").map(Number);
            var route = "/website_channel/create";
            var payload = {
                recipients: partner_ids,
                csrf_token: core.csrf_token,
            };
            if (partner_ids.length === 0) {
                toastr.error(_t("You must select recipient!"));
            } else {
                ajax.jsonRpc(route, "call", payload).then(function (res) {
                    // Check if the channel already existed
                    var channel_id = res.id;
                    if ($("#channel_" + channel_id).length === 0) {
                        location.reload();
                    } else {
                        var msg = _t("You already have a chat with these recipients.");
                        msg += "<br/><a href='/website_channel/" + channel_id + "'><b>";
                        msg += _t("Click here to open channel") + "</b></a>.";
                        toastr.info(msg);
                        $("#modal_create_channel").modal("hide");
                    }
                });
            }
        });
    });
});
