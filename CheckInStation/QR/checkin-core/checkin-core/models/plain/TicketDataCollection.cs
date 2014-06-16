using System;
using System.Runtime.Serialization;
using System.Linq;
using System.Collections.Generic;
using NLog;
using Microsoft.CSharp.RuntimeBinder;
using checkin.core.support;
using checkin.core.message;

namespace checkin.core.models
{
    [DataContract]
    public class TicketDataMinumum
    {
        public static Logger logger = LogManager.GetCurrentClassLogger();
        [DataMember]
        public string ordered_product_item_token_id;
        [DataMember]
        public string printed_at;
        [DataMember]
        public string locked_at;
        [DataMember]
        public string refreshed_at;
        [DataMember]
        public _SeatData seat;
        [DataMember]
        public _ProductData product;
        [DataMember]
        public bool is_selected;

        public TicketDataMinumum()
        {
            //dont use
        }

        public TicketDataMinumum (dynamic json)
        {
            this.ordered_product_item_token_id = json.ordered_product_item_token_id;
            this.printed_at = json.printed_at;
            this.refreshed_at = json.refreshed_at;
            try
            {
                this.locked_at = json.locked_at == null ? "" : json.locked_at;
            }
            catch (RuntimeBinderException ex)
            {
                logger.Warn("server response doesn't have locked_at.".WithMachineName());
                this.locked_at = "";
            }
            this.seat = new _SeatData (json.seat);
            this.product = new _ProductData(json.product);
            this.is_selected = (this.printed_at == null ? true : false);
        }
    }

    [DataContract]
    public class TicketDataCollection
    {
        [DataMember]
        public TokenStatus status;
        //認証情報
        [DataMember]
        public string secret;
        [DataMember]
        public AdditionalData additional;
        [DataMember]
        public TicketDataMinumum[] collection;

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