odoo.define("website_channel_messages.submission", function (require) {
    "use strict";

    var loadingScreen = require("website_utilities.loader").loadingScreen;
    var checkFileSizes = require("website_channel_messages.files").checkFileSizes;

    require("web.dom_ready");

    var lang = "fi";
    if (window.location.pathname.indexOf("en_US") >= 0) {
        lang = "en";
    } else if (window.location.pathname.indexOf("sv_SE") >= 0) {
        lang = "sv";
    }
    ClassicEditor.create(document.querySelector("#comment"), {
        language: lang,
        toolbar: [
            "heading", "|", "bold", "italic",
            "link", "bulletedList", "numberedList",
            "blockQuote", "undo", "redo",
        ],
    }).then(function (editor) {
        editor.model.document.on("change:data", function () {
            var text = $.trim(editor.getData());
            $("#submission_submit").prop("disabled", !text);
        });
    });

    function resizeMe (img) {
        var canvas = document.createElement("canvas");
        var width = img.width;
        var height = img.height;
        var MAX_WIDTH = $("#image").attr("data-maxwidth");
        var MAX_HEIGHT = $("#image").attr("data-maxheight");

        // Calculate the width and height, constraining the proportions
        if (width >= height && width > MAX_WIDTH) {
            height *= MAX_WIDTH / width;
            width = MAX_WIDTH;
        } else if (width < height && height > MAX_HEIGHT) {
            width *= MAX_HEIGHT / height;
            height = MAX_HEIGHT;
        }
        canvas.width = width;
        canvas.height = height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);
        return canvas.toDataURL("image/jpeg");
    }

    function processfile (file) {
        if (!(/image/i).test(file.type)) {
            // Not an image, prevent this
            return false;
        }
        loadingScreen();
        var reader = new FileReader();
        reader.readAsArrayBuffer(file);
        
        reader.onload = function (event) {
            var blob = new Blob([event.target.result]);
            window.URL = window.URL || window.webkitURL;
            var blobURL = window.URL.createObjectURL(blob);
            var image = new Image();
            image.src = blobURL;
            image.onload = function () {
                var resized = resizeMe(image);
                var newinput = document.createElement("input");
                newinput.type = "hidden";
                newinput.name = "resized";
                newinput.value = resized;
                $("#submission_form").append(newinput);
                $.unblockUI();
            };
        };
    }

    $("#submission_submit").on("click", function () {
        loadingScreen();
        $("#submission_form").submit();
    });

    $("#image").on("change", function () {
        var file = $(this).prop("files")[0];
        var fileTooBig = checkFileSizes($(this), $("#submission_info_div"));
        if (fileTooBig) {
            $(this).val("");
            $("#submission_submit").prop("disabled", "disabled");
        } else {
            if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
                alert("The File APIs are not fully supported in this browser.");
                return false;
            }
            processfile(file);
        }
    });

    $("#file").on("change", function () {
        var fileTooBig = checkFileSizes($(this), $("#submission_info_div"));
        if (fileTooBig) {
            $(this).val("");
            $("#submission_submit").prop("disabled", "disabled");
        }
    });
});
