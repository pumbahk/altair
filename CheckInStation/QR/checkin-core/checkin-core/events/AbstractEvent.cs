using System;
using System.Collections.Generic;
using NLog;
using System.Windows.Threading;

namespace checkin.core.events
{
    public abstract class AbstractEvent
    {
        protected static Logger logger = LogManager.GetCurrentClassLogger();

        public Dispatcher CurrentDispatcher { get; set; }

        public List<string> messages;

        public string ShorthandError {get;set;}

        public virtual string GetMessageFormat ()
        {
            return "{0}";
        }

        public InternalEventStaus Status { get; set; }

        public AbstractEvent ()
        {
            messages = new List<string> ();
        }

        public bool NotifyFlushMessage (string message)
        {
            messages.Add (message);
            return true;
        }

        public void HandleEvent ()
        {
            foreach (var m in messages) {
                Console.WriteLine (GetMessageFormat (), m);
            }
            messages.Clear ();
        }

        public void HandleEvent(Action<string> useAction)
        {
             foreach (var m in messages) {
                useAction(String.Format(GetMessageFormat(), m));
            }
            messages.Clear ();
        }

        public string GetMessageString()
        {
            return string.Join(Environment.NewLine, this.messages);
        }
    }
}

