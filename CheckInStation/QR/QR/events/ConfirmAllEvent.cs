using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QR
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
        TicketDataCollection TicketDataCollection { get; set; }
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
    }
}
