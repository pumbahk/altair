using System;

namespace checkin.core.events
{
    public enum PrintUnit
    {
        one = 0,
        all = 1
    }

    public class QRInputEvent : AbstractEvent, IInternalEvent
    {
        public string QRCode { get; set; }

        public QRInputEvent () : base ()
        {
        }
    }
}

