using System;
using System.Runtime.Serialization;
using System.Linq;
using System.Collections.Generic;

namespace QR
{
	[DataContract]
	public class TicketDataMinumum
	{
		[DataMember]
		internal string ordered_product_item_token_id;
		[DataMember]
		internal string seat_id;
		[DataMember]
		internal string seat_name;
	}

	[DataContract]
	public class TicketDataCollection
	{
		[DataMember]
		internal TicketData tdata;
		[DataMember]
		internal TicketDataMinumum[] collection;

		public TicketDataCollection (dynamic json, TicketData tdata)
		{
			this.tdata = tdata;
			var coll = new List<TicketDataMinumum> ();
			foreach (var sub in json.collection) {
				coll.Add (new TicketDataMinumum () {
					ordered_product_item_token_id = sub.ordered_product_item_token_id,
					seat_id = sub.seat_id,
					seat_name = sub.seat_name
				});
			}
			this.collection = coll.ToArray ();
		}
	}
}
