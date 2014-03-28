using WindowsInput;
using WpfKb.Controls;
using WpfKb.LogicalKeys;

namespace vkeyboard.viewmodel
{
   
    public class TenKeyPad : UniformOnScreenKeyboard
    {
        private VirtualCapsLockKeyFactory env;
        public VirtualCapsLockKeyFactory Env
        {
            get { return this.env; }
            set
            {
                this.env = value;
                this.UpdateKeyMap();
            }
        }

        private void UpdateKeyMap()
        {
            var ks = this.Env.OnTenKeyPadEnhanced();
            foreach (var k in ks)
            {
                k.Layout = new KeyPadKeyLayout(k);
            }

            this.Keys = ks;
        }

        public TenKeyPad()
            : base()
        {

            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 0, Key = new VirtualKey(VirtualKeyCode.VK_7, "7") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 1, Key = new VirtualKey(VirtualKeyCode.VK_8, "8") });
            Keys.Add(new OnScreenKey { GridRow = 0, GridColumn = 2, Key = new VirtualKey(VirtualKeyCode.VK_9, "9") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 0, Key = new VirtualKey(VirtualKeyCode.VK_4, "4") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 1, Key = new VirtualKey(VirtualKeyCode.VK_5, "5") });
            Keys.Add(new OnScreenKey { GridRow = 1, GridColumn = 2, Key = new VirtualKey(VirtualKeyCode.VK_6, "6") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 0, Key = new VirtualKey(VirtualKeyCode.VK_1, "1") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 1, Key = new VirtualKey(VirtualKeyCode.VK_2, "2") });
            Keys.Add(new OnScreenKey { GridRow = 2, GridColumn = 2, Key = new VirtualKey(VirtualKeyCode.VK_3, "3") });
            Keys.Add(new OnScreenKey { GridRow = 3, GridColumn = 1, Key = new VirtualKey(VirtualKeyCode.VK_0, "0") });

            foreach (var k in Keys)
            {
                k.Layout = new KeyPadKeyLayout(k);
            }
        }
    }
}
