const artist_input = document.querySelector("#artist_id");
const start_input = document.querySelector("#start_time");
const venue_input = document.querySelector("#venue_id");
const create_button = document.querySelector("#create_show"); 

// 0 = artist_input, 1 = start_input, 2 = venue_input
var inputs_valid = [false, false, false];

// on load turn of the button
create_button ? create_button.disabled = true : null;

const assignTimes = (obj, first, second, warning) => {
    obj.nextElementSibling.querySelector("#from_time").innerText = first;
    obj.nextElementSibling.querySelector("#to_time").innerText = second;
    obj.nextElementSibling.querySelector("#warning").innerText = warning;
}

const appearValid = (obj, who) => {
  obj.style.border = "1px solid green";
  inputs_valid[who] = true;
}
const appearWrong = (obj, who) => {
  obj.style.border = "1px solid red";
  if (inputs_valid[who]) {
    inputs_valid[who] = false;
    create_button.disabled = true;
  }
}

artist_input && artist_input.addEventListener("focusout", function() {
  // make an ajax request to the server checking if the entered artist id is available
  this.nextElementSibling.classList.remove("hidden");
  if (this.value.length > 0) {
    fetch('/artists/' + artist_input.value + '/get_availability')
    .then(async r => await r.json())
    .then((r) => {
      if (r.exist) {
        if (r.available) {
          appearValid(this, 0);
          if (r.restriction) {
            assignTimes(this, "From: " + r.from_time, "To: " + r.to_time, "");
          } else {
            assignTimes(this, "", "", "Available whenever!");
          }
          if (inputs_valid[1] && inputs_valid[2]) {
            create_button.disabled = false;
          }
        } else {
          console.log("was not available");
          appearWrong(this, 0);
          assignTimes(this, "", "", "Artist(" + r.id + ") is not available for booking.");
        }
      } else {
        assignTimes(this, "", "", "An artist with the id of " + r.id + " does not exist.");
        appearWrong(this, 0);
      }
    })
    .catch((e) => {console.error(e)})
  }
});

venue_input && venue_input.addEventListener("focusout", async function() {
  this.nextElementSibling.classList.remove("hidden");
  if (this.value.length > 0) {
    // could check if its a number, but for this project... not going to.
    var r = await fetch("/venues/" + venue_input.value + "/exist");
    r = await r.json();
    if (r.exist) {
      this.nextElementSibling.querySelector("#warning").innerText = "";
      appearValid(this, 1);
      if (inputs_valid[0] && inputs_valid[2]) {
        create_button.disabled = false;
      }
    } else {
      this.nextElementSibling.querySelector("#warning").innerText = "A venue with the id of " +  r.id + " does no exist.";
      appearWrong(this, 1);
    }
  }
});

start_input && start_input.addEventListener("focusout", async function() {
  this.nextElementSibling.classList.remove("hidden");
  if (inputs_valid[0]) {
    var r = await fetch("/artists/" + artist_input.value + "/available", {
      method: "POST",
      body: JSON.stringify({"start_time": this.value}),
      headers: new Headers({"Content-Type": "application/json"})
    });
    r = await r.json();
    if (r.valid) {
      appearValid(this, 2);
      this.nextElementSibling.querySelector("#warning").innerText = null;
      if (inputs_valid[0] && inputs_valid[1]) {
        create_button.disabled = false;
      }
    } else {
      appearWrong(this, 2);
      this.nextElementSibling.querySelector("#warning").innerText = r.choosen_time + " does not meet artist(" + r.id + ") availability schedule.";
    }
  } else {
    appearWrong(this, 2);
  }
});

/*
 * I would have done a check on submission, but when I do form.submit() the generated value flaskwtf inputs values are not saved. 
 */
