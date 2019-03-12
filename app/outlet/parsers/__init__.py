#!/usr/bin/env python
# file outlet/parsers/__init__.py

# python imports
import importlib
import pkgutil

# discover and dynamically import all modules in this subpackage
for module_name in [m[1] for m in pkgutil.iter_modules(__path__)]:
    importlib.import_module(f'outlet.parsers.{module_name}')
