$(function() {
  $("#showCurve").click(function() {
    var selected = $('#showCurve').prop('checked');
    $.post("/updateConfigSetting", {
        show_fit: selected
      });
  });

  $("#blankCorrection").click(function() {
    var selected = $('#blankCorrection').prop('checked');
    $.post("/updateConfigSetting", {
        blank_correction: selected
      });
  });

  $("#axisScaleSelect > .btn").click(function() {
    axisScale = this.control.id
    $.post("/updateConfigSetting", {
        x_axis_type: axisScale
      });
  });

  // handles selections on a bootstrap dropdown list
  $('.dropdown-menu').click(function(e) {
    $("#dropdownMenuButton").text(e.target.innerText)
    $.post("/updateConfigSetting",{
        curr_function: e.target.innerText
    });
  });

});

var GetPing = function() {
  $.getJSON('/ping', function(data) {
    $("#pingValue").text(data);
    $("#pingTitle").css("display", "block");
  });
};
