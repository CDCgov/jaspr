$(document).ready(function() {
  $("#pingTitle").html("Ping Value");return false;
});

var GetPing = function() {
  $.AJAX('/ping', {}, function(response) {
    $("#pingValue").html(response);
    return false;
  });
};
