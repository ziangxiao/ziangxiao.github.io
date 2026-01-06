var scripts = document.getElementsByTagName('script');
var myScript = scripts[scripts.length - 1];

var queryString = myScript.src.replace(/^[^\?]+\??/, '');

var params = parseQuery(queryString);

var recruit = 0;

function parseQuery(query) {
    var Params = {};
    if (!query) return Params; // return empty object
    var Pairs = query.split(/[;&]/);
    for (var i = 0; i < Pairs.length; i++) {
        var KeyVal = Pairs[i].split('=');
        if (!KeyVal || KeyVal.length != 2) continue;
        var key = unescape(KeyVal[0]);
        var val = unescape(KeyVal[1]);
        val = val.replace(/\+/g, ' ');
        Params[key] = val;
    }
    return Params;
}

function showPubs(id) {
  const legend = document.getElementById('legend');
  if (id == 0) {
    document.getElementById('pubs').innerHTML = document.getElementById('pubs_selected').innerHTML;
    document.getElementById('select0').style = 'text-decoration:underline;color:#000000';
    document.getElementById('select1').style = '';
    document.getElementById('select2').style = '';
    if (legend) legend.style.marginBottom = '1em';
  } else if (id == 1) {
    document.getElementById('pubs').innerHTML = document.getElementById('pubs_by_date').innerHTML;
    document.getElementById('select1').style = 'text-decoration:underline;color:#000000';
    document.getElementById('select0').style = '';
    document.getElementById('select2').style = '';
    if (legend) legend.style.marginBottom = '0.5em';
  } else {
    document.getElementById('pubs').innerHTML = document.getElementById('pubs_by_topic').innerHTML;
    document.getElementById('select2').style = 'text-decoration:underline;color:#000000';
    document.getElementById('select0').style = '';
    document.getElementById('select1').style = '';
    if (legend) legend.style.marginBottom = '0.5em';
  }
}


