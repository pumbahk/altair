using NUnit.Framework;
using System;
using checkin.core.message;
using checkin.core.models;
using checkin.core.events;

namespace checkin.core
{
    [TestFixture ()]
    public class TokenStatusMessageAppConfigTests
    {
        [Test, Description("refresh password")]
        public void TestRefreshPassword()
        {
            var resource = new Resource();
            var result = resource.GetRefreshPassword();
            Assert.AreNotEqual(default(string), result);
        }

        [Test, Description ("token status printed")]
        public void TestTokenStatusMessagePrinted ()
        {
            var resource = new Resource ();
            var result = resource.GetTokenStatusMessage (TokenStatus.printed);
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("token status canceled")]
        public void TestTokenStatusMessageCanceled ()
        {
            var resource = new Resource ();
            var result = resource.GetTokenStatusMessage (TokenStatus.canceled);
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description("token status before_start")]
        public void TestTokenStatusMessageBefore_Start()
        {
            var resource = new Resource();
            var result = resource.GetTokenStatusMessage(TokenStatus.before_start);
            Assert.AreNotEqual(default(string), result);
        }

        [Test, Description("token status after_end")]
        public void TestTokenStatusMessageAfter_End()
        {
            var resource = new Resource();
            var result = resource.GetTokenStatusMessage(TokenStatus.after_end);
            Assert.AreNotEqual(default(string), result);
        }

        [Test, Description ("token status not_support")]
        public void TestTokenStatusMessageNot_Support ()
        {
            var resource = new Resource ();
            var result = resource.GetTokenStatusMessage (TokenStatus.not_supported);
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("token status unknown")]
        public void TestTokenStatusMessageUnknown ()
        {
            var resource = new Resource ();
            var result = resource.GetTokenStatusMessage (TokenStatus.unknown);
            Assert.AreNotEqual (default(string), result);
        }
    }

    [TestFixture ()]
    public class GetMessageFromAppConfigTests
    {
        [Test, Description ("login failure message")]
        public void TestsGetLoginFailureMessage ()
        {
            var resource = new Resource ();
            var result = resource.GetLoginFailureMessageFormat ();
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("task canel message")]
        public void TestsGetTaskCancelMessage ()
        {
            var resource = new Resource ();
            var result = resource.GetTaskCancelMessage ();
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("web exception message")]
        public void TestsGetWebExceptionMessage ()
        {
            var resource = new Resource ();
            var result = resource.GetWebExceptionMessage ();
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("invalid input message")]
        public void TestsGetInvalidInputMessage ()
        {
            var resource = new Resource ();
            var result = resource.GetInvalidInputMessage ();
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("invalid output message")]
        public void TestsGetInvalidOutputMessage ()
        {
            var resource = new Resource ();
            var result = resource.GetInvalidOutputMessage ();
            Assert.AreNotEqual (default(string), result);
        }

        [Test, Description ("default error message")]
        public void TestsGetDefaultErrorMessage ()
        {
            var resource = new Resource ();
            var result = resource.GetDefaultErrorMessage ();
            Assert.AreNotEqual (default(string), result);
        }
    }
}

