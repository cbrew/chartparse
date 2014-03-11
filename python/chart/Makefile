doc: chart.py english.py
	(cd docs; make html)
clean:
	rm -rf *.pyc html
test: chart.py english.py
	nosetests  --with-doctest --with-coverage --cover-package=chart.py --cover-package=english.py