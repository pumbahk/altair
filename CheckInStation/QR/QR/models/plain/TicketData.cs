using System;
using System.Runtime.Serialization;

namespace QR
{
	[DataContract]
	public class TicketData
	{
		[DataMember]
		internal AdditionalData additional;
		[DataMember]
		internal string ordered_product_item_token_id;
		[DataMember]
		internal string order_no;
		[DataMember]
		internal string seat_id;
		[DataMember]
		internal string seat_name;
		[DataMember]//認証情報
		internal string secret;
		[DataMember]
		internal string status;
		//statusのdefaultはvalid
		public TicketData (dynamic json)
		{
			ordered_product_item_token_id = json.ordered_product_item_token_id;
			order_no = json.order_no;
			seat_id = json.seat_id;
			seat_name = json.seat_name;
			secret = json.secret;
			status = json.status;
			additional = new AdditionalData (json);
		}

		public bool Verify ()
		{
			/*
			 * - キャンセル済み
			 * - 印刷済み
			 * - 何かわからない状況で失敗(こちらはOnFailure()になるのでOK)
			 */ 
			return true; //this.status == "valid"; //fmm;
		}

		public string StatusMessage (IResource resource)
		{
			return this.status;
		}
	}
}
