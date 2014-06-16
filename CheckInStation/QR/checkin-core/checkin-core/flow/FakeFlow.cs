using System;
using System.Threading.Tasks;
using checkin.core.events;

namespace checkin.core.flow
{
    class FakeFlow : Flow
    {
        public IInternalEvent PresentationChanel { get; set; }
        public FakeFlow (FlowManager manager, ICase _case) : base (manager, _case)
        {
            this.PresentationChanel = new EmptyEvent ();
        }

        public bool VerifyStatus{ get; set; }

        public override Task PrepareAsync ()
        {
            //ここでは詳細に触れない。
            return Task.Run (() => {
                this.Case.PresentationChanel = new EmptyEvent ();
            });
        }

        public override Task<bool> VerifyAsync ()
        {
            return Task.Run (() => {
                return VerifyStatus;
            });
        }

        public override async Task<IFlow> Forward ()
        {
            var nextCase = await NextCase ();
            return new FakeFlow (Manager, nextCase);
        }
    }
}

