using System;
using System.Threading.Tasks;
using checkin.core.message;
using checkin.core.models;

namespace checkin.core.auth
{
    public class FakeAuthentication :Authentication, IAuthentication
    {
        public string OrganizationId { get; set; }

        public string ExpectedName { get; set; }

        public string ExpectedPassword { get; set; }

        public FakeAuthentication (IResource resource, string expectedName, string expectedPassowrd) : base (resource)
        {
            ExpectedName = expectedName;
            ExpectedPassword = expectedPassowrd;
        }

        public override Task<ResultTuple<string, AuthInfo>> AuthAsync (string name, string password)
        {
            if (!ExpectedName.Equals (name) || !ExpectedPassword.Equals (password)) {
                //Console.WriteLine ("{0} - {1}", name, password);
                //Console.WriteLine("{0} - {1}", ExpectedName, ExpectedPassword);
                return Task.Run<ResultTuple<string,AuthInfo>> (() => OnFailure ());
            }
            return Task.Run<ResultTuple<string,AuthInfo>> (() => {
                return new Success<string,AuthInfo> (new AuthInfo (){ login = true });
            });
        }
    }
}

