using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.support
{

    public static class WpfUtilEx
    {
        public static T FindVisualChild<T>(System.Windows.UIElement element) where T : System.Windows.UIElement
        {
            for (int i = 0; i < System.Windows.Media.VisualTreeHelper.GetChildrenCount(element); i++)
            {
                System.Windows.UIElement uIElement = (System.Windows.UIElement)System.Windows.Media.VisualTreeHelper.GetChild(element, i);
                if (uIElement != null)
                {
                    T t = uIElement as T;
                    if (t != null)
                    {
                        return t;
                    }
                    T t2 = WpfUtilEx.FindVisualChild<T>(uIElement);
                    if (t2 != null)
                    {
                        return t2;
                    }
                }
            }
            return default(T);
        }
    }
}
