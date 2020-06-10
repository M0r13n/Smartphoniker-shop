all: minify

minify: minify-css minify-js

minify-js:
	curl -X POST -s --data-urlencode 'input@project/client/static/scripts/script.js' https://javascript-minifier.com/raw > project/client/static/scripts/script.min.js

minify-css:
	curl -X POST -s --data-urlencode 'input@project/client/static/css/main.css' https://cssminifier.com/raw > project/client/static/css/main.min.css

test:
	python manage.py test && python manage.py flake