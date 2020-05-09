/**
 * Return URLSearchParams object for the current URL.
 * @returns {URLSearchParams}
 */
function getURLSearchParams() {
    const paramsString = window.location.search;
    return new URLSearchParams(paramsString);
}

/**
 * Type safe conversion from string to (positive) integer.
 * Returns -1 on error.
 * @param str
 * @returns {number}
 */
const toInt = (str) => {
    if (str === null || isNaN(str)) {
        return -1;
    } else {
        return parseInt(str);
    }
};

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
 * Hide a given element by setting it's display attr to none.
 */
function hide(elem) {
    elem.style.display = "none"
}

/**
 * Show a given element by setting it's display attr.
 */
function show(elem) {
    elem.style.display = "";
}

/**
 * WTF is this mess?
 * TODO: This method is way to complex and unreadable. Rewrite it.
 */
function filterFunction() {
    const input = document.getElementById("Search"),
        filter = input.value.toUpperCase(),
        questionList = document.getElementById("FaqList"),
        questionHeadings = questionList.getElementsByClassName("faq__subheading");

    let li, a, txtValue, div, txtValuediv;

    for (const heading of questionHeadings) {
        input.value.length > 0 ? hide(heading) : show(heading);
    }

    li = questionList.querySelectorAll("li.faq__item");
    li.forEach((l) => {
        a = l.getElementsByTagName("span")[0];
        div = l.getElementsByTagName("div")[0];
        txtValue = a.textContent || a.innerText;
        txtValuediv = div.innerHTML;
        if ((txtValue.toUpperCase().indexOf(filter) > -1) ||
            (txtValuediv.toUpperCase().indexOf(filter) > -1)) {
            show(l);
        } else {
            hide(l);
        }
    });
}

const radioJS = () => {
    const radios = document.getElementsByName('color');
    document.getElementById("menu").addEventListener("click", () => {
        document.getElementById("nav").classList.toggle("header__list--in")
    }, false);

    for (const radio of radios) {
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

const faqJS = () => {
    document.getElementById("Search").addEventListener("keyup", () => {
        filterFunction()
    }, false);

    const params = getURLSearchParams(),
        questionID = toInt(params.get('q')),
        questions = document.getElementById("FaqList").getElementsByClassName("faq__item"),
        questionTitles = document.getElementById("FaqList").getElementsByTagName("h3");

    let i = 0;
    for (const question of questions) {
        i++;
        question.addEventListener("click", () => {
            question.classList.toggle("collapsed")
        }, false);

        if (questionID > 0) {
            hide(question);
        }
        if (questionID === i) {
            for (const title of questionTitles) {
                hide(title);
            }
            show(question);
            question.classList.toggle("collapsed");
        }
    }
};

const searchJS = () => {
    document.getElementById("Submit").addEventListener("click", () => {
        appendURL()
    }, false);
    document.getElementById("Search").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            appendURL()
        }
    }, false);
};

/* Register event listeners */
radioJS();

if (window.location.pathname === "/faq") {
    faqJS();
} else if (window.location.pathname === "/manufacturers") {
    searchJS();
}


