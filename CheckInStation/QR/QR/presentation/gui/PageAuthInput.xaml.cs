using System;
using System.Collections.Generic;
using System.Linq;
using System.Security;
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

namespace QR.presentation.gui
{
    public class AuthInputData
    {
        private PasswordBox input;
        public AuthInputData(PasswordBox input)
        {
            this.input = input;
        }
        public string LoginName { get; set; }
        public string LoginPassword { get { return this.input.Password; } }
    }

    /// <summary>
    /// Interaction logic for PageAuthInput.xaml
    /// </summary>
    public partial class PageAuthInput : Page
    {
        public PageAuthInput()
        {
            InitializeComponent();
            //PasswordBox is not Dependency Property. so.
            this.DataContext = new AuthInputData(this.PasswordInput);
        }

        private async void LoginButton_Click(object sender, RoutedEventArgs e)
        {
            //hmm.
            var data = this.DataContext as AuthInputData;
            var ev = new AuthenticationEvent()
            {
                LoginName = data.LoginName,
                LoginPassword = data.LoginPassword
            };
            //authInput
            await AppUtil.GetCurrentBroker().Submit(ev as IInternalEvent);
            await AppUtil.GetCurrentBroker().Submit(ev as IInternalEvent);
            MessageBox.Show(String.Format("name: {0}, password: {1}", data.LoginName, data.LoginPassword));
        }
    }
}
