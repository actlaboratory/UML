build:
	scons
fmt:
	py -m autopep8 -r -i -a -a --ignore=E402,E721 --max-line-length 150 addon/
