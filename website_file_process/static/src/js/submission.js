odoo.define('website_file_process.submission', function (require) {
    'use strict';

    var loadingScreen = require('website_utilities.loader').loadingScreen;

    $(function () {

        function processfile(file) {
            if(!(/image/i).test(file.type)){
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
                image.onload = function() {
                    var resized = resizeMe(image);
                    var newinput = document.createElement("input");
                    newinput.type = 'hidden';
                    newinput.name = 'resized';
                    newinput.value = resized;
                    var form_ID = $(this).closest("form").attr('id');
                    console.log(form_ID);
                    form_ID.append(newinput);
                    $.unblockUI();
                }
            };
        }

        function resizeMe(img) {
            var canvas = document.createElement('canvas');
            var width = img.width;
            var height = img.height;
            var MAX_WIDTH = $('#image').attr('data-maxwidth');
            var MAX_HEIGHT = $('#image').attr('data-maxheight');

            // calculate the width and height, constraining the proportions
            if (width > height) {
                if (width > MAX_WIDTH) {
                    height *= MAX_WIDTH / width;
                    width = MAX_WIDTH;
                }
            } else {
                if (height > MAX_HEIGHT) {
                    width *= MAX_HEIGHT / height;
                    height = MAX_HEIGHT;
                }
            }
            canvas.width = width;
            canvas.height = height;
            var ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);
            return canvas.toDataURL("image/jpeg");
        }
    });
});
