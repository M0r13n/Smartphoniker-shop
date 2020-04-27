// Das ist das Hamburger Menu
document.getElementById("menu").addEventListener("click", function () {
    document.getElementById("nav").classList.toggle("header__list--in")
}, false)


// Das ist die Suche aus dem FAQ-Bereich
if (document.getElementById("HERO__SEARCH")) {
    document.getElementById("HERO__SEARCH").addEventListener("keyup", function() {filterFunction()}, false)
}
function filterFunction() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById("HERO__SEARCH");
    filter = input.value.toUpperCase();
    ul = document.getElementById("FAQ__LIST");
    h2 = ul.getElementsByClassName("faq__category")
    for (let j = 0; j < h2.length; j++) {
        h2[j].style.display = "none";
        if (input.value == "") {
            h2[j].style.display = "";
        }
    }
    li = ul.querySelectorAll("li.faq__item--search");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("span")[0];
        div = li[i].getElementsByTagName("div")[0];
        txtValue = a.textContent || a.innerText;
        txtValuediv = div.innerHTML;
        if ((txtValue.toUpperCase().indexOf(filter) > -1) || 
            (txtValuediv.toUpperCase().indexOf(filter) > -1)) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}