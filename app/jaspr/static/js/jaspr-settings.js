$(function() {
  $("#showCurve").click(function() {
    var selected = $('#showCurve').prop('checked');
    if (selected) {
      alert("curve will be shown");
    } else {
      alert("curve will not be shown");
    }
  });

  $("#axisScaleSelect > .btn").click(function() {
    num = this.control.id
    alert("Axis selected is " + num );
  });

  // handles selections on a bootstrap dropdown list
  $('.dropdown-menu').click(function(e){
      alert(" Algorithm selected is " + e.target.innerText );
  });

});

var GetPing = function() {
  $.getJSON('/ping', function(data) {
    $("#pingValue").text(data);
    $("#pingTitle").css("display", "block");
  });
};
