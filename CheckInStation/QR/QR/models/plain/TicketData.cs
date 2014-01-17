using System;
using System.Runtime.Serialization;

namespace QR
{
	[DataContract]
	public class TicketData
	{
		//QR
		[DataMember]
		internal string codeno;
		//Status
		[DataMember]
		internal string refreshed_at;
		[DataMember]
		internal string printed_at;
		[DataMember]
		internal string ordered_product_item_token_id;
		[DataMember]
		internal string status;
		//認証情報
		[DataMember]
		internal string secret;
		//Seat
		[DataMember]
		internal _SeatData seat;
		//Additional
		[DataMember]
		internal AdditionalData additional;

		//statusのdefaultはvalid
		public TicketData (dynamic json)
		{
			this.codeno = json.codeno;
			this.refreshed_at = json.refreshed_at;
			this.printed_at = json.printed_at;
			this.ordered_product_item_token_id = json.ordered_product_item_token_id;
			this.secret = json.secret;
			this.status = json.status;
			this.seat = new _SeatData (json.seat);
			this.additional = new AdditionalData (json.additional);
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
