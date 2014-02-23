using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WpfKb.LogicalKeys;

namespace vkeyboard.logicalkeys
{
    public class ComboKey : LogicalKeyBase
    {
        private readonly ICollection<ILogicalKey> keys;

        public ComboKey(ICollection<ILogicalKey> keys, string displayName)
        {
            this.DisplayName = displayName;
            this.keys = keys;
        }

        public override void Press()
        {
            foreach (var k in this.keys)
            {
                k.Press();
            }
        }
    }
}
