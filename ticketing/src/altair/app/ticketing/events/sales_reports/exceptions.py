# -*- coding: utf-8 -*-

class ReportSettingValidationError(Exception):
    form = None

    def __init__(self, form):
        self.form = form
