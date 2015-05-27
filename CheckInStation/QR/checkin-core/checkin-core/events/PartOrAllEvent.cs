using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.events
{
    public class PartOrAllEvent : AbstractEvent, IInternalEvent
    {
        public int PrintCount { set; get; }
        public PartOrAllEvent()
            : base()
        {
        }
        public PartOrAllEvent(int printcount)
            : base()
        {
            PrintCount = printcount;
        }
    }
}
