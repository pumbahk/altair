using System;

namespace QR
{
	public class MessageResourceUtil
	{
		public static string GetTaskCancelMessage (IResource resource)
		{
			return resource.SettingValue ("message.task.cancel.format.0");
		}

		public static string GetLoginFailureMessageFormat (IResource resource)
		{
			return resource.SettingValue ("message.auth.failure.format.0");
		}

		public static string GetWebExceptionMessage (IResource resource)
		{
			return resource.SettingValue ("message.web.exception.format.0");
		}
	}
}

