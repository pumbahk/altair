using System;
using System.Collections.Generic;

namespace checkin.core.events
{
    public class WelcomeEvent : AbstractEvent, IInternalEvent
    {
        public int PrintType{ set; get; }
        public WelcomeEvent() : base()
        {
        }
        public WelcomeEvent(int printtype)
            : base()
        {
            PrintType = printtype;
        }
    }
}

