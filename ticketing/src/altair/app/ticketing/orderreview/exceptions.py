class InvalidForm(Exception):
    def __init__(self, form, errors=[]):
        self.form = form
        self.errors = errors


