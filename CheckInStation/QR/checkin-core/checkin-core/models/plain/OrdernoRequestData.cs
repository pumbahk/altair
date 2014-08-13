using System;
using System.Runtime.Serialization;

namespace checkin.core.models
{
    public class OrdernoRequestData
    {
        public string order_no { get; set; }

        public string tel { get; set; }
    }

    [DataContract]
    public class VerifiedOrdernoRequestData
    {
        [DataMember]
        public string order_no;
        [DataMember]
        public string secret;

        public VerifiedOrdernoRequestData (dynamic json)
        {
            this.order_no = json.order_no;
            this.secret = json.secret;
        }
    }
}

