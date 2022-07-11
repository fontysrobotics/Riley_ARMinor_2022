function openModal() {
    // Get the modal
    var modal = document.getElementById("modal");

    // Get the image and insert it inside the modal - use its "alt" text as a caption
    var img = document.getElementById("image");
    var modalImg = document.getElementById("modalImage");
    var captionText = document.getElementById("caption");

    modal.style.display = "block";
    modalImg.src = this.src;
    captionText.innerHTML = this.alt;

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    modal.style.display = "none";

}