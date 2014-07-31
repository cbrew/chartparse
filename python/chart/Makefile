clean:
	rm -rf *.pyc html
test: chart.py english.py edges.py lattice.py features.py feature_tests.py
	nosetests  --with-doctest --with-coverage --cover-package=chart.py --cover-package=edges.py --cover-package=english.py --cover-package="lattice.py" --cover-package="features.py" --cover-package="feature_tests.py"