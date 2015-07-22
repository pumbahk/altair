using NUnit.Framework;
using System;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.core
{

    [TestFixture ()]
    public class BackwardTests
    {
        [Test, Description ("QR印刷 -ok> 印刷完了しました -ok> QR読み込み -backward-> QR読み込み")]
        public void TestBackwardFromQRPrintFinished ()
        {
            var manager = new FlowManager ();
            var startpoint = new CasePrintFinish (new Resource (), null);
            FakeFlow target = new FakeFlow (manager, startpoint);

            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;
            manager.SetStartPoint (target);

            ICase result, case_;
            var t = Task.Run (async () => {
                // start 
                (manager.Peek () as FakeFlow).VerifyStatus = true;
                case_ = await manager.Forward ();
                Assert.IsInstanceOf<CaseQRCodeInput> (case_);

                /// 印刷後. backword.
                result = await manager.Backward ();
                Assert.IsInstanceOf<CaseInputStrategySelect> (result);

                // peekでも現在のCaseが取れる必要がある!!
                Assert.IsInstanceOf<CaseInputStrategySelect>(manager.Peek().Case);
            });
            t.Wait ();
        }

        [Test, Description ("認証情報選択 -[qr]-> QR読み込み -backward-> 認証情報選択")]
        public void TestBackwordFromAfterInputStrategySelect ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseInputStrategySelect (new Resource());
            var target = new FakeFlow (manager, startpoint);
            startpoint.Unit = InputUnit.qrcode;
            manager.SetStartPoint (target);

            ICase result, case_;
            var t = Task.Run (async () => {
                // start 
                (manager.Peek () as FakeFlow).VerifyStatus = true;
                case_ = await manager.Forward ();
                Assert.IsInstanceOf<CaseQRCodeInput> (case_);

                result = await manager.Backward ();
                Assert.IsInstanceOf<CaseInputStrategySelect> (result);
                // peekでも現在のCaseが取れる必要がある!!
                Assert.IsInstanceOf<CaseInputStrategySelect>(manager.Peek().Case);
            }); 
            t.Wait ();
        }
        [Test, Description("QRデータ取得中 -ng -> エラー画面 -ok> QR読み込み -backward-> 認証方法選択")]
        public void TestBackwordFromQRDataFetchErrorRedirect()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseQRDataFetch (new Resource (), null);
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;
            manager.SetStartPoint (target);

            ICase result, case_;
            var t = Task.Run (async () => {
                // start 
                (manager.Peek () as FakeFlow).VerifyStatus = false;
                case_ = await manager.Forward ();
                Assert.IsInstanceOf<CaseFailureRedirect> (case_);

                (manager.Peek () as FakeFlow).VerifyStatus = true;
                case_ = await manager.Forward ();
                Assert.IsInstanceOf<CaseQRCodeInput> (case_);

                // 印刷表示(1枚)の後

                result = await manager.Backward ();
                Assert.IsInstanceOf<CaseInputStrategySelect> (result);

                // peekでも現在のCaseが取れる必要がある!!
                Assert.IsInstanceOf<CaseInputStrategySelect>(manager.Peek().Case);
            });
            t.Wait ();
        }

        [Test, Description ("QR読み込み -ok-> QRからデータ取得中 -ok-> QR表示(1枚) -backword-> QR読み込み")]
        public void TestBackwordFromQRConfirmForwarding ()
        {
            var manager = new FlowManager ();
            var startpoint = new CaseQRCodeInput (new Resource ());
            FakeFlow target = new FakeFlow (manager, startpoint);
            // これは遷移時にすでに設定されている
            target.GetFlowDefinition ().CurrentInputUnit = InputUnit.qrcode;
            manager.SetStartPoint (target);

            ICase result, case_;
            var t = Task.Run (async () => {
                // start 
                (manager.Peek () as FakeFlow).VerifyStatus = true;
                case_ = await manager.Forward ();
                Assert.IsInstanceOf<CaseQRDataFetch> (case_);

                (manager.Peek () as FakeFlow).VerifyStatus = true;
                case_ = await manager.Forward ();
                Assert.IsInstanceOf<CaseQRConfirmForOne> (case_);

                // 印刷表示(1枚)の後

                result = await manager.Backward ();
                Assert.IsInstanceOf<CaseQRCodeInput> (result);

                // peekでも現在のCaseが取れる必要がある!!
                Assert.IsInstanceOf<CaseQRCodeInput>(manager.Peek().Case);
            });
            t.Wait ();
        }
    }
}

