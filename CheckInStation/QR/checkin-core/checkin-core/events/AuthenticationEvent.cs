using System;
using System.Collections.Generic;

namespace checkin.core.events
{
    public class AuthenticationEvent :AbstractEvent,IInternalEvent
    {
        public string LoginName{ get; set; }

        public string LoginPassword{ get; set; }

        public string ValidationErrorMessage{ get; set; }

        public AuthenticationEvent (string name, string password) : base ()
        {
            LoginName = name;
            LoginPassword = password;
        }

        public AuthenticationEvent () : base ()
        {
        }

        public void AuthenticationFailure (string message)
        {
            //ここは非同期にする必要ないのかー。
            ValidationErrorMessage = message;
        }
    }
}

