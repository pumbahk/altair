using System;

namespace checkin.core.events
{
    public enum InputUnit
    {
        qrcode = 0,
        order_no = 1,
        before_auth = 404,
    }

    public class SelectInputStragetyEvent : AbstractEvent, IInternalEvent
    {
        public InputUnit InputUnit { get; set; }

        public string InputUnitString { get; set; }
    }
}

