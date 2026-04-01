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
      try {
        $('#graph-target').empty();
        console.log('Received graph data:', data.graph);
        if (data.graph && typeof Bokeh !== 'undefined' && Bokeh.embed && Bokeh.embed.embed_item) {
          data.graph.target_id = 'graph-target';
          const targetEl = document.getElementById('graph-target');
          Bokeh.embed.embed_item(data.graph, targetEl)
            .catch(function(err) {
              console.error('Bokeh embed error:', err);
              $('#graph-target').html('<div class="alert alert-danger">Graph render error: ' + err + '</div>');
            });
        } else {
          console.error('Missing Bokeh or graph data');
          $('#graph-target').html('<div class="alert alert-danger">Bokeh not loaded.</div>');
        }
        $('#table-target').html(data.t_html || '');
      } catch(e) {
        console.error('Graph error:', e);
        $('#graph-target').html('<div class="alert alert-danger">Error: ' + e.message + '</div>');
      }
    },
    error: function(xhr, status, err) {
      $('#graph-target').html('<div class="alert alert-danger">Load failed: ' + err + '</div>');
      $('#table-target').html('<div class="alert alert-danger">Load failed.</div>');
    }
  });
};
