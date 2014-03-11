using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WpfKb.Controls;

namespace vkeyboard.viewmodel
{
    public class ModifyKeysPad : UniformOnScreenKeyboard
    {
        private VirtualCapsLockKeyFactory env;
        public VirtualCapsLockKeyFactory Env
        {
            get { return this.env; }
            set
            {
                var ks = new ObservableCollection<OnScreenKey>();
                this.env = value;
                var k = new OnScreenKey() { GridRow = 0, GridColumn = 0, Key = this.env.CreateToggleStateKey() };
                k.Layout = new KeyPadKeyLayout(k, InnerTextCreate.TwoLineText);
                ks.Add(k);
                this.Keys = ks;
            }
        }

        public ModifyKeysPad()
            : base()
        {
        }
    }
}
