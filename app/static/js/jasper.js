$(document).ready(function() {
  //setupDemoGrid();
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

var setupDemoGrid = function(sampleData) {

  $("#jsGrid").jsGrid({
    width: "100%",
    height: "400px",

    inserting: false,
    editing: false,
    sorting: true,
    paging: true,

    data: sampleData,

    fields: [{
      name: "Sample",
      type: "text",
      width: 150,
      validate: "required"
    }, {
      name: "Date",
      type: "date",
      width: 150
    }, {
      name: "Result",
      type: "number",
      width: 50
    }, {
      name: "Comments",
      type: "text",
      width: 100
    }, {
      name: "IncludeInGraph",
      type: "checkbox",
      title: "Include",
      sorting: false
    }, ]

  });
}
