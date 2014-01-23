using System;
using System.Runtime.Serialization;

namespace QR
{
	public enum TokenStatus
	{
		valid,
		printed,
		canceled,
		before_start,
		not_supported,
		unknown
	}

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
		internal TokenStatus status;
		//認証情報
		[DataMember]
		internal string secret;
		//Seat
		[DataMember]
		internal _SeatData seat;
        [DataMember]
        internal _ProductData product;
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
			this.status = EnumUtil.ParseEnum<TokenStatus> (json.status);
			this.seat = new _SeatData (json.seat);
            this.product = new _ProductData(json.product);
			this.additional = new AdditionalData (json.additional);
		}

		public bool Verify ()
		{
			return this.status == TokenStatus.valid;
		}
	}
}
