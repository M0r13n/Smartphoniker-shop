/* Constants */
const radios = document.getElementsByName('color');


/* Global Functions */
/**
 * Return URLSearchParams object for the current URL.
 * @returns {URLSearchParams}
 */
function getURLSearchParams() {
    const paramsString = window.location.search;
    return new URLSearchParams(paramsString);
}


/**
 * Search Funtion.
 *
 * TODO: For stuff like this it is nicer to use a URL query string instead of an url.
 */
function appendURL() {
    let input = document.getElementById("Search");
    if (input.value.length === 0) return;
    input = input.value.split(" ").join("$");
    window.location.href = "/search/" + input + "/"
}

/**
 * TODO: This method is way to complex and unreadable. Rewrite it.
 */
function filterFunction() {
    const input = document.getElementById("Search"),
        filter = input.value.toUpperCase(),
        questionList = document.getElementById("FaqList"),
        questionHeadings = questionList.getElementsByClassName("faq__subheading");

    let li, a, txtValue, div, txtValuediv;

    for (const heading of questionHeadings) {
        heading.style.display = "none";
        if (input.value === "") {
            heading.style.display = "";
        }
    }

    li = questionList.querySelectorAll("li.faq__item");
    li.forEach((l) => {

        a = l.getElementsByTagName("span")[0];
        div = l.getElementsByTagName("div")[0];
        txtValue = a.textContent || a.innerText;
        txtValuediv = div.innerHTML;
        if ((txtValue.toUpperCase().indexOf(filter) > -1) ||
            (txtValuediv.toUpperCase().indexOf(filter) > -1)) {
            l.style.display = "";
        } else {
            l.style.display = "none";
        }
    });
}

/* JS for each page */
const radioJS = () => {
    document.getElementById("menu").addEventListener("click", () => {
        document.getElementById("nav").classList.toggle("header__list--in")
    }, false);
};

const faqJS = () => {
    // Suchleiste
    document.getElementById("Search").addEventListener("keyup", () => {
        filterFunction()
    }, false);

    // URL Queries verarbeiten
    const params = getURLSearchParams(),
        questionID = params.get('q');

    // Eventlistener an FAQ Fragen appenden und ausführen, wenn entsprechende Queries in URL sind
    const questions = document.getElementById("FaqList").getElementsByClassName("faq__item");
    let i = 0;
    for (const question of questions) {
        i++;
        question.addEventListener("click", () => {
            question.classList.toggle("collapsed")
        }, false);

        if (!isNaN(questionID) && parseInt(questionID) >= 0 && parseInt(questionID) < questions.length) {
            question.style.display = "none";
            const questionTitles = document.getElementById("FaqList").getElementsByTagName("h3");
            questionTitles.forEach((title) => {
                title.style.display = "none";
            });
            if (questionID === i.toString()) {
                question.style.display = "";
                question.classList.toggle("collapsed")
            }
        }
    }
};

const searchJS = () => {
    if (window.location.pathname === "/manufacturers" || window.location.pathname.substring(0, 7) === "/search") {
        document.getElementById("Submit").addEventListener("click", () => {
            appendURL()
        }, false);
        document.getElementById("Search").addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                appendURL()
            }
        }, false);
    }
    for (let radio of radios) {
        if (radio.checked) {
            document.getElementById("ColorName").innerHTML = "Aktuelle Farbauswahl: " + radio.value.replace("_", " ")
        }
        radio.addEventListener("change", () => {
            if (this.checked) {
                document.getElementById("ColorName").innerHTML = "Aktuelle Farbauswahl: " + this.value.replace("_", " ")
            }
        }, false)
    }
};

/* Register event listeners */
radioJS();

if (window.location.pathname === "/faq") {
    faqJS();
} else if (window.location.pathname === "/manufacturers" || window.location.pathname.substring(0, 7) === "/search") {
    searchJS();
}


