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

namespace checkin.presentation.gui.command
{
    public class AppCloseCommand : ICommand
    {
        public readonly Page Wrapper;
        public AppCloseCommand(Page wrapper)
        {
            this.Wrapper = wrapper;
        }

        public bool CanExecute(object parameter)
        {
            return true;
        }

        public event EventHandler CanExecuteChanged;

        public void Execute(object parameter)
        {
            var resource = AppUtil.GetCurrentResource();
            if (resource.LoginUser == null)
            {
                this.Shutdown();
            }
            else
            {
                this.Wrapper.Dispatcher.InvokeAsync(() =>
                {
                    this.Wrapper.NavigationService.Navigate(new PageCloseConfirm());
                });
            }
        }

        public void Shutdown()
        {
            Application.Current.Shutdown();
        }
    }
}
