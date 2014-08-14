using System;
using System.Runtime.Serialization;

/* {"login": true,
    "loginuser": {"type": "login",
        "id": unicode(operator.id),
        "name": operator.name},
    "organization": {"id": operator.organization_id}}
*/
namespace checkin.core.models
{
    [DataContract]
    public class AuthInfo
    {
        [DataMember]
        public bool login;
        [DataMember]
        public string loginname;
        //        [DataMember]
        //        public string secret;
        [DataMember]
        public string organization_code;
        [DataMember]
        public string device_id;
        [DataMember]
        public string organization_id;

        public AuthInfo (dynamic json)
        {
            login = json.login;
            loginname = json.loginuser.name;
            organization_id = json.organization.id;
            organization_code = json.organization.code;
            device_id = json.identity.device_id;
        }

        public AuthInfo ()
        {
        }
    }
    //なんか付加するような操作が必要;
}

