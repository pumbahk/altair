using System;
using System.Threading.Tasks;
using checkin.core.flow;
using checkin.core;
using checkin.core.events;

namespace checkin.presentation.cli
{
    public class QRInput
    {
        public RequestBroker RequestBroker { get; set; }

        public ICase Case { get; set; }

        public QRInput (RequestBroker broker, ICase case_)
        {
            RequestBroker = broker;
            Case = case_;            
        }

        public async Task<ICase> Run ()
        {
            ICase result;
            var ev = new QRInputEvent ();
            var confirm_ev = new ConfirmOneEvent();
            do {
                Console.WriteLine ("------QRCode input---------");
                Console.Write ("qrcode:");
                ev.QRCode = Console.ReadLine ();
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
            } while(ev.Status == InternalEventStaus.failure);
            Console.WriteLine ("-------QRCode DataFetch *ticket data*--------");
            result = await RequestBroker.SubmitAsync (ev);
            ev.HandleEvent ();

            Console.WriteLine ("--------QRCode Confirm for one print unit select: 0:one, 1:all-------------------");
            confirm_ev.PrintUnitString = Console.ReadLine ();
            result = await RequestBroker.SubmitAsync (confirm_ev);
            ev.HandleEvent ();
            if (result is CasePrintForOne) {
                Console.WriteLine ("-------QRCode printing one (fetch *svg data*)-----");
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();

                Console.WriteLine ("-------QRCode after printed at--------------");
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
                return result;
            } else if (result is CaseQRConfirmForAll) {
                Console.WriteLine ("-------QRCode Confirm All-----");
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
                Console.WriteLine ("-------QRCode printing all (fetch *svg data*)-----");
                result = await RequestBroker.SubmitAsync (ev);

                Console.WriteLine ("-------QRCode after printed at--------------");
                result = await RequestBroker.SubmitAsync (ev);
                ev.HandleEvent ();
                return result;
            } else {
                throw new NotImplementedException ();
            }
        }
    }
}
