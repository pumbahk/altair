from datetime import datetime
from wtforms import widgets
from altair.formhelpers.widgets import Switcher, GenericSerializerWidget

__all__ = (
    'ymd_widget',
    'radio_list_widget',
    'get_year_choices',
    'get_year_months',
    'get_year_days',
    )

ymd_widget = Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

radio_list_widget = Switcher(
    'list',
    list=widgets.ListWidget(prefix_label=False),
    plain=GenericSerializerWidget(prefix_label=False)
    )

def get_year_choices():
    current_year = datetime.now().year
    years =  [(str(year), year) for year in range(1920, current_year)]
    return years

def get_year_months():
    months =  [(str(month), month) for month in range(1,13)]
    return months

def get_year_days():
    days =  [(str(month), month) for month in range(1,32)]
    return days
