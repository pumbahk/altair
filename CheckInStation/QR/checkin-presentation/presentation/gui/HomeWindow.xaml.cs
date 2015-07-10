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
using System.Windows.Shapes;
using checkin.presentation.support;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// HomeWindow.xaml の相互作用ロジック
    /// </summary>
    public partial class HomeWindow : Window
    {
        public HomeWindow()
        {
            this.Title = "CheckInStation Version" + ApplicationVersion.GetApplicationInformationalVersion();
            InitializeComponent();
            this.PreviewKeyDown += new KeyEventHandler(HandleEsc);
        }

        private void HandleEsc(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Escape)
            {
                this.Close();
            }
        }
    }
}
