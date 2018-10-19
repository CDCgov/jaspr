var GetPing = function() {
  $.getJSON('/ping', {}, function(data) {
      $("#pingValue").text(data);
  });
};

var loadGraph = function() {
  $(".dataGraph").html("loading graph...");
  $.getJSON('/graphHTML',function(data) {
    $(".dataGraph").html(data.g_div);
    });
};
