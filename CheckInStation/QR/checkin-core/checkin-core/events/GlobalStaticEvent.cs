using System;
using System.Collections.Generic;
using System.Diagnostics.Tracing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace checkin.core.events
{
    public class DescriptionMessageEventArgs : EventArgs
    {
        public readonly string Message;
        public DescriptionMessageEventArgs(string message)
        {
            this.Message = message;
        }
    }
    public delegate void DescriptionMessageEventHandler(object sender, DescriptionMessageEventArgs e);

    public static class GlobalStaticEvent
    {
        public static event DescriptionMessageEventHandler DescriptionMessageEvent;

        public static void FireDescriptionMessageEvent(object sender, string message)
        {
            var ev = DescriptionMessageEvent;
            if (ev != null)
            {
                ev(sender, new DescriptionMessageEventArgs(message));
            }
        }
    }
}
