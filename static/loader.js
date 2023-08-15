// window loading function
window.addEventListener("load", () =>{
    const loader = document.querySelector(".loader");
    loader.classList.add("loader-hidden");

    loader.addEventListener('transitionend', () =>{
        document.body.removeChild("loader");
    })
})

// button loading
document.addEventListener("DOMContentLoaded", function () {
    // Hide the div when the window is loaded
    var hiddenDiv = document.getElementById("info-loading");
    hiddenDiv.style.display = "none";
    
    // Attach click event to the button
    var toggleButtons = document.querySelectorAll(".loadonclick");
    toggleButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            // Toggle the visibility of the corresponding hidden div
            if (hiddenDiv.style.display === "none") {
                hiddenDiv.style.display = "block";
            } else {
                hiddenDiv.style.display = "none";
            }
        });
    });
});





