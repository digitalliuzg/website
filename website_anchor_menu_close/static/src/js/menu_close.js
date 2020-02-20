/* global $ */
(function() {
    $(window).on("hashchange", function() {
        $("#top_menu_collapse").removeClass("show");
        $("#top_menu_collapse_clone").removeClass("show");
    });
})();
