// -----------------------------------------------
// -----------------  Header  --------------------
// -----------------------------------------------
document.getElementById("menu").addEventListener("click", function () {
    document.getElementById("nav").classList.toggle("header__list--in")
}, false)


// -----------------------------------------------
// -----------------   FAQ    --------------------
// -----------------------------------------------
if (window.location.pathname == "/faq") {
    // Suchleiste
    document.getElementById("Search").addEventListener("keyup", function() {
        filterFunction()
    }, false)

    // URL Queries verarbeiten
    var query = window.location.search.substring(1)
    questionID = query.split("q=")[1]
    
    // Eventlistener an FAQ Fragen appenden und ausführen, wenn entsprechende Queries in URL sind
    e = document.getElementById("FaqList").getElementsByClassName("faq__item")
    for (let i = 0; i < e.length; i++) {
        e[i].addEventListener("click", function() {
            e[i].classList.toggle("collapsed")
        }, false)

        if(!isNaN(questionID) && parseInt(questionID) >= 0 && parseInt(questionID) < e.length) {
            e[i].style.display = "none"
            f = document.getElementById("FaqList").getElementsByTagName("h3")
            for (let j = 0; j < f.length; j++) {
                f[j].style.display = "none"
            }
            if(questionID == i) {
                e[i].style.display = ""
                e[i].classList.toggle("collapsed")
            }
        }
        
    }
    // Funktion die Texte und Überschriften nach den eingegebenen Wörtern untersucht
    function filterFunction() {
        var input, filter, ul, li, a, i, txtValue;
        input = document.getElementById("Search");
        filter = input.value.toUpperCase();
        ul = document.getElementById("FaqList");
        h3 = ul.getElementsByClassName("faq__subheading")
        console.log(h3)
        for (let j = 0; j < h3.length; j++) {
            h3[j].style.display = "none";
            if (input.value == "") {
                h3[j].style.display = "";
            }
        }
        li = ul.querySelectorAll("li.faq__item");
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
}



// Das ist die Suche für Geräte aus dem Shop-Bereich
if (window.location.pathname == "/manufacturers" || window.location.pathname.substring(0, 7) == "/search") {
    console.log('mau')
    document.getElementById("Submit").addEventListener("click", function(){
        appendURL()
    }, false)
    document.getElementById("Search").addEventListener("keypress", function(e) {
        if (e.key == "Enter") {
            appendURL()
        }
    } ,false)
    function appendURL() {
        input = document.getElementById("Search")
        if (input.value.length == 0) return
        input = input.value.split(" ").join("$")
        window.location.href= "/search/" + input + "/"
    }
}



var radios = document.getElementsByName('color')
for (var i = 0, length = radios.length; i < length; i++) {
    if (radios[i].checked) {
        document.getElementById("ColorName").innerHTML = "Aktuelle Farbauswahl: " + radios[i].value.replace("_", " ")
    }
    radios[i].addEventListener("change", function() {
        if (this.checked) {
            document.getElementById("ColorName").innerHTML = "Aktuelle Farbauswahl: " + this.value.replace("_", " ")
        }
    }, false)
}