# Contribution

Le projet est hébergé sur GitHub

[Visiter GitHub](https://github.com/3liz/QgisCadastrePlugin){: .md-button .md-button--primary }

## Code

[![🎳 Tests](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/ci.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/ci.yml)

La CI GitHub et GitLab lance le linter (`ruff`), l'analyse de sécurité (`bandit`) et les tests
avec QGIS 3.40, 3.44, 4.0 et 4.2. La CI GitHub vérifie aussi les types (`mypy`).

```bash
# Linter, analyse de sécurité et types
make lint scan typecheck

# Tests dans Docker, avec PostGIS, pour une version de QGIS (3.44 par défaut)
make docker-test QGIS_VERSION=4.2
```

La variable d'environnement `CI=true` permet d'éviter certaines QMessageBox.


## Documentation

[![📖 Documentation](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/publish-doc.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/publish-doc.yml)

La documentation utilise [MkDocs](https://www.mkdocs.org/) avec [Material](https://squidfunk.github.io/mkdocs-material/) :

```bash
pip install -r requirements/doc.txt
mkdocs serve
```
