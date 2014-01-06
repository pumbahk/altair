using System;
using System.Runtime.Serialization;

/*{
    "user": "苗字名前", 
    "codeno": "*codeno*", 
    "ordered_product_item_token_id": "-1", 
    "refreshed_at": "2012年12月12日", 
    "printed_at": null,
    "order_no": "RT10101010", 
    "order_id": "-11", 
    "performance_name": "ダミー公演", 
    "performance_date": "2012年12月24日", 
    "event_id": "-111", 
    "product_name": "ダミー席", 
    "seat_id": "-1111",
    "seat_name": "自由席",
    "note": "何かメモがあったりなかったり",
}
*/
namespace QR
{
	[DataContract]
	public class TicketData
	{
		[DataMember]
		internal string user;
		[DataMember]
		internal string ordered_product_item_token_id;
		[DataMember]
		internal string order_no;
		[DataMember]
		internal string seat_id;
		[DataMember]
		internal string seat_name;

		public TicketData (dynamic json)
		{
			user = json.user;
			ordered_product_item_token_id = json.ordered_product_item_token_id;
			order_no = json.order_no;
			seat_id = json.seat_id;
			seat_name = json.seat_name;
		}
	}
}
