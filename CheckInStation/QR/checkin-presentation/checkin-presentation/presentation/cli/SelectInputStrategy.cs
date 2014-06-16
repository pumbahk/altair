using System;
using System.Threading.Tasks;
using checkin.core;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.presentation.cli
{
    public class SelectInputStrategy
    {
        public RequestBroker RequestBroker { get; set; }

        public ICase Case { get; set; }

        public SelectInputStrategy (RequestBroker broker, ICase case_)
        {
            RequestBroker = broker;
            Case = case_;            
        }

        public async Task<ICase> Run ()
        {
            ICase result;
            var ev = new SelectInputStragetyEvent ();
            do {        
                Console.WriteLine ("------input unit select: (0:qr, 1:order_no)-----");
                ev.InputUnitString = Console.ReadLine ();
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
            } while(ev.Status == InternalEventStaus.failure);
            return result;
        }
    }
}

