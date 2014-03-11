using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using WpfKb.LogicalKeys;

namespace WpfKb.Controls
{
    public interface IScreenKeyLayout
    {
        void SetupControl(ILogicalKey key);
        void AnimateMouseDown();
        void AnimateMouseUp();
        void OnMouseEnter();
        void OnMouseLeave();
    }
}
