using System;
using NLog;
using checkin.core.support;

namespace checkin.core.message
{
    public class EnumUtil
    {
        private static Logger logger = LogManager.GetCurrentClassLogger ();

        public static T ParseEnum<T> (string target)
        {
            return (T)Enum.Parse (typeof(T), target);
        }

        public static bool TryParseEnum<T> (string target, out T result)
        {
            try {
                result = EnumUtil.ParseEnum<T>(target);
                return true;
            } catch (ArgumentException) {
                logger.Error ("`{0}` is undefined value. default value {1} is selected.".WithMachineName(), target, default(T));
                result = default(T);
                return true;
            } catch (Exception e) {
                logger.ErrorException (":".WithMachineName(), e);
                result = default(T);
                return false;
            }
        }
    }
}

