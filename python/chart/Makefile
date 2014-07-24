clean:
	rm -rf *.pyc html
test: chart.py english.py
	nosetests  --with-doctest --with-coverage --cover-package=chart.py --cover-package=english.py --cover-package="lattice.py" --cover-package="features.py" --cover-package="feature_tests.py"