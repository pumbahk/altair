using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WpfKb.LogicalKeys;

namespace vkeyboard.logicalkeys
{
    public class ToggleStateKey<KeyState> : LogicalKeyBase
    {
        private int stateIndex;
        private IList<KeyState> states;
        public readonly HasStateKeyFactory<KeyState> Env;
        public ToggleStateKey(HasStateKeyFactory<KeyState> env)
        {
            this.Env = env;
            this.stateIndex = 0;
            this.states = Enum.GetValues(typeof(KeyState)).Cast<KeyState>().ToList();
            this.UpdateIndex(this.stateIndex);
        }

        public override void Press()
        {
            this.stateIndex += 1;
            if (this.stateIndex >= this.states.Count)
            {
                this.stateIndex = 0;
            }
            this.UpdateIndex(this.stateIndex);
        }

        public void UpdateIndex(int i)
        {
            this.DisplayName = this.states[i].ToString();
            this.Env.OnPressed(this.states[this.stateIndex]);
        }
    }
}
