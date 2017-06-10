/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function toggle_responsive_class() {
    var x = document.getElementById("myTopnav");
    x.className === "topnav" ? x.className += " responsive" :  x.className = "topnav";
}
