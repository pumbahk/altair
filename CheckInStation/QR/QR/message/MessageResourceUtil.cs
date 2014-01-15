using System;

namespace QR.message
{
	public static class MessageResourceUtil
	{
		public static string GetTaskCancelMessage (this IResource resource)
		{
			return resource.SettingValue ("message.task.cancel.format.0");
		}

		public static string GetLoginFailureMessageFormat (this IResource resource)
		{
			return resource.SettingValue ("message.auth.failure.format.0");
		}

		public static string GetWebExceptionMessage (this IResource resource)
		{
			return resource.SettingValue ("message.web.exception.format.0");
		}

		public static string GetInvalidInputMessage(this IResource resource)
		{
			return resource.SettingValue ("message.invalid.input.format.0");
		}

		public static string GetInvalidOutputMessage(this IResource resource)
		{
			return resource.SettingValue ("message.invalid.output.format.0");
		}

		public static string GetDefaultErrorMessage(this IResource resource)
		{
			return resource.SettingValue ("message.default.error.format.0");
		}
	}
}

