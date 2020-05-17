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
 * @param str
 * @returns {object}
 */
function $(id) {
    return document.getElementById(id);
};

/**
 * Search Funtion.
 * @param {string}
 */
function appendURL(path = '/search/') {
    const origin = window.location.origin;
    let url = new URLSearchParams(origin + path);
    let input = $('Search');
    if (input.value.length === 0) return;
    url.searchParams.append('search', input);
    window.location.href = url;
}

/**
 * Hide a given element by setting it's display attr to none.
 */
function hide(elem) {
    elem.style.display = 'none'
}

/**
 * Show a given element by setting it's display attr.
 */
function show(elem) {
    elem.style.display = '';
}

/**
 * Returns plain text in html object
 * @param object
 * @param string
 * @returns {string}
 */
const extractPlainText = (htmlObject, query = false) => {
    let toBeSearched = query ? htmlObject.querySelectorAll(query)[0] : htmlObject;
    return toBeSearched.textContent.toLowerCase() || toBeSearched.innerText.toLowerCase() || '';
}

/**
 * filters Questions and Answers on the FAQ Page
 */
function filterFunction() {
    const input = $('Search').value.toLowerCase();
    const questionHeadings = $('FaqList').getElementsByClassName('faq__subheading');

    let question;
    let answer;

    for (const heading of questionHeadings) {
        input.length > 0 ? hide(heading) : show(heading);
    }  

    let list = $('FaqList').querySelectorAll('li.faq__item');
    for (const item of list) {
        question = extractPlainText(item, 'span.faq__question');
        answer = extractPlainText(item, 'div.faq__answer');

        if ((question.indexOf(input) > -1) || (answer.indexOf(input) > -1)) {
            show(item);
        } else {
            hide(item);
        }
    }
}

/**
 * filters questions with user-input 
 */
const faqJS = () => {
    $('Search').addEventListener('keyup', () => {
        filterFunction()
    }, false);

    const params = getURLSearchParams(),
        questionID = toInt(params.get('q')),
        questions = $('FaqList').getElementsByClassName('faq__item'),
        questionTitles = $('FaqList').getElementsByTagName('h3');

    let i = 0;
    for (const question of questions) {
        i++;
        question.addEventListener('click', () => {
            question.classList.toggle('collapsed')
        }, false);

        if (questionID > 0) {
            hide(question);
        }
        if (questionID === i) {
            for (const title of questionTitles) {
                hide(title);
            }
            show(question);
            question.classList.toggle('collapsed');
        }
    }
};

/**
 * eventlisteners for device-search 
 */
const searchJS = () => {
    $('Submit').addEventListener('click', () => {
        appendURL()
    }, false);
    $('Search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            appendURL()
        }
    }, false);
};

/**
 * returns array of values of elements selected by a css query
 * @param {string}
 * @returns {Array}
 */
const getValues = (selector) => {
    var elements = document.querySelectorAll(selector);
    return [].map.call(elements, el => toInt(el.value));
}

/**
 * calculate total on modell.html 
 */
const totalJS = () => {
    const repairs = document.getElementsByName('repair');

    const calculateSum = () => {
        let checkedRepairPrices = getValues('input[name="repair"]:checked');

        if (checkedRepairPrices.length > 1) {
            let cheapest = Math.min(...checkedRepairPrices);
            let preDiscount = checkedRepairPrices.reduce((sum, x) => sum + x);
            let total = preDiscount - cheapest + (cheapest * 0.8);
            $('Total').innerHTML = '<s>' + toInt(preDiscount) + '</s> ' + toInt(total);
        } else {
            $('Total').innerHTML = checkedRepairPrices[0] ?? 0;
        }
    }
    
    for (const repair of repairs) {
        repair.addEventListener('change', () => {
            calculateSum()
        }, false);
    }
}

/**
 * register EventListeners for Colors on modell.html 
 */
const colorJS = () => {
    const radios = document.getElementsByName('color');

    for (const radio of radios) {
        if (radio.checked) {
            $('ColorName').innerHTML = 'Aktuelle Farbauswahl: ' + radio.id.replace('_', ' ')
        }
        radio.addEventListener('change', () => {
            if (radio.checked) {
                $('ColorName').innerHTML = 'Aktuelle Farbauswahl: ' + radio.id.replace('_', ' ')
            }
        }, false);
    }
}

const main = () => {
    /* mobile Navigation */
    $('menu').addEventListener('click', () => {
        $('nav').classList.toggle('header__list--in')
    }, false);

    /* I know that switch statements have bad stigma, 
     * but I think they have great readability & are more maintanable
     * and the default case makes sense here
     */
    switch (window.location.pathname) {
        case '/faq':
            faqJS();
            break;

        case '/shop':
        case '/search':
            searchJS();
            break;

        default:
            colorJS();
            totalJS();
            break;
    }
};


main();