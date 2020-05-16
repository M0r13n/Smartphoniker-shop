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
 * Shorthand for document.getElementById()
 * 
 * @param str
 * @returns {object}
 */
function $(id) {
    return document.getElementById(id);
};

/**
 * Search Funtion.
 *
 * TODO: For stuff like this it is nicer to use a URL query string instead of an url.
 */
function appendURL() {
    const origin = window.location.origin;
    let url = new URLSearchParams(origin + "/search/");
    let input = $("Search");
    if (input.value.length === 0) return;
    url.searchParams.append("search", input);
    window.location.href = url;
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
 * Returns plain text in html object
 * 
 * @param object
 * @param string
 * 
 * @returns {string}
 */
const extractPlainText = (htmlObject, query = false) => {
    let toBeSearched = query ? htmlObject.querySelectorAll(query)[0] : htmlObject;
    return toBeSearched.textContent.toLowerCase() || toBeSearched.innerText.toLowerCase() || "";
}

/**
 * WTF is this mess? I don't know either...
 * 
 */
function filterFunction() {
    const input = $("Search").value.toLowerCase();
    const questionHeadings = $("FaqList").getElementsByClassName("faq__subheading");

    let question;
    let answer;

    for (const heading of questionHeadings) {
        input.length > 0 ? hide(heading) : show(heading);
    }  

    let list = $("FaqList").querySelectorAll("li.faq__item");
    for (const item of list) {
        question = extractPlainText(item, "span.faq__question");
        answer = extractPlainText(item, "div.faq__answer");

        if ((question.indexOf(input) > -1) || (answer.indexOf(input) > -1)) {
            show(item);
        } else {
            hide(item);
        }
    }
}

const radioJS = () => {
    const radios = document.getElementsByName('color');
    $("menu").addEventListener("click", () => {
        $("nav").classList.toggle("header__list--in")
    }, false);

    for (const radio of radios) {
        if (radio.checked) {
            $("ColorName").innerHTML = "Aktuelle Farbauswahl: " + radio.value.replace("_", " ")
        }
        radio.addEventListener("change", () => {
            if (this.checked) {
                $("ColorName").innerHTML = "Aktuelle Farbauswahl: " + this.value.replace("_", " ")
            }
        }, false)

    }
};

const faqJS = () => {
    $("Search").addEventListener("keyup", () => {
        filterFunction()
    }, false);

    const params = getURLSearchParams(),
        questionID = toInt(params.get('q')),
        questions = $("FaqList").getElementsByClassName("faq__item"),
        questionTitles = $("FaqList").getElementsByTagName("h3");

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
    $("Submit").addEventListener("click", () => {
        appendURL()
    }, false);
    $("Search").addEventListener("keypress", (e) => {
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


