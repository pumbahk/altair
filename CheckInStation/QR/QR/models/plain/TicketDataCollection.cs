using System;
using System.Runtime.Serialization;
using System.Linq;
using System.Collections.Generic;
using NLog;

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
		internal string user;
		[DataMember]//認証情報
		internal string secret;
		[DataMember]
		internal AdditionalData additional;
		[DataMember]
		internal TicketDataMinumum[] collection;
		private static Logger logger = LogManager.GetCurrentClassLogger ();

		public void ConfigureCollection (dynamic json)
		{			
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

		public TicketDataCollection (dynamic json)
		{
			this.ConfigureCollection (json);
			this.additional = new AdditionalData (json);
		}
	}
}