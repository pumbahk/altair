using System;

using checkin.core.models;
using checkin.core.flow;

namespace checkin.core.message
{
    public static class MessageResourceUtil
    {
        public static string GetRefreshPassword(this IResource resource)
        {
            return resource.SettingValue("refresh.password.format.0");
        }

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

        public static string GetInvalidInputMessage (this IResource resource)
        {
            return resource.SettingValue ("message.invalid.input.format.0");
        }

        public static string GetInvalidOutputMessage (this IResource resource)
        {
            return resource.SettingValue ("message.invalid.output.format.0");
        }

        public static string GetDefaultErrorMessage (this IResource resource)
        {
            return resource.SettingValue ("message.default.error.format.0");
        }

        public static string GetGuessTimeoutErrorMessage (this IResource resource)
        {
            return resource.SettingValue("message.guess.timeout.error.format.0");
        }

        public static string GetCaseDescriptionMessage(this IResource resource, ICase case_)
        {
            {
                //e.g. QR.CaseAuthInput.description.format.0
                var k = String.Format("message.{0}.description.format.0", case_.GetType().ToString());
                var r = resource.SettingValue(k);
                if (r == null)
                {
                    return "<説明が設定されていません>";
                }
                return r;
            }
        }

        public static string GetTokenStatusMessage (this IResource resource, TokenStatus tokenStatus)
        {
            switch (tokenStatus) {
            case TokenStatus.valid:
                throw new InvalidOperationException ("don't call with valid token.");
            case TokenStatus.printed:
                return resource.SettingValue ("message.token.status.printed.format.0");
            case TokenStatus.canceled:
                return resource.SettingValue ("message.token.status.canceled.format.0");
            case TokenStatus.before_start:
                return resource.SettingValue ("message.token.status.before_start.format.0");
            case TokenStatus.after_end:
                return resource.SettingValue ("message.token.status.after_end.format.0");
            case TokenStatus.not_supported:
                return resource.SettingValue ("message.token.status.not_supported.format.0");
            case TokenStatus.over_print_limit:
                return resource.SettingValue("message.token.status.over_print_limit.format.0");
            default:
                return resource.SettingValue ("message.token.status.unknown.format.0");
            }
        }
    }
}

