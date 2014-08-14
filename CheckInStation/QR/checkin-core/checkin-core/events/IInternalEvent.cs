using System;
using System.Windows.Threading;

namespace checkin.core.events
{
    /// <summary>
    /// I internal event. the Event from presentation layer;
    /// </summary>
    public interface IInternalEvent
    {
        void HandleEvent ();
        void HandleEvent (Action<string> useAction);        
        bool NotifyFlushMessage (string message);
        string ShorthandError { get; set; }
        string GetMessageString();
        InternalEventStaus Status { get; set; }
        Dispatcher CurrentDispatcher { get; set; }
    }

    public enum InternalEventStaus
    {
        failure,
        success,
    }
}

