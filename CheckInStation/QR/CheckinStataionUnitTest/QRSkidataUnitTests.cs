using System;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.flow;
using checkin.core.events;
using checkin.core.web;
using checkin.core;
using Codeplex.Data;

namespace CheckinStataionUnitTest
{
    [TestClass]
    public class QRCodeSkidataProcessTest
    {
        [TestMethod]
        public void QRCodeSkidataFetchSuccess()
        {
            var t = Task.Run(async () =>
            {
                //var responseJSON = Testing.ReadFromEmbeddedFile("checkin-presentation.tests.misc.qrdata_skidata.json");
                string responseJSON = @"{
                    ""refreshed_at"": ""2012年12月12日"", 
                    ""printed_at"": null,
                    ""ordered_product_item_token_id"": ""-1"", 
                    ""status"": ""printed"",
                    ""secret"": ""xxx this is needed xxxx"",
                    ""product"": {
                        ""name"": ""ダミー席""
                    },
                    ""seat"": {
                        ""id"": ""-1111"",
                        ""name"": ""指定席A(1)""
                    },
                    ""additional"": {
                        ""user"": ""苗字名前"",
                        ""order"": {
                            ""order_no"": ""RT10101010"", 
                            ""id"": ""-11"",
                            ""note"": ""何かメモがあったりなかったり""
                        },
                        ""performance"": {
                            ""name"": ""ダミー公演"", 
                            ""date"": ""2012年12月24日"" 
                        },
                        ""event"": {
                            ""id"": ""-111"" 
                        }
                    }
                }";
                IResource resource = new Resource()
                {
                    HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper>(responseJSON)
                };
                resource.TicketDataFetcher = new TicketDataFetcher(resource);
                string strEndPoints = @"{
                        ""performance_list"": ""http:\/\/localhost:8000\/performance\/list"", 
                        ""qr_ticketdata_collection"": ""http:\/\/localhost:8000\/\/ticketdata\/collection"", 
                        ""login_status"": ""http:\/\/localhost:8000\/\/status"", 
                        ""qr_ticketdata"": ""http:\/\/localhost:8000\/\/ticketdata"",
                        ""qr_ticketdata_skidata"": ""http:\/\/localhost:8000\/\/ticketdata\/skidata"", 
                        ""orderno_verified_data"": ""http:\/\/localhost:8000\/\/verified_data"", 
                        ""image_from_svg"": ""http:\/\/localhost:8000"", 
                        ""refresh_order2"": ""http:\/\/localhost:8000\/\/order2"", 
                        ""qr_svgsource_all"": ""http:\/\/localhost:8000\/\/svgsource\/all"", 
                        ""refresh_order"": ""http:\/\/localhost:8000\/\/order"", 
                        ""refresh_order_qr"": ""http:\/\/localhost:8000\/\/order\/qr"", 
                        ""qr_svgsource_one"": ""http:\/\/localhost:8000\/qr\/svgsource\/one"", 
                        ""qr_ticketdata_skidata"": ""http:\/\/localhost:8000\/qr\/ticketdata\/skidata"", 
                        ""qr_update_printed_at"": ""http:\/\/localhost:8000\/qr\/printed\/update""
                }";
                var apiJson = DynamicJson.Parse(strEndPoints);
                resource.EndPoint = new EndPoint(apiJson);
                // case 初期化
                var qrcode = "TS0123456789ABCDEFGH";
                ICase target = new CaseQRDataFetch(resource, qrcode);
                QRInputEvent ev = new QRInputEvent();

                await target.PrepareAsync(ev as IInternalEvent);
                //Console.WriteLine (await target.VerifyAsync ());
                //ev.HandleEvent ();

                Assert.IsTrue(await target.VerifyAsync());
            });
            t.Wait();
        }

        [TestMethod]
        public void QRCodeFetchSuccess()
        {
            var t = Task.Run(async () =>
            {
                //var responseJSON = Testing.ReadFromEmbeddedFile("checkin-presentation.tests.misc.qrdata_skidata.json");
                string responseJSON = @"{
                    ""codeno"": ""1"", 
                    ""refreshed_at"": ""2012年12月12日"", 
                    ""printed_at"": null,
                    ""ordered_product_item_token_id"": ""-1"", 
                    ""status"": ""printed"",
                    ""secret"": ""xxx this is needed xxxx"",
                    ""product"": {
                        ""name"": ""ダミー席""
                    },
                    ""seat"": {
                        ""id"": ""-1111"",
                        ""name"": ""指定席A(1)""
                    },
                    ""additional"": {
                        ""user"": ""苗字名前"",
                        ""order"": {
                            ""order_no"": ""RT10101010"", 
                            ""id"": ""-11"",
                            ""note"": ""何かメモがあったりなかったり""
                        },
                        ""performance"": {
                            ""name"": ""ダミー公演"", 
                            ""date"": ""2012年12月24日"" 
                        },
                        ""event"": {
                            ""id"": ""-111"" 
                        }
                    }
                }";
                IResource resource = new Resource()
                {
                    HttpWrapperFactory = new FakeHttpWrapperFactory<HttpWrapper>(responseJSON)
                };
                resource.TicketDataFetcher = new TicketDataFetcher(resource);
                string strEndPoints = @"{
                        ""performance_list"": ""http:\/\/localhost:8000\/performance\/list"", 
                        ""qr_ticketdata_collection"": ""http:\/\/localhost:8000\/\/ticketdata\/collection"", 
                        ""login_status"": ""http:\/\/localhost:8000\/\/status"", 
                        ""qr_ticketdata"": ""http:\/\/localhost:8000\/\/ticketdata"",
                        ""qr_ticketdata_skidata"": ""http:\/\/localhost:8000\/\/ticketdata\/skidata"", 
                        ""orderno_verified_data"": ""http:\/\/localhost:8000\/\/verified_data"", 
                        ""image_from_svg"": ""http:\/\/localhost:8000"", 
                        ""refresh_order2"": ""http:\/\/localhost:8000\/\/order2"", 
                        ""qr_svgsource_all"": ""http:\/\/localhost:8000\/\/svgsource\/all"", 
                        ""refresh_order"": ""http:\/\/localhost:8000\/\/order"", 
                        ""refresh_order_qr"": ""http:\/\/localhost:8000\/\/order\/qr"", 
                        ""qr_svgsource_one"": ""http:\/\/localhost:8000\/qr\/svgsource\/one"", 
                        ""qr_ticketdata_skidata"": ""http:\/\/localhost:8000\/qr\/ticketdata\/skidata"", 
                        ""qr_update_printed_at"": ""http:\/\/localhost:8000\/qr\/printed\/update""
                }";
                var apiJson = DynamicJson.Parse(strEndPoints);
                resource.EndPoint = new EndPoint(apiJson);
                // case 初期化
                var qrcode = "*qrcode*";
                ICase target = new CaseQRDataFetch(resource, qrcode);
                QRInputEvent ev = new QRInputEvent();

                await target.PrepareAsync(ev as IInternalEvent);
                //Console.WriteLine (await target.VerifyAsync ());
                //ev.HandleEvent ();

                Assert.IsTrue(await target.VerifyAsync());
            });
            t.Wait();
        }
    }
}
