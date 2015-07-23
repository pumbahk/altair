using System;
using NUnit.Framework;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.core
{
    [TestFixture ()]
    public class FlowAuthTests
    {
        [Test, Description ("認証input画面 -ok-> password入力 -ok> auth情報取得 -ok-> <認証後の遷移へ>")]
            public void TestAuthFlow ()
        {            
            var resource = new Resource ();

            var fakeDefinition = new Moq.Mock<IFlowDefinition> ();
            var fakeAfterAuthorization = new Moq.Mock<ICase> () ;
            fakeDefinition.Setup (d => d.AfterAuthorization (resource)).Returns (fakeAfterAuthorization.Object);
            

            var manager = new FlowManager (){FlowDefinition = fakeDefinition.Object};
            var startpoint = new CaseAuthInput (resource);

            FakeFlow target = new FakeFlow (manager, startpoint);

            var t = Task.Run (async () => {
                // start
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseAuthInput> (target.Case);

                // 認証処理
                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseAuthPassword> (target.Case);

                // 認証処理
                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseAuthDataFetch> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.AreSame(fakeAfterAuthorization.Object, target.Case);
            });
            t.Wait ();
        }

        [Test, Description ("認証情報入力 -ng-> 認証情報入力")]
        public void Test__AuthInput__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseAuthInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = false;
                Assert.IsInstanceOf<CaseAuthInput> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseAuthInput> (target.Case);

            });
            t.Wait ();
        }

        [Test, Description ("認証情報取得 -ng-> 認証情報入力")]
        public void Test__AuthDataFetch__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseAuthDataFetch (new Resource (), "user", "password");
            FakeFlow target = new FakeFlow (manager, startpoint);

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = false;
                Assert.IsInstanceOf<CaseAuthDataFetch> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseAuthInput> (target.Case);

            });
            t.Wait ();
        }
    }

    [TestFixture ()]
    public class FlowInputStrategySelectTests
    {
        [Test]
        public void TestManagerGetInternalEvent__AtleastEmptyEvent ()
        {
            var manager = new FlowManager ();
            manager.GetInternalEvent ();
        }

        [Test, Description ("default: 認証方法選択画面 -qr-> QR読み込み")]
        public void TestInputSelectRedirectQRCode ()
        {
            var manager = new FlowManager (new DefaultFlowDefinition());
            var startpoint = new CaseInputStrategySelect (new Resource ());

            FakeFlow target = new FakeFlow (manager, startpoint);

            var t = Task.Run (async () => {
                // start
                target.VerifyStatus = true;
                (target.Case as CaseInputStrategySelect).Unit = InputUnit.qrcode;

                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }

        [Test, Description ("default: 認証方法選択画面 -order_no-> 注文番号読み込み")]
        public void TestInputSelectRedirectOrderno ()
        {
            var manager = new FlowManager (new DefaultFlowDefinition());
            var startpoint = new CaseInputStrategySelect (new Resource ());

            FakeFlow target = new FakeFlow (manager, startpoint);

            var t = Task.Run (async () => {
                // start
                target.VerifyStatus = true;
                (target.Case as CaseInputStrategySelect).Unit = InputUnit.order_no;

                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);
            });
            t.Wait ();
        }

        [Test, Description ("認証方法選択画面 -ng-> 認証方法選択画面")]
        public void TestInputSelect__Failure__InputSelect ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseInputStrategySelect (new Resource ());

            FakeFlow target = new FakeFlow (manager, startpoint);

            var t = Task.Run (async () => {
                // start
                target.VerifyStatus = false;
                (target.Case as CaseInputStrategySelect).Unit = InputUnit.qrcode;

                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseInputStrategySelect> (target.Case);

            });
            t.Wait ();
        }
    }

    [TestFixture ()]
    public class FlowOrdernoTests
    {
        [Test, Description ("default 注文番号読み込み -ok-> 電話番号読み込み -ok-> 注文番号データのverify -ok-> Orderno表示(all) -ok-> 印刷(all) -ok-> 発券しました -ok-> 注文番号読み込み")]
        public void TestItForOrderno_Default ()
        {
            var manager = new FlowManager (new DefaultFlowDefinition());
            var startpoint = new CaseOrdernoOrdernoInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.order_no;

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoTelInput> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoVerifyRequestData> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoConfirmForAll> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.That ((target.Case is CasePrintForOne), Is.False);
                Assert.IsInstanceOf<CasePrintForAll> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CasePrintFinish> (target.Case);

                // Finish. after redirect
                Assert.AreSame (InputUnit.order_no.ToString (), target.GetFlowDefinition ().CurrentInputUnit.ToString ());

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);
            });
            t.Wait ();
        }
    

        [Test, Description ("注文番号読み込み -ng-> 注文番号読み込み ")]
        public void Test__OrdernoInput__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseOrdernoOrdernoInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.order_no;

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = false;
                Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);
            });
            t.Wait ();
        }

        [Test, Description ("注文番号データのverify -ng-> エラー表示 -ok> 注文番号読み込み ")]
        public void Test__OrdernoVerifyOrderData__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseOrdernoVerifyRequestData (new Resource (), null);
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.order_no;

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = false;
                Assert.IsInstanceOf<CaseOrdernoVerifyRequestData> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseFailureRedirect> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseOrdernoOrdernoInput> (target.Case);
            });
            t.Wait ();
        }
    }

    [TestFixture ()]
    public class FlowQRTests
    {
        [Test, Description ("default QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚) -ok-> 印刷(1枚) -ok> 発券しました -ok-> QR読み込み")]
        public void TestItForOne__Default ()
        {
            var manager = new FlowManager(new DefaultFlowDefinition());
            var startpoint = new CaseQRCodeInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRDataFetch> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRConfirmForOne> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CasePrintForOne> (target.Case);
                Assert.That ((target.Case is CasePrintForAll), Is.False);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CasePrintFinish> (target.Case);

                // Finish. after redirect
                Assert.AreSame (InputUnit.qrcode.ToString (), target.GetFlowDefinition ().CurrentInputUnit.ToString ());

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }
        
        [Test,Description ("QR読み込み -ng-> QR読み込み")]
        public void Test__QRInput__Failure__QRInput ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseQRCodeInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

            var t = Task.Run (async () => {
                target.VerifyStatus = false;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }


        [Test,Description ("QRからデータ取得中 -ng-> エラー表示 -ok-> QR読み込み")]
        public void Test__QRDataFetch__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseQRDataFetch (new Resource (), null);
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

            var t = Task.Run (async () => {
                target.VerifyStatus = false;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseFailureRedirect> (target.Case);

                target.VerifyStatus = true;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }

        [Test,Description ("印刷(1枚) -ng-> エラー表示 -> QR読み込み")]
        public void Test__PrintForOne__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CasePrintForOne (new Resource (), null);
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

            var t = Task.Run (async () => {
                target.VerifyStatus = false;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseFailureRedirect> (target.Case);

                target.VerifyStatus = true;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }

        [Test,Description ("印刷(all) -ng-> エラー表示 -> QR読み込み")]
        public void Test__PrintForAll__Failure__DisplayError ()
        {
            var manager = new FlowManager ();
            var startpoint = new CasePrintForAll (new Resource (), null);
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

            var t = Task.Run (async () => {
                target.VerifyStatus = false;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseFailureRedirect> (target.Case);

                target.VerifyStatus = true;
                target = await target.Forward () as FakeFlow;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }

        [Test,Description ("default: QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚)[すべて印刷選択] -ok-> QR表示(all) -ok-> 印刷(all) -ok> 発券しました -ok-> QR読み込み")]
        public void TestItForAll__Default ()
        {
            var manager = new FlowManager (new DefaultFlowDefinition());
            var startpoint = new CaseQRCodeInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;

            var t = Task.Run (async () => {
                // start 
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRDataFetch> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRConfirmForOne> (target.Case);

                (target.Case as CaseQRConfirmForOne).Unit = PrintUnit.all;

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRConfirmForAll> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.That ((target.Case is CasePrintForOne), Is.False);
                Assert.IsInstanceOf<CasePrintForAll> (target.Case);

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CasePrintFinish> (target.Case);

                // Finish. after redirect
                Assert.AreSame (InputUnit.qrcode.ToString (), target.GetFlowDefinition ().CurrentInputUnit.ToString ());

                target = await target.Forward () as FakeFlow;
                target.VerifyStatus = true;
                Assert.IsInstanceOf<CaseQRCodeInput> (target.Case);
            });
            t.Wait ();
        }

    }
}

