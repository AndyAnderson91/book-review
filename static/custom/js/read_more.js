function myFunction(id) {
  let dots = document.getElementById(`dots${id}`);
  let moreText = document.getElementById(`more${id}`);
  let btnText = document.getElementById(`myBtn${id}`);

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btnText.innerHTML = "Read more";
    moreText.style.display = "none";
  } else {
    dots.style.display = "none";
    btnText.innerHTML = "Read less";
    moreText.style.display = "inline";
  }
}
