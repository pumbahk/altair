using NUnit.Framework;
using System;
using System.Threading.Tasks;
using checkin.core.flow;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core
{
    [TestFixture()]
    public class BackwardForEaglesTests
    {
        [Test, Description ("QR印刷 -ok> 印刷完了しました -ok> QR読み込み -backward-> QR読み込み")]
        public void TestBackwardFromQRPrintFinished__Eagles ()
        {
            var manager = new FlowManager (new EaglesFlowDefinition());
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
                Assert.IsInstanceOf<CaseQRCodeInput> (result);

                // peekでも現在のCaseが取れる必要がある!!
                Assert.IsInstanceOf<CaseQRCodeInput>(manager.Peek().Case);
            });
            t.Wait ();
        }

        [Test, Description("QRデータ取得中 -ng -> エラー画面 -ok> QR読み込み -backward-> QR読み込み")]
        public void TestBackwordFromQRDataFetchErrorRedirect()
        {
            var manager = new FlowManager (new EaglesFlowDefinition());
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
                Assert.IsInstanceOf<CaseQRCodeInput>(case_);

                // peekでも現在のCaseが取れる必要がある!!
                Assert.IsInstanceOf<CaseQRCodeInput>(manager.Peek().Case);
            });
            t.Wait ();
        }
    }
    
}
