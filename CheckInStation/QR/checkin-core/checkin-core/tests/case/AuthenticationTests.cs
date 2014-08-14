using NUnit.Framework;
using System;
using System.Threading.Tasks;
using checkin.core.models;
using checkin.core.events;
using checkin.core.auth;
using checkin.core.flow;

namespace checkin.core
{
    [TestFixture, Description ("AuthenticationInput")]
    public class AuthenticationTests
    {
        [Test, Description ("認証情報入力部分. configureでloginnameとloginpassword取得")]
        public void TestAuthentcationInput__PrepareAsync__Setvalue ()
        {
            var resource = new Resource ();
            ICase target = new CaseAuthInput (resource);

            var t = Task.Run (async () => {
                RequestBroker broker = new RequestBroker (new FlowManager ()); //hmm.
                broker.Event = new AuthenticationEvent ("*username*", "*password*");
                await target.PrepareAsync (broker.GetInternalEvent ());
                await target.VerifyAsync ();

                Assert.AreEqual ("*username*", (target as CaseAuthInput).LoginName);
                Assert.AreEqual ("*password*", (target as CaseAuthInput).LoginPassword);

            });
            t.Wait ();
        }
    }

    [TestFixture, Description ("AuthenticationDataFetch")]
    public class AuthenticaionFetchDataTests
    {
        [Test, Description ("認証情報入力した後のvalidation. successした時AuthInfoが取得できる")]
        public void TestAuthenticationInput__Verify__True__Get__AuthInfo ()
        {
            var resource = new Resource ();
            var inputUsername = "*username*";
            var inputPassword = "*password*";
            resource.Authentication = new FakeAuthentication (resource, inputUsername, inputPassword);
            
            CaseAuthDataFetch target = new CaseAuthDataFetch (
                                           resource,
                                           inputUsername, 
                                           inputPassword);
            var t = Task.Run (async () => {
                var ev = new AuthenticationEvent (inputUsername, inputPassword);
                await target.PrepareAsync (ev);
                Assert.IsTrue (await target.VerifyAsync ());
                ev.HandleEvent ();
                Assert.IsNotNull (resource.AuthInfo);
            });
            t.Wait ();
        }
    }
}

