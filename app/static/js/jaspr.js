$(document).ready(function() {

});

var app = new Vue({
  el: '#title',
  data: {
    message: 'Ping Testing Value'
  }
});

var GetPing = function() {
  $.get('/ping', {}, function(response){
       console.log("success");
       console.log(response);
       $("#pingValue").html(response);
  });
};

}
