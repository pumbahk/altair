using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using QR.message;

namespace QR
{
    using NG = Failure<string, bool>;

    public class ModelValidation : IModelValidation
    {
        public static Success<string, bool> OK = new Success<string, bool>(true);

        public message.ResultTuple<string, bool> ValidateAuthLoginName(string name)
        {
            if (name.Equals(""))
                return new NG("名前が未入力です。入力してください");
            else
                return OK;
        }

        public message.ResultTuple<string, bool> ValidateAuthPassword(string password)
        {
            if (password.Equals(""))
                return new NG("パスワードが未入力です。入力してください");
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

        public message.ResultTuple<string, bool> ValidateOrderno(string orderno)
        {
            if (orderno == null)
                return new NG("購入時の予約番号を入力してください(例 RE0101010101)");
            if (orderno.Length != 12)
                return new NG("予約番号は数字アルファベット大文字12桁です(例 RE0101010101)");
            return OK;
        }

        public message.ResultTuple<string, bool> ValidateTel(string tel)
        {
            int n;
            if (tel == null || tel == "")
                return new NG("電話番号を入力してください");
            if (!int.TryParse(tel, out n))
            {
                return new NG("電話番号は数字のみです");
            }
            return OK;            
        }
    }
}
