using System;
using NUnit.Framework;
using System.Threading.Tasks;

//TODO: 2度押し防止
/*
namespace checkin.core
{
    //fake object
    [TestFixture ()]
    public class QRCodeInputTests
    {
        public CaseQRCodeInput target;

        [SetUp]
        public void SetupFixture ()
        {
            var loader = new FakeDataLoader<string> ("*qrcode*");
            var verifier = new FakeVerifier<string> (true);

            var resource = new Resource () {
                TicketDataFetcher = loader,
                QRCodeVerifier = verifier
            };

            this.target = new CaseQRCodeInput (resource);
        }

        [Test ()]
        public void TestVerify ()
        {
            var t = Task.Run (async () => {
                await target.PrepareAsync (new QRInputEvent (){ QRCode = "*qrcode*" });
                Assert.That (await target.VerifyAsync (), Is.True);
                Assert.That (Is.Equals (target.QRCode, "*qrcode*"));
            });
            t.Wait ();
        }

        [Test ()]
        public void TestCallVerifyManyTimes ()
        {
            var t = Task.Run (async () => {
                await target.PrepareAsync (new QRInputEvent (){ QRCode = "*qrcode*" });
                Assert.That (Is.Equals (target.VerifiedCount, 0));

                Assert.IsTrue (await target.VerifyAsync ());
                Assert.That (Is.Equals (target.VerifiedCount, 1));

                Assert.IsTrue (await target.VerifyAsync ());
                Assert.That (Is.Equals (target.VerifiedCount, 1));
            });
            t.Wait ();
        }

        [Test ()]
        public void TestCallVerifyManyTimes__False ()
        {
            var t = Task.Run (async () => {
                await target.PrepareAsync (new QRInputEvent (){ QRCode = "*qrcode*" }); 
                FakeVerifier<string> v = target.TicketDataFetcher as FakeVerifier<string>;
                v.Result = false;

                Assert.That (Is.Equals (target.VerifiedCount, 0));

                Assert.IsFalse (await target.VerifyAsync ());
                Assert.That (Is.Equals (target.VerifiedCount, 1));

                Assert.IsFalse (await target.VerifyAsync ());
                Assert.That (Is.Equals (target.VerifiedCount, 1));
            });
            t.Wait ();
        }
    }
}
*/
