window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};
function deleteCurrent(obj) {
  if (confirm("Are you sure?")) {
    fetch('/' + obj.getAttribute("name") + 's/' + obj.getAttribute("id"), {
      method: "DELETE",
      headers: new Headers({
        "Content-Type": "application/json"
      })
    })
    .then(async r => await r.json())
    .then((r) => {
      if (r.result) {
        window.location.href = '/';
      } else {
        window.location.href= "/artists/" + obj.getAttribute("id");
      }
    })
  }
}
