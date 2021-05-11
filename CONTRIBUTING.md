# Contribution

Le projet est hébergé sur GitHub

[Visiter GitHub](https://github.com/3liz/QgisCadastrePlugin){: .md-button .md-button--primary }

## Code

Les tests unitaires sont en cours.

[![❄ Flake8](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-lint.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-lint.yml)
[![🎳 Tests](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-python.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-python.yml)

```bash
pip install -r requirements/dev.txt
flake8
```

* Run tests in Docker

```bash
make start_tests
make run_tests
# Run a custom pattern
cd .docker/ && ./exec_tests.sh test_*.py
make stop_tests

# All in one, but slower
make tests
```

* In your QGIS Desktop itself
  * Open the QGIS console

```python
from qgis.utils import plugins
plugins['cadastre'].run_tests()

# Custom pattern
plugins['cadastre'].run_tests('test_*.py')
```

* In your IDE, with linked QGIS library
    * Setup your `QGIS_PREFIX_PATH` etc
    * Right click on a test and launch it


## Documentation

[![📖 Documentation](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/publish-doc.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/publish-doc.yml)

La documentation utilise [MkDocs](https://www.mkdocs.org/) avec [Material](https://squidfunk.github.io/mkdocs-material/) :

```bash
pip install -r requirements/doc.txt
mkdocs serve
```
