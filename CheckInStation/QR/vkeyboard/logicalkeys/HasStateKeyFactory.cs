using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WpfKb.LogicalKeys;

namespace vkeyboard.logicalkeys
{
    public class HasStateKeyFactory<KeyState>
    {
        public readonly ICollection<HasStateKey<KeyState>> hasStateKeys;
        public readonly ICollection<ToggleStateKey<KeyState>> stateChangeKeys;
        public HasStateKeyFactory()
        {
            this.hasStateKeys = new List<HasStateKey<KeyState>>();
            this.stateChangeKeys = new List<ToggleStateKey<KeyState>>();
        }

        public HasStateKey<KeyState> CreateHasStateKey(IDictionary<KeyState, ILogicalKey> keys)
        {
            var k = new HasStateKey<KeyState>(keys);
            this.hasStateKeys.Add(k);
            return k;
        }

        public ToggleStateKey<KeyState> CreateToggleStateKey()
        {
            var k = new ToggleStateKey<KeyState>(this);
            this.stateChangeKeys.Add(k);
            return k;
        }

        public void OnPressed(KeyState s)
        {
            foreach (var k in this.hasStateKeys)
            {
                k.State = s;
            }
        }
    }
}
