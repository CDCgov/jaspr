REM This publishes the help documentation.  It uses pandoc from
REM https://pandoc.org to work correctly (although and MD parser will do)

pandoc authors.md -f markdown -t html -s -o ..\static\help\authors.html
pandoc changelog.md -f markdown -t html -s -o ..\static\help\changelog.html
pandoc data_format.md -f markdown -t html -s -o ..\static\help\data_format.html
pandoc fitting.md -f markdown -t html -s -o ..\static\help\fitting.html
pandoc index.md -f markdown -t html -s -o ..\static\help\index.html
pandoc install.md -f markdown -t html -s -o ..\static\help\install.html
pandoc jaspr_configuration.md -f markdown -t html -s -o ..\static\help\jaspr_configuration.html
pandoc license.md -f markdown -t html -s -o ..\static\help\license.html
cp "jaspr Software Agreement 2010.doc" ..\static\help
