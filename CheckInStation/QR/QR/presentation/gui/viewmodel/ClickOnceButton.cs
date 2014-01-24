using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using System.Windows.Threading;

namespace QR.presentation.gui
{
    public class ClickOnceButton : Button
    {

        volatile bool isProcessing;

        protected override void OnClick()
        {
            if (isProcessing) return;   //処理中ならOnClickを実行せずに終了

            isProcessing = true;

            base.OnClick();

            this.Dispatcher.InvokeAsync(new Action(() =>
            {
                isProcessing = false;

            }), DispatcherPriority.ApplicationIdle);
        }
    }
}
