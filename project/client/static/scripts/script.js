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
 * @returns {object} HTML-DOM-Reference
 */
function $(id) {
    return document.getElementById(id);
};

/**
 * Shorthand for document.querySelectorAll()
 * @param str
 * @returns {NodeList} Liste mit passenden Elementen
 */
function byQuery(query) {
    return document.querySelectorAll(query);
}

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
 * second argument allows specifying the display attribute
 * @param {object}
 * @param {string}
 */
function show(elem, display = false) {
    if (display) {
        elem.style.display = display;
        return;
    }
    elem.style.display = '';
}

/**
 * Returns plain text in html object
 * @param object
 * @param string
 * @returns {string}
 */
const extractPlainText = (htmlObject, query = false) => {
    const toBeSearched = query ? htmlObject.querySelectorAll(query)[0] : htmlObject;
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
const getPrices = (selector) => {
    const elements = byQuery(selector);
    return [].map.call(elements, el => toInt(el.getAttribute('data-price')));
}

/**
 * calculate total on modell.html 
 */
const totalJS = () => {
    const repairs = document.getElementsByName('repairs');

    const calculateSum = () => {
        let checkedRepairPrices = getPrices('input[name="repairs"]:checked');

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
/**
 * checks every input with given name, shows error message and 
 * returns array of bools with the result
 * @param {Array} names input names which should be tested
 * @returns {Array} with a bool for each name
 */
const selectionValidation = (names) => {
    const validated = [];

    for (name of names) {
        let checked = true;
        // checks if at least one of inputs with given name is checked
        const checkedInputs = byQuery('input[name=' + name + ']:checked');
        if (checkedInputs.length === 0) {
            checked = false;
        }
        
        // shows individual error message
        if (!checked) {
            show($(name), 'block');
        } else {
            hide($(name));
        }

        // pushes to array
        validated.push(checked);
    }
    return validated;
}

/**
 * validates the form on the modell page
 */
const modellFormJS = () => {
    $('SubmitModell').addEventListener('click', (evt) => {
        const okay = [];
        okay.push(...selectionValidation(['color', 'repairs']));
        
        // prevent form from sending + show top error message
        if (okay.includes(false)) {
            show($('Error0'), 'block');
            evt.preventDefault();
        }
    } ,true);
}

/**
 * calls the right formvalidation
 * @param {string} form id of the submitbutton
 */
const validateForms = (form) => {
    switch (form) {
        case 'Modell':
            if($('SubmitModell')) {
                modellFormJS();
            }
            break;
        default:
            break;
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
            validateForms('Modell');
            break;
    }
};


// run script
main();