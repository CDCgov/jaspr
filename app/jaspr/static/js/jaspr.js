$(document).ready(function() {
  $("#pingTitle").html("Ping Value");return false;
});

var GetPing = function() {
  $.get('/ping', {}, function(response) {
    console.log("success");
    console.log(response);
    $("#pingValue").html(response);
    return false;
  });
};
