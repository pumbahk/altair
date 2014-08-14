using checkin.core.support;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using checkin.core.events;

namespace checkin.core.flow
{
    /// <summary>
    /// 画面遷移しないエラーに対応するためのadhocなクラス
    /// </summary>
    public class AggregateShorthandError
    {
        public bool IsShortHandError { get; set; }
        public readonly IInternalEvent ev;
        public AggregateShorthandError(IInternalEvent ev)
        {
            this.ev = ev;
        }

        public void Parse(string s)
        {
            this.ev.NotifyFlushMessage(s);

            if (EnsureResponse.HasSpecificErrorMessage(s))
            {
                this.ev.ShorthandError = s;
                this.IsShortHandError = true;
            }
            else
            {
                this.IsShortHandError = false;
            }
        }

        public ICase Redirect(IFlow flow)
        {
            var t = flow.Manager.Backward();
            t.Wait(300); //xxxx:
            return t.Result;
        }
    }
}
