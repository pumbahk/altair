using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Diagnostics;

namespace TECImageWriterGateway
{
    class BlockingQueue<T>
    {
        private Queue<T> c = new Queue<T>();

        public int Count
        {
            get { return c.Count; }
        }

        public void Enqueue(T item)
        {
            Monitor.Enter(c);
            try
            {
                c.Enqueue(item);
                Monitor.Pulse(c);
            }
            finally
            {
                Monitor.Exit(c);
            }
        }

        public T Poll()
        {
            return Poll(0);
        }

        public T Poll(int timeout)
        {
            Monitor.Enter(c);
            try
            {
                if (c.Count == 0)
                {
                    if (timeout > 0)
                    {
                        if (!Monitor.Wait(c, timeout))
                            return default(T);
                    }
                    else
                    {
                        if (!Monitor.Wait(c))
                            return default(T);
                    }
                }
                Debug.Assert(c.Count > 0);
                return c.Dequeue();
            }
            finally
            {
                Monitor.Exit(c);
            }
        }
    }
}
