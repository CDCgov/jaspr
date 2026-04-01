$(function() {
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
  $('#graph-target').empty().html('<div>loading graph...</div>');
  $('#table-target').empty().html('<div>loading table...</div>');

  $.ajax({
    dataType: 'json',
    url: '/drawWidgetHTML',
    success: function(data) {
      $('#graph-target').empty();
      Bokeh.embed.embed_item(data.graph, 'graph-target');
      $('#table-target').html(data.t_html);
    },
    error: function() {
      $('#graph-target').html('<div class="alert alert-danger">Graph failed to load.</div>');
      $('#table-target').html('<div class="alert alert-danger">Table failed to load.</div>');
    }
  });
};
