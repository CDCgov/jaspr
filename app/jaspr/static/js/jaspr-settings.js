$(function() {
  $("#showCurve").click(function() {
    var selected = $('#showCurve').prop('checked');
    $.post("/updateConfigSetting", {
        showCurveFit: selected
      });
  });

  $("#blankCorrection").click(function() {
    var selected = $('#blankCorrection').prop('checked');
    $.post("/updateConfigSetting", {
        blankCorrection: selected
      });
  });

  $("#axisScaleSelect > .btn").click(function() {
    axisScale = this.control.id
    $.post("/updateConfigSetting", {
        axisScale: axisScale
      });
  });

  // handles selections on a bootstrap dropdown list
  $('.dropdown-menu').click(function(e) {
    $("#dropdownMenuButton").text(e.target.innerText)
    $.post("/updateConfigSetting",{
        selectedAlgorithm:e.target.innerText
    });
  });

});

var GetPing = function() {
  $.getJSON('/ping', function(data) {
    $("#pingValue").text(data);
    $("#pingTitle").css("display", "block");
  });
};
