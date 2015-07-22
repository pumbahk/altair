using System;
using System.Runtime.Serialization;

namespace checkin.core.models
{
    [DataContract]
    public class _OrderData
    {
        [DataMember]
        public string order_no;
        [DataMember]
        public string id;
        [DataMember]
        public string note;

        public _OrderData (dynamic json)
        {
            this.order_no = json.order_no;
            this.id = json.id;
            this.note = json.note;
        }
    }

    [DataContract]
    public class _SeatData
    {
        [DataMember]
        public string id;
        [DataMember]
        public string name;

        public _SeatData (dynamic json)
        {
            this.id = json.id;
            this.name = json.name;
        }
    }

    public class _PerformanceData
    {
        [DataMember]
        public string name;
        [DataMember]
        public string date;
        public _PerformanceData(dynamic json)
        {
            this.name = json.name;
            this.date = json.date;
        }
    }

    [DataContract]
    public class _ProductData
    {
        [DataMember]
        public string name;

        public _ProductData(dynamic json)
        {
            this.name = json.name;
        }
    }

    [DataContract]
    public class AdditionalData
    {
        [DataMember]
        public string user;
        //Order
        [DataMember]
        public _OrderData order;
        [DataMember]
        public _PerformanceData performance;

        public AdditionalData (dynamic json)
        {
            this.user = json.user;
            this.order = new _OrderData (json.order);
            this.performance = new _PerformanceData(json.performance);
        }
    }
}

