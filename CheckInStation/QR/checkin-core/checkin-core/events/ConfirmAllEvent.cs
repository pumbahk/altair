using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using checkin.core.models;

namespace checkin.core.events
{
    public enum ConfirmAllStatus
    {
        starting,
        prepared,
        requesting,
        fetched,
    }

    public enum ConfirmAllType
    {
        none,
        all,
    }

    public interface IConfirmAllStatusInfo
    {
        ConfirmAllStatus Status { get; set; }
        TicketData ReadTicketData { get; set; }
        TicketDataCollection TicketDataCollection { get; set; }
        int PartOrAll { get; set; }
    }
    
    public class ConfirmAllEvent : AbstractEvent, IInternalEvent       
    {
        public IConfirmAllStatusInfo StatusInfo { get; set; }
        public void ChangeStatus(ConfirmAllStatus s)
        {
            this.StatusInfo.Status = s;
        }

        public void SetCollection(TicketDataCollection ticketcollection, ConfirmAllType type)
        {
            TicketDataCollection tempCollection = this.StatusInfo.TicketDataCollection;
            foreach (TicketDataMinumum ticket in ticketcollection.collection)
            {
                if (type == ConfirmAllType.none)
                {
                    ticket.is_selected = false;
                }
                else
                {
                    if (ticket.printed_at == null)
                    {
                        ticket.is_selected = true;
                    }
                }
            }
            if (tempCollection != null)
            {
                /*
                foreach (TicketDataMinumum ticket in ticketcollection.collection)
                {
                    ticket.is_selected = false;
                }
                foreach(TicketDataMinumum t in tempCollection.collection)
                {
                    foreach (TicketDataMinumum ticket in ticketcollection.collection)
                    {   
                        if (ticket.ordered_product_item_token_id == t.ordered_product_item_token_id)
                        {
                            ticket.is_selected = t.is_selected;
                        }
                    }
                }
                 */
                ticketcollection = tempCollection;
            }
            this.StatusInfo.TicketDataCollection = ticketcollection;
            this.StatusInfo.Status = ConfirmAllStatus.prepared;
        }
    
        public void SetInfo(TicketData readTicketData)
        {
            this.StatusInfo.ReadTicketData = readTicketData;
        }

        public void SetPartOrAll(int partorall)
        {
            this.StatusInfo.PartOrAll = partorall;
        }
    }
}
