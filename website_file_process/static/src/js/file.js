odoo.define('website_file_process.files', function (require) {
    'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;

    // Check filesizes, add corresponding message to targeted info div
    var checkFileSizes = function (el, info_div) {
        var files = $(el).prop('files');
        var size = '';
        var msg = '';
        var maxSize = $(el).data('maxsize');
        var elements = '';
        var fileCount = files.length.toString() + _t(' file(s) selected:');
        var fileNameLabel = _t('File name: ');
        var fileSizeLabel = _t('File size: ');
        var fileTooBigLabel = _t('File size too big! Max size for file is ') + maxSize + 'MB';
        var fileTooBig = false;

        $(info_div).addClass('d-none');

        elements += '<p>' + fileCount + '</p><p id="file_sizes">';

        for (var i = 0; i < files.length; ++i) {
            var file = files[i];
            if (file.size > 1024 * 1024) {
                size = (Math.round(file.size * 10 / (1000 * 1000)) / 10).toString() + 'MB';
            }
            else {
                size = (Math.round(file.size * 10 / 1000) / 10).toString() + 'KB';
            }
            // If file is larger than max_size, clear the element and give notifications
            if (file.size > (maxSize * 1000 * 1000)) {
                fileTooBig = true;
                elements += '<strong>' + fileTooBigLabel + '</strong><br/>'
                elements += fileNameLabel + file.name + ', ' + fileSizeLabel + size + '<br/><br/>';
            } else {
                elements += fileNameLabel + file.name + ', ' + fileSizeLabel + size + '<br/>';
            }
        }
        elements += "</p>";
        if (fileTooBig) {
            $(info_div).removeClass('d-none alert-info').addClass('alert-danger');
        } else {
            $(info_div).removeClass('d-none alert-danger').addClass('alert-info');
        }
        $(info_div).html(elements);
        return fileTooBig;
    }

    return {
        checkFileSizes: checkFileSizes
    } 
});
