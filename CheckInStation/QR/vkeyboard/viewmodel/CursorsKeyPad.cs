using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WindowsInput;
using WpfKb.Controls;
using WpfKb.LogicalKeys;

namespace vkeyboard.viewmodel
{ 
    public class CursorsKeyPad : UniformOnScreenKeyboard
    {
        public CursorsKeyPad()
            : base()
        {
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 0, Key = new VirtualKey(VirtualKeyCode.LEFT, "←") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 1, Key = new VirtualKey(VirtualKeyCode.RIGHT, "→") });

            foreach (var k in Keys)
            {
                k.Layout = new KeyPadKeyLayout(k);
            }
        }
    }
}
