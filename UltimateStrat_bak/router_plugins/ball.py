#!/usr/bin/python

import Router

# About Ball
# ---Getter
@Router.register_function
def getBallPosition():
    return Router.black_board['ball']['position']
