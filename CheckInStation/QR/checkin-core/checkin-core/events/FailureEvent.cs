using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.events
{
    public interface IFailureStatusInfo
    {
        string Message { get; set; }
    }
    public class FailureEvent : AbstractEvent, IInternalEvent
    {
        public IFailureStatusInfo StatusInfo { get; set; }
        public string Message
        {
            get { return this.StatusInfo.Message; }
            set { this.StatusInfo.Message = value; }
        }
    }
}
