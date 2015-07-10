using System;
using System.Runtime.Serialization;
using checkin.core.message;

namespace checkin.core.models
{
    public enum TokenStatus
    {
        valid,
        printed,
        canceled,
        before_start,
        after_end,
        not_supported,
        over_print_limit,
        unknown
    }

    [DataContract]
    public class TicketData
    {
        //QR
        [DataMember]
        public string codeno;
        //Status
        [DataMember]
        public string refreshed_at;
        [DataMember]
        public string printed_at;
        [DataMember]
        public string ordered_product_item_token_id;
        [DataMember]
        public TokenStatus status;
        //認証情報
        [DataMember]
        public string secret;
        //Seat
        [DataMember]
        public _SeatData seat;
        [DataMember]
        public _ProductData product;
        //Additional
        [DataMember]
        public AdditionalData additional;
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
            //印刷済みということをユーザーに伝えるべきか考える。
            return this.status == TokenStatus.valid || this.status == TokenStatus.printed;
        }
    }
}
