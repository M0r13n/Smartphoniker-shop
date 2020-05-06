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
if (window.location.pathname == "/manufacturers") {
    document.getElementById("SEARCHBUTTON").addEventListener("click", function(){
        appendURL()
    }, false)
    document.getElementById("HERO__SEARCH--SEARCHDEVICE").addEventListener("keypress", function(e) {
        if (e.key == "Enter") {
            appendURL()
        }
    } ,false)
    function appendURL() {
        input = document.getElementById("HERO__SEARCH--SEARCHDEVICE")
        if (input.value.length == 0) return
        input = input.value.split(" ").join("+")
        alert(input)
        // window.location.href("?input=" + input)
        // redirect
    }
}

// To-Do: ich muss wissen, wie die Verlinkungen funktionieren
// Das ist um die Kreise in der Progressbar entsprechend zu füllen
if (window.location.pathname == "/manufacturer_grid" || window.location.pathname == "/series_grid" || window.location.pathname == "/device__grid") {
    query = window.location.search.substring(1).split("step=")[1];
    if (query.length == 1) {
        query = parseInt(query, 10)
        if (query > 1) {
            document.getElementById("STEP2").classList.toggle("progressbar__number--active")
        }
        if (query > 2) {
            document.getElementById("STEP3").classList.toggle("progressbar__number--active")
        }
    }
}