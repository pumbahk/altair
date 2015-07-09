using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.events
{
    public class OneOrPartEvent : AbstractEvent, IInternalEvent
    {
        public int PrintCount { set; get; }
        public OneOrPartEvent()
            : base()
        {
        }
        public OneOrPartEvent(int printcount)
            : base()
        {
            PrintCount = printcount;
        }
    }
}
