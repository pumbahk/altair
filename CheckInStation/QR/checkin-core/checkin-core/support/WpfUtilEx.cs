using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin_core.support
{
    public class UIElement : IEnumerable<UIElement>
    {
        private List<UIElement> children = new List<UIElement>();
        public int VisualChildrenCount { get { return children.Count; } }
        public UIElement GetVisualChild(int i) { return children[i]; }

        public UIElement() { }
        public UIElement(IEnumerable<UIElement> e) { children.AddRange(e); }

        public void Add(UIElement n) { children.Add(n); }
        public IEnumerator<UIElement> GetEnumerator() { return children.GetEnumerator(); }
        System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator() { return children.GetEnumerator(); }
    }

    public static class WpfUtilEx
    {
        public static UIElement FindVisualChild<T>(UIElement searchFrom) where T : UIElement
        {
            if (searchFrom is T)
            {
                return searchFrom;
            }
            var numChildren = searchFrom.VisualChildrenCount;
            for (int i = 0; i < numChildren; i++)
            {
                var r = FindVisualChild<T>(searchFrom.GetVisualChild(i));
                if (r != null)
                {
                    return r;
                }
            }
            return null;
        }

    }
}
