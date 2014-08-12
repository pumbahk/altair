using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using checkin.presentation.gui.control;

namespace checkin.presentation.gui
{
    /// <summary>
    /// ErrorMessageが変更されたときにエラーダイアログを表示させる
    /// </summary>
    public class BindingErrorDialogAction
    {
        public MessageDialog ErrorDialog { get; set; }
        public InputDataContext Context { get; set; }
        public BindingErrorDialogAction(InputDataContext ctx, MessageDialog dialog)
        {
            this.ErrorDialog = dialog;
            this.Context = ctx;          
        }

        public void Bind()
        {
            this.Context.PropertyChanged += OnHasErrorMessageShowDialog;
            this.ShowDialogIfNeed();
        }

        public void OnHasErrorMessageShowDialog(object sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (e.PropertyName == "ErrorMessage")
            {
                this.ShowDialogIfNeed();
            }
        }

        public void ShowDialogIfNeed()
        {
            if (this.Context.ErrorMessage != "")
            {
                this.ErrorDialog.Show();
            }
        }
    }
}
