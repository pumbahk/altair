using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using vkeyboard.logicalkeys;
using WindowsInput;
using WpfKb.Controls;
using WpfKb.LogicalKeys;

namespace vkeyboard.viewmodel
{

    public class ClearKeysPad : UniformOnScreenKeyboard
    {
        public ClearKeysPad()
            : base()
        {
            ICollection<ILogicalKey> allClearKeys = new ILogicalKey[] {
                new ChordKey("",VirtualKeyCode.CONTROL, VirtualKeyCode.VK_A),
                new VirtualKey(VirtualKeyCode.BACK,"")
            };

            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 0, Key = new VirtualKey(VirtualKeyCode.BACK, "1文字" + Environment.NewLine + "クリア") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 1, Key = new ComboKey(allClearKeys, "すべて" + Environment.NewLine + "クリア") });

            foreach (var k in Keys)
            {
                k.Layout = new KeyPadKeyLayout(k, InnerTextCreate.TwoLineText);
            }
        }
    }
}
