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
using System.Windows.Input;

namespace checkin.presentation.gui.page
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : NavigationWindow
    {
        public MainWindow()
        {
            InitializeComponent();
            this.PreviewKeyDown += new KeyEventHandler(HandleEsc);

            //disable IME!!!!!!!!!!!!
            InputMethod.Current.ImeState = InputMethodState.Off;
        }

        private void Shutdown()
        {
           // this.Close();
            Application.Current.Shutdown();
        }

        private void HandleEsc(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Escape)
            {
                this.Shutdown();
            }
        }

        private void MenuItem_Close(object sender, RoutedEventArgs e)
        {
            this.Shutdown();
        }
    }
}
