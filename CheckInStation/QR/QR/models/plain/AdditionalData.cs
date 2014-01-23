using System;
using System.Runtime.Serialization;

namespace QR
{
	[DataContract]
	public class _OrderData
	{
		[DataMember]
		internal string order_no;
		[DataMember]
		internal string id;
		[DataMember]
		internal string note;

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
		internal string id;
		[DataMember]
		internal string name;

		public _SeatData (dynamic json)
		{
			this.id = json.id;
			this.name = json.name;
		}
	}

    public class _PerformanceData
    {
        [DataMember]
        internal string name;
        [DataMember]
        internal string date;
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
        internal string name;

        public _ProductData(dynamic json)
        {
            this.name = json.name;
        }
    }

	[DataContract]
	public class AdditionalData
	{
		[DataMember]
		internal string user;
		//Order
		[DataMember]
		internal _OrderData order;
        [DataMember]
        internal _PerformanceData performance;

		public AdditionalData (dynamic json)
		{
			this.user = json.user;
			this.order = new _OrderData (json.order);
            this.performance = new _PerformanceData(json.performance);
		}
	}
}

