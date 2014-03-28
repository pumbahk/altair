using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using vkeyboard.logicalkeys;
using WpfKb.Controls;
using WpfKb.LogicalKeys;

namespace vkeyboard.viewmodel
{
    public class VirtualCapsLockKeyFactory : HasStateKeyFactory<VirtualCapsLockKeyState>
    {
        public HasStateKey<VirtualCapsLockKeyState> CreateHasStateKey(string first, string second, string third)
        {
            var dic = new Dictionary<VirtualCapsLockKeyState, ILogicalKey>(){
                {VirtualCapsLockKeyState.大文字, new StringKey(first, first)},
                {VirtualCapsLockKeyState.小文字, new StringKey(second, second)},
                {VirtualCapsLockKeyState.記号,   new StringKey(third, third)}
            };
            var k = new HasStateKey<VirtualCapsLockKeyState>(dic);
            this.hasStateKeys.Add(k);
            return k;
        }

        public ObservableCollection<OnScreenKey> OnAlphabetKeyPadEnhanced()
        {
            var ks = new ObservableCollection<OnScreenKey>();
            var env = this;
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 0, Key = env.CreateHasStateKey("A", "a", "!") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 1, Key = env.CreateHasStateKey("B", "b", @"""") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 2, Key = env.CreateHasStateKey("C", "c", "#") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 3, Key = env.CreateHasStateKey("D", "d", "$") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 4, Key = env.CreateHasStateKey("E", "e", "%") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 5, Key = env.CreateHasStateKey("F", "f", "&") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 6, Key = env.CreateHasStateKey("G", "g", "'") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 0, Key = env.CreateHasStateKey("H", "h", "(") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 1, Key = env.CreateHasStateKey("I", "i", ")") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 2, Key = env.CreateHasStateKey("J", "j", "-") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 3, Key = env.CreateHasStateKey("K", "k", "=") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 4, Key = env.CreateHasStateKey("L", "l", "^") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 5, Key = env.CreateHasStateKey("M", "m", "~") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 6, Key = env.CreateHasStateKey("N", "n", @"\") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 0, Key = env.CreateHasStateKey("O", "o", "|") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 1, Key = env.CreateHasStateKey("P", "p", "@") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 2, Key = env.CreateHasStateKey("Q", "q", "`") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 3, Key = env.CreateHasStateKey("R", "r", "[") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 4, Key = env.CreateHasStateKey("S", "s", "]") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 5, Key = env.CreateHasStateKey("T", "t", "{") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 6, Key = env.CreateHasStateKey("U", "u", "}") });
            ks.Add(new OnScreenKey { GridRow = 3, GridColumn = 0, Key = env.CreateHasStateKey("V", "v", "+") });
            ks.Add(new OnScreenKey { GridRow = 3, GridColumn = 1, Key = env.CreateHasStateKey("W", "w", ";") });
            ks.Add(new OnScreenKey { GridRow = 3, GridColumn = 2, Key = env.CreateHasStateKey("X", "x", "*") });
            ks.Add(new OnScreenKey { GridRow = 3, GridColumn = 3, Key = env.CreateHasStateKey("Y", "y", ":") });
            ks.Add(new OnScreenKey { GridRow = 3, GridColumn = 4, Key = env.CreateHasStateKey("Z", "z", "_") });
            return ks;
        }

        public ObservableCollection<OnScreenKey> OnTenKeyPadEnhanced()
        {
            var ks = new ObservableCollection<OnScreenKey>();
            var env = this;
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 0, Key = env.CreateHasStateKey("7", "7", ",") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 1, Key = env.CreateHasStateKey("8", "8", ".") });
            ks.Add(new OnScreenKey { GridRow = 0, GridColumn = 2, Key = env.CreateHasStateKey("9", "9", "<") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 0, Key = env.CreateHasStateKey("4", "4", ">") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 1, Key = env.CreateHasStateKey("5", "5", "/") });
            ks.Add(new OnScreenKey { GridRow = 1, GridColumn = 2, Key = env.CreateHasStateKey("6", "6", "?") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 0, Key = env.CreateHasStateKey("1", "1", "_") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 1, Key = env.CreateHasStateKey("2", "2", "") });
            ks.Add(new OnScreenKey { GridRow = 2, GridColumn = 2, Key = env.CreateHasStateKey("3", "3", "") });
            ks.Add(new OnScreenKey { GridRow = 3, GridColumn = 1, Key = env.CreateHasStateKey("0", "0", "") });
            return ks;
        }
    }
}
