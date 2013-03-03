from ..rowspanlib import RowSpanGrid

## ticket grid
def seattype_for_grid(data, k, changed):
    if changed:
        return data.seattype or u"--"

def data_for_grid(data, k, changed):
    return data
TicketGrid = RowSpanGrid()
TicketGrid.register("seattype", mapping=seattype_for_grid, keyfn=lambda ticket: ticket.seattype)
TicketGrid.register("ticket", mapping=data_for_grid, keyfn=lambda ticket: ticket.id)
