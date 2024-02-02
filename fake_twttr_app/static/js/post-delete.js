function postStuff(e, ev) {
  var xhttp = new XMLHttpRequest();
  var p = String(e.id) + '-counter';
  xhttp.open("POST", e.ariaDescription, true);
  xhttp.send();
  xhttp.onreadystatechange=function()
  {
        if (xhttp.readyState==4 && xhttp.status==201)
        {
          var pe = document.getElementById(p)
          ev.stopPropagation();
          e.innerHTML = [e.value, e.value = e.innerHTML][0];
          e.onclick = function() {deleteStuff(this, event)};
          pe.innerHTML = Number(pe.innerHTML) + 1
                  }
  }
};
function deleteStuff(e, ev) {
  var xhttp = new XMLHttpRequest();
  var p = String(e.id) + "-counter";
  xhttp.open("DELETE", e.ariaDescription, true);
  xhttp.send();
  xhttp.onreadystatechange=function()
  {
        if (xhttp.readyState==4 && xhttp.status==201)
        {
          var pe = document.getElementById(p)
          ev.stopPropagation();
          e.innerHTML = [e.value, e.value = e.innerHTML][0];
          e.onclick = function() {postStuff(this, event)};
          pe.innerHTML = Number(pe.innerHTML) - 1
        }
  }
}