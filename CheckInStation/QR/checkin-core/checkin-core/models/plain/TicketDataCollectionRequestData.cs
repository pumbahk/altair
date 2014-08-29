using System;

namespace checkin.core.models
{
    public class TicketDataCollectionRequestData
    {
        public string order_no{ get; set; }

        public string secret { get; set; } //認証情報

        public bool refreshMode { get; set; }
    }
}
