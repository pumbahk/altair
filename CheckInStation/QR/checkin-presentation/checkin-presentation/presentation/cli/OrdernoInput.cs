using System;
using System.Threading.Tasks;
using checkin.core;
using checkin.core.flow;
using checkin.core.events;
using checkin.core;
using checkin.core.flow;
using checkin.core.events;

namespace checkin.presentation.cli
{
    public class OrdernoInput
    {
        public RequestBroker RequestBroker { get; set; }

        public ICase Case { get; set; }

        public OrdernoInput (RequestBroker broker, ICase case_)
        {
            RequestBroker = broker;
            Case = case_;            
        }

        public async Task<ICase> Run ()
        {
            ICase result;
            var ev = new OrdernoInputEvent ();
            do {
                Console.WriteLine ("------Orderno input---------");
                Console.Write ("Orderno:");
                ev.Orderno = Console.ReadLine ();
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
            } while(ev.Status == InternalEventStaus.failure);
            do {
                Console.WriteLine ("------TEL input---------");
                Console.Write ("TEL:");
                ev.Tel = Console.ReadLine ();
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
            } while(ev.Status == InternalEventStaus.failure);

            Console.WriteLine ("-------Orderno DataFetch *ticket data*--------");
            result = await RequestBroker.SubmitAsync (ev);
            ev.HandleEvent ();
            Console.WriteLine ("-------Orderno Confirm All-----");
            result = await RequestBroker.SubmitAsync (ev);
            ev.HandleEvent ();
            Console.WriteLine ("-------Orderno printing all (fetch *svg data*)-----");
            result = await RequestBroker.SubmitAsync (ev);

            Console.WriteLine ("-------Orderno after printed at--------------");
            result = await RequestBroker.SubmitAsync (ev);
            ev.HandleEvent ();
            return result;
        }
    }
}
