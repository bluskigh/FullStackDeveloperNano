const restrictionCheckbox = document.querySelector("#availability_restriction"); 
const revealRestriction = (obj) => {
  obj.nextElementSibling.classList.toggle('hidden');
}
restrictionCheckbox && restrictionCheckbox.addEventListener("change", function() {
  revealRestriction(this);
});
