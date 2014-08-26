using System;
using System.Runtime.Serialization;

/* 本当は以下のことのチェックが必要
- 抜けている属性が無いか
- validな値か
*/
// see also: tests.misc.login.json
namespace checkin.core.models
{
    [DataContract]
    public class EndPoint
    {
        [DataMember]
        public string LoginStatus;
        [DataMember]
        public string QRFetchData;
        [DataMember]
        public string DataCollectionFetchData;
        [DataMember]
        public string QRSvgOne;
        [DataMember]
        public string QRSvgAll;
        [DataMember]
        public string ImageFromSvg;
        [DataMember]
        public string UpdatePrintedAt;
        [DataMember]
        public string UpdateRefreshedAt;
        [DataMember]
        public string UpdateRefreshedAt2;
        [DataMember]
        public string VerifyOrderData;

        [DataMember]
        public string[] AdImages; //xxx: 

        public static string asURL (string url)
        {
            new Uri (url); //slackoff validation
            return url;
        }

        public EndPoint (dynamic json)
        {
            this.LoginStatus = EndPoint.asURL (json.login_status);
            this.QRFetchData = EndPoint.asURL (json.qr_ticketdata);
            this.QRSvgOne = EndPoint.asURL (json.qr_svgsource_one);
            this.QRSvgAll = EndPoint.asURL (json.qr_svgsource_all);
            this.VerifyOrderData = EndPoint.asURL (json.orderno_verified_data);
            this.ImageFromSvg = EndPoint.asURL (json.image_from_svg);
            this.UpdatePrintedAt = EndPoint.asURL (json.qr_update_printed_at);
            this.UpdateRefreshedAt = EndPoint.asURL(json.refresh_order_qr);
            this.UpdateRefreshedAt2 = EndPoint.asURL(json.refresh_order2);
            this.DataCollectionFetchData = EndPoint.asURL (json.qr_ticketdata_collection);
        }

        public void ConfigureAdImages(string[] imageUrlList)
        {
            foreach(var url in imageUrlList){
                new Uri(url);
            }
            this.AdImages = imageUrlList;
        }
    }
}

