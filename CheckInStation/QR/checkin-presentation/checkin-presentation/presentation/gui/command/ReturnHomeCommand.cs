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
                if (this.Wrapper is PageConfirmListOne ||
                    this.Wrapper is PageConfirmListAll ||
                    this.Wrapper is PageConfirmListPart)
                {
                    AppUtil.GotoWelcome(this.Wrapper);
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
