$(function() {
  //TODO: move to main.js or something like that
  //this isn't good for all pages, but put it here to get started
  $(".dataGraph").html("<div>loading graph.</div>");
  $(".dataTable").html("<div>loading table.</div>");
  $(".FRNTdataGraph").html("<div>loading FRNT graph.</div>");
  loadGraph();
});

var ChangeSample = function(sampleName) {
  $.ajax({
    type: 'POST',
    xhrFields: {
      withCredentials: true
    },
    url: '/changeSample/' + encodeURIComponent(sampleName)
      .replace(/\(/g, "%28").replace(/\)/g, "%29"),
    success: function() {
      loadGraph();
    }
  });
}

var ChangeExperiment = function(selectedItem) {
  $.ajax({
    type: 'POST',
    xhrFields: {
      withCredentials: true
    },
    url: '/changeExperiment/' + encodeURIComponent(selectedItem.value)
      .replace(/\(/g, "%28").replace(/\)/g, "%29"),
    success: function() {
      //the sample got set to th first one in the sampleList
      $("ul.samplelist").find("a.nav-link").removeClass("active");
      $("ul.samplelist li a.nav-link").first().addClass("active");
      loadGraph();
    }
  });
}


var loadGraph = function() {
  $(".dataGraph").html("loading graph...");
  $(".dataTable").html("loading table...");
  $(".FRNTdataGraph").html("loading graph...");

  $.ajax({
    dataType: 'json',
    url: '/drawWidgetHTML',
    success: function(data) {
      $(".dataGraph").replaceWith('<span class="dataGraph">' + data.g_div +
        '</span>');
      $(".dataTable").replaceWith('<span class="dataTable">' + data.t_div +
        '</span>');
      $(".FRNTdataGraph").replaceWith('<span class="FRNTdataGraph">' + data.FRNT_div +
        '</span>');
      $(data.g_script).appendTo(".dataGraph");
      $(data.t_script).appendTo(".dataTable");
      $(data.FRNT_script).appendTo(".FRNTdataGraph");
    }
  });
};
