doc: chart.py english.py
	(cd docs; make html)
clean:
	rm -rf *.pyc html
test: chart.py english.py
	nosetests  --with-doctest --with-coverage chart.py english.py