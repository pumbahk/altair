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

    public class AlphabetKeyPad : UniformOnScreenKeyboard
    {
        public AlphabetKeyPad()
            : base()
        {

            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 0, Key = new StringKey("A", "A") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 1, Key = new StringKey("B", "B") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 2, Key = new StringKey("C", "C") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 3, Key = new StringKey("D", "D") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 4, Key = new StringKey("E", "E") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 5, Key = new StringKey("F", "F") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 6, Key = new StringKey("G", "G") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 0, Key = new StringKey("H", "H") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 1, Key = new StringKey("I", "I") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 2, Key = new StringKey("J", "J") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 3, Key = new StringKey("K", "K") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 4, Key = new StringKey("L", "L") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 5, Key = new StringKey("M", "M") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 6, Key = new StringKey("N", "N") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 0, Key = new StringKey("O", "O") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 1, Key = new StringKey("P", "P") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 2, Key = new StringKey("Q", "Q") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 3, Key = new StringKey("R", "R") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 4, Key = new StringKey("S", "S") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 5, Key = new StringKey("T", "T") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 6, Key = new StringKey("U", "U") });
            Keys.Add(new OnScreenKey { GridRow = 3, GridColumn = 0, Key = new StringKey("V", "V") });
            Keys.Add(new OnScreenKey { GridRow = 3, GridColumn = 1, Key = new StringKey("W", "W") });
            Keys.Add(new OnScreenKey { GridRow = 3, GridColumn = 2, Key = new StringKey("X", "X") });
            Keys.Add(new OnScreenKey { GridRow = 3, GridColumn = 3, Key = new StringKey("Y", "Y") });
            Keys.Add(new OnScreenKey { GridRow = 3, GridColumn = 4, Key = new StringKey("Z", "Z") });

            foreach (var k in Keys)
            {
                k.Layout = new KeyPadKeyLayout(k);
            }
        }
    }
}
