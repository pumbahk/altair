using System;
using NLog;

namespace QR
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
				logger.Error ("`{0}` is undefined value. default value {1} is selected.", target, default(T));
				result = default(T);
				return true;
			} catch (Exception e) {
				logger.ErrorException (":", e);
				result = default(T);
				return false;
			}
		}
	}
}

