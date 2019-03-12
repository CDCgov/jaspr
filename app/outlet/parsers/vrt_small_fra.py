#!/usr/bin/env python

from outlet import ParserRegistry


class SmallFraParser(ParserRegistry):
    name = 'small_fra'
    description = 'Small-format FRA parser'

    

    def __call__(self):
        return {}
