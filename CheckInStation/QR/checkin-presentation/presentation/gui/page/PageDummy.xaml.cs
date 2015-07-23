using checkin.presentation.gui.control;
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

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// PageDummy.xaml の相互作用ロジック
    /// </summary>
    public partial class PageDummy : Page
    {
        public PageDummy()
        {
            InitializeComponent();
        }

        private void KeyPad_KeyPadFinish(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
        }

    }
}
