using System;
using System.Threading.Tasks;
using checkin.core;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.presentation.cli
{
    public class AuthInput
    {
        public RequestBroker RequestBroker { get; set; }
        public ICase Case { get; set; }

        public AuthInput (RequestBroker broker, ICase case_)
        {
            RequestBroker = broker;
            Case = case_;            
        }

        public async Task<ICase> Run ()
        {
            ICase result;
            var ev = new AuthenticationEvent ();
            do {
                do {
                    Console.WriteLine ("------login input---------");
                    Console.Write ("name:");
                    ev.LoginName = Console.ReadLine ();
                    Console.Write ("password:");
                    ev.LoginPassword = Console.ReadLine ();
                    await RequestBroker.SubmitAsync (ev);
                    ev.HandleEvent ();
                } while(ev.Status == InternalEventStaus.failure);

                // requestn
                Console.WriteLine ("------login request---------");
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
            } while(ev.Status == InternalEventStaus.failure);
            return result;
        }
    }
}

