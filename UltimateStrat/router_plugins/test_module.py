#!/usr/bin/python

import Router

lolstring = "lol"
@Router.register_function
def printlollol():
    print(lolstring*2)
