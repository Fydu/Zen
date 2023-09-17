// HOME PIECHART //
// The following lines of code were taken from Youtuber ProgProd thanks for the easyPieChart tutorial //

$(function() {
    $('.chart').easyPieChart({
        size: 160,
        barColor: "#e7b25c",
        scaleLength: 0,
        lineWidth: 15,
        trackColor: "#e7e3e0",
        lineCap: "circle",
        animate: 2000,
    });
});

if ( window.history.replaceState ) {
    window.history.replaceState( null, null, window.location.href );
};