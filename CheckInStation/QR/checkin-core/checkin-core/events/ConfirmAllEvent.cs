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

        public void SetCollection(TicketDataCollection collection)
        {
            this.StatusInfo.TicketDataCollection = collection;
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
