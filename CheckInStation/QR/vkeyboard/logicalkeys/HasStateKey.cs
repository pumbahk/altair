using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WpfKb.LogicalKeys;

namespace vkeyboard.logicalkeys
{
    public class HasStateKey<KeyState> : LogicalKeyBase
    {
        private readonly IDictionary<KeyState, ILogicalKey> keymap;
        private KeyState state;
        public KeyState State
        {
            get { return this.state; }
            set
            {
                this.state = value;
                this.DisplayName = this.keymap[value].DisplayName;
            }
        }
        public HasStateKey(IDictionary<KeyState, ILogicalKey> keys)
        {
            this.keymap = keys;
            this.State = default(KeyState);
        }


        public override void Press()
        {
            this.keymap[this.State].Press();
        }
    }
}
