$(document).ready(function () {
    $.ajax({
        dataType: "json",
        url: '/api/hosts/',
        success: function (data) {
            $(data).each( function (host) {
                $('#dash-proces').append(
                    "<p>" + host['name'] + "</p>"
                );
            });
        }
    })
})
