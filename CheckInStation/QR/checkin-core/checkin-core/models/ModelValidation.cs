using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using checkin.core.message;

namespace checkin.core.models
{
    using NG = Failure<string, bool>;

    public class ModelValidation : IModelValidation
    {
        public static Success<string, bool> OK = new Success<string, bool>(true);

        public message.ResultTuple<string, bool> ValidateAuthLoginName(string name)
        {
            if (name.Equals(""))
                return new NG("ユーザー名を正しく入力してください");
            else
                return OK;
        }

        public message.ResultTuple<string, bool> ValidateAuthPassword(string password)
        {
            if (password.Equals(""))
                return new NG("パスワードを正しく入力してください");
            else
                return OK;
        }

        public message.ResultTuple<string, bool> ValidateQRCode(string qrcode)
        {
            if (qrcode == null || qrcode == "")
                return new NG("値が入力されていません");
            else
                return OK;
        }

        public message.ResultTuple<string, bool> ValidateOrderno(string orderno, string organizationCode)
        {
            if (orderno == null)
                return new NG("購入時の受付番号を入力してください(例 " + organizationCode + "0101010101)");
            if (orderno.Length != 12)
                return new NG("受付番号は数字アルファベット大文字12桁です(例 " + organizationCode + "0101010101)");
            return OK;
        }

        public message.ResultTuple<string, bool> ValidateTel(string tel)
        {
            long n;
            if (tel == null || tel == "")
                return new NG("電話番号を入力してください");
            if (!long.TryParse(tel, out n))
            {
                return new NG("電話番号は数字のみです");
            }
            return OK;            
        }
    }
}
