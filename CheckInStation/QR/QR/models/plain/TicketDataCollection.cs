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
        internal string printed_at;
        [DataMember]
        internal string refreshed_at;
        [DataMember]
        internal _SeatData seat;
        [DataMember]
        internal _ProductData product;
        [DataMember]
        internal bool is_selected;

        public TicketDataMinumum (dynamic json)
        {
            this.ordered_product_item_token_id = json.ordered_product_item_token_id;
            this.printed_at = json.printed_at;
            this.refreshed_at = json.refreshed_at;
            this.seat = new _SeatData (json.seat);
            this.product = new _ProductData(json.product);
            this.is_selected = (this.printed_at == null ? true : false);
        }
    }

    [DataContract]
    public class TicketDataCollection
    {
        [DataMember]
        internal TokenStatus status;
        //認証情報
        [DataMember]
        internal string secret;
        [DataMember]
        internal AdditionalData additional;
        [DataMember]
        internal TicketDataMinumum[] collection;

        public void ConfigureCollection (dynamic json)
        {            
            var coll = new List<TicketDataMinumum> ();
            foreach (var sub in json) {
                coll.Add (new TicketDataMinumum (sub));
            }
            this.collection = coll.ToArray ();
        }

        public TicketDataCollection (dynamic json)
        {
            this.status = EnumUtil.ParseEnum<TokenStatus> (json.status);
            this.secret = json.secret;
            this.ConfigureCollection (json.collection);
            this.additional = new AdditionalData (json.additional);
        }

        public bool Verify ()
        {
            return this.status == TokenStatus.valid;
        }
    }
}