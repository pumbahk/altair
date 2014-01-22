using NLog;
using System;
using System.Collections.Generic;
using System.ComponentModel;
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

namespace QR.presentation.gui.page
{

    class AuthInputDataContext : InputDataContext
    {
        private PasswordBox input;
                
        public AuthInputDataContext(PasswordBox input)
        {
            this.input = input;
        }
        public string LoginName { get; set; }
        public string LoginPassword { get { return this.input.Password; } }

        public override void OnSubmit()
        {
            var ev = this.Event as AuthenticationEvent;
            ev.LoginName = this.LoginName;
            ev.LoginPassword = this.LoginPassword; //TODO:use seret string
            //logger.Info(String.Format("Submit: Name:{0}, Password:{1}", ev.LoginName, ev.LoginPassword));
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageAuthInput.xaml
    /// </summary>
    public partial class PageAuthInput : Page
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageAuthInput()
        {
            InitializeComponent();
            //PasswordBox is not Dependency Property. so.
            this.DataContext =new AuthInputDataContext(this.PasswordInput){
              Broker=AppUtil.GetCurrentBroker(),
              Event=new AuthenticationEvent()
            };
        }

        private async void LoginButton_Click(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.Submit();
            
            if (ctx.Event.Status == InternalEventStaus.success)
            {
                case_ = await ctx.Submit();
            }
            
            var coll = new List<string>();
            ctx.Event.HandleEvent((string s) =>
            {
                coll.Add(s);
            });
            ctx.ErrorMessage = String.Join(",", coll.ToArray<string>());

            AppUtil.GetNavigator().NavigateNextPage(case_, this);
        }
    }
}
