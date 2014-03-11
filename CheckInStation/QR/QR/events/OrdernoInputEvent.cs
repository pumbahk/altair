using System;

namespace QR
{
    /*
    public enum OrdernoInputStatus
    {
        starting,
        requesting,
        prepared,
        fetched
    }
    */
    

    public class OrdernoInputEvent : AbstractEvent, IInternalEvent
    {
        public string Orderno { get; set; }

        public string Tel { get; set; }

        public OrdernoInputEvent () : base ()
        {
        }

    }
}
