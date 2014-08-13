using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.models
{
    public class LoginUser
    {
        public string login_id { get; set; }

        public string password { get; set; }

        public string device_id { get; set; } //端末ごとにuniqueなid(e.g. xxxのPC)
    }
}
