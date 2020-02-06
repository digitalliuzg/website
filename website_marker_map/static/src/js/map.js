/* global google:false */

(function markerMap () {
    'use strict';
    function initMap () {

        var api_url = "/marker_map_api/" +
            window.location.hash.replace("#", "");

        $.get(api_url, function (data) {

            var parsed_data = JSON.parse(data);

            var settings = {
                zoom: 5,
                center: {
                    lat: 65.5274,
                    lng: 27.1588,
                },
            };

            if (data.settings) {
                settings = parsed_data.settings;
            }

            var map = new google.maps.Map(
                document.getElementById('marker_map'), settings);

            parsed_data.markers.forEach(function (marker_data) {

                marker_data.map = map;
                var marker = new google.maps.Marker(marker_data);

                if (marker_data.show_infowindow === true) {

                    var infowindow = new google.maps.InfoWindow({
                        content: marker_data.infowindow_text,
                    });

                    marker.addListener('click', function () {
                        infowindow.open(map, marker);
                    });

                    if (marker_data.infowindow_open_start === true) {
                        infowindow.open(map, marker);
                    }
                }
            });
        });
    }

    $(window).hashchange(initMap);

    $(document).ready(function () {
        initMap();
    });
}());
