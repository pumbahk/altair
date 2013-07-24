.. contents::

Introduction
============

from altair.browserid import browser

def view(request):
    return "browserid = %s" % browser.id
