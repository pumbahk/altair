using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace checkin_presentation.presentation.gui.page
{
    /// <summary>
    /// Interaction logic for PagePrintingConfirm.xaml
    /// </summary>
    public partial class PagePrintingConfirm : Page
    {
        public PagePrintingConfirm()
        {
            InitializeComponent();
        }
        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            OnGotoNextPageStart();
        }

        private void OnGotoNextPageStart()
        {

        }
    }
}
