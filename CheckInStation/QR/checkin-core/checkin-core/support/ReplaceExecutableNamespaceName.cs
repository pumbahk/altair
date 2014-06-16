using NLog;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace checkin.core.support
{
    /// <summary>
    /// XamlReaderで読み込む文字列中でこのアプリのnamespaceで定義されているクラスを使うために変換する。
    /// e.g. xmlns:c="clr-namespace:@ns@.control;assembly=@ns@"
    /// => xmlns:c="clr-namespace:App.control;assembly=App"
    /// </summary>
    public static class ReplaceExecutableNamespaceName
    {
        private static Logger logger = LogManager.GetCurrentClassLogger();

        public static string Name = null;
        public static string FullName = null;

        public static string Replace(string target)
        {
            return Replace(target, "@ns@");
        }

        public static string Replace(string target, string pattern)
        {
            return target.Replace(pattern, GetName());
        }

        public static string GetName()
        {
            if (Name == null)
            {
                var a = System.Reflection.Assembly.GetExecutingAssembly();
                FullName = a.FullName;

                var d = FullName.IndexOf(",");
                if(d > 0){
                    Name = FullName.Substring(0, d);
                } else {
                    logger.Warn("anything is wrong?(Name={0}, FullName={1})".WithMachineName(), Name, FullName);
                    Name = FullName;
                }
                logger.Info("Getting application name: Name={0}".WithMachineName(), Name);
            }
            return Name;
        }
    }
}
