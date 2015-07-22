using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using checkin.core;
using System.Windows;
using checkin.presentation.gui.viewmodel;
using System.Windows.Controls;
using checkin.presentation.gui.page;
using checkin.presentation.gui.control;
using checkin.core.flow;

namespace checkin.presentation.gui.command
{
    public class ReturnHomeCommand : ICommand
    {
        public readonly Page Wrapper;
        public ReturnHomeCommand(Page wrapper)
        {
            this.Wrapper = wrapper;
        }
        public ReturnHomeCommand()
        {
        }

        public bool CanExecute(object parameter)
        {
            return true;
        }

        public event EventHandler CanExecuteChanged;

        public void Execute(object parameter)
        {
            if(this.Wrapper != null)
            {
                if (this.Wrapper is PageConfirmAll)
                {
                    var p = this.Wrapper as PageConfirmAll;
                    if(p != null)
                    {
                        var ctx = p.DataContext as PageConfirmAllDataContext;
                        if (ctx != null && ctx.NumberOfSelectableTicket == 0)
                        {
                            AppUtil.GotoWelcome(this.Wrapper);
                            return;
                        }
                    }
                }
                else if (this.Wrapper is PageConfirmListOne)
                {
                    AppUtil.GotoWelcome(this.Wrapper);
                }
                else if(this.Wrapper is PageConfirmListAll)
                {
                    AppUtil.GotoWelcome(this.Wrapper);
                }
                else if(this.Wrapper is PageCloseConfirm)
                {
                    if (AppUtil.GetCurrentResource().FlowDefinition is OneStepFlowDefinition)
                    {
                        var r = AppUtil.GetCurrentResource();
                        var case_ = AppUtil.GetCurrentResource().FlowDefinition.AfterAuthorization(r);
                        AppUtil.GetNavigator().NavigateToMatchedPage(case_, this.Wrapper);
                    }
                    else
                    {
                        AppUtil.GotoWelcome(this.Wrapper);
                    }
                }
                else if(this.Wrapper is PageConfirmListPart)
                {
                    AppUtil.GotoWelcome(this.Wrapper);
                }
                else if(this.Wrapper is PageQRCodeInput)
                {
                    var p = this.Wrapper as PageQRCodeInput;
                    Button b = p.FindName("buttonsubmit") as Button;
                    if(b != null)
                    {
                        b.Visibility = Visibility.Hidden;
                    }
                    TextBox tb = p.FindName("QRCodeInput") as TextBox;
                    if (tb != null)
                    {
                        tb.Focus();
                    }
                }

                MessageDialog e = this.Wrapper.FindName("ErrorDialog") as MessageDialog;
                if (e != null)
                {
                    e.Hide();
                }
            }
        }

    }
}
