using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace checkin.presentation.gui.page
{
    interface IDataContextHasCase
    {
        InputDataContext CreateDataContext();
        void OnLoad(object sender, RoutedEventArgs e);
        void OnSubmitWithDataContext(object sender, RoutedEventArgs e);
    }
}
