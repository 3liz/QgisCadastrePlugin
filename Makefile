github-pages:
	@docker run --rm -w /plugin -v $(shell pwd):/plugin 3liz/pymarkdown:latest docs/index.md docs/index.html