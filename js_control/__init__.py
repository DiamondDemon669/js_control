from .communication import *
from .primitives import *
from .utils import *
from .variable import *
from .errors import *

# Javascript wrapper for python
# Written by DiamondDemon669
# This wrapper uses a tampermonkey/greasemonkey websocket to connect to the browser
# Designed to be compatible with as many browsers as possible
# If you want to adapt for selenium or anything else like brotab, create a class inheriting from javascript.communication.BaseTab
# If you are adding a different communication method, include all methods in the tab class using @staticmethod

from . import utils
utils.Variable = Variable
# To avoid circular import in variable/utils

