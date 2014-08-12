using System;
using System.Linq;

namespace checkin.core.models
{
    using System.Collections.Generic;
using TokenTicketTemplatePair = Tuple<string, string>;

    public class _PrintedTicket {
        public string token_id { get; set; }
        public string template_id { get; set; }
    }


    public class UpdatePrintedAtRequestData
    {
        public _PrintedTicket[] printed_ticket_list { get; set; }

        public string order_no{ get; set; }

        public string secret{ get; set; }

        public UpdatePrintedAtRequestData ()
        {
        }

        public static UpdatePrintedAtRequestData Build(TicketData tdata, IEnumerable<TokenTicketTemplatePair> printedList){
            return new UpdatePrintedAtRequestData(){
                secret = tdata.secret,
                order_no = tdata.additional.order.order_no,
                printed_ticket_list = printedList.Select(p => new _PrintedTicket(){token_id=p.Item1, template_id=p.Item2}).ToArray()
            };
        }
        public static UpdatePrintedAtRequestData Build(TicketDataCollection tdata, IEnumerable<TokenTicketTemplatePair> printedList)
        {
            return new UpdatePrintedAtRequestData()
            {
                secret = tdata.secret,
                order_no = tdata.additional.order.order_no,
                printed_ticket_list = printedList.Select(p => new _PrintedTicket() { token_id = p.Item1, template_id = p.Item2 }).ToArray()
            };
        }
    }
}

