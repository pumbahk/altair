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

namespace QR.presentation.gui
{

    public class AuthInputDataContext : InputDataContext
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
            logger.Info(String.Format("Submit: Name:{0}, Password:{1}", ev.LoginName, ev.LoginPassword));
            base.OnSubmit();
        }
    }

    public class InputDataContext : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public RequestBroker Broker { get; set; }
        public IInternalEvent Event { get; set; }

        protected Logger logger = LogManager.GetCurrentClassLogger();

        protected virtual void OnPropertyChanged(string propName)
        {
            var handler = this.PropertyChanged;
            if (handler != null)
                handler(this, new PropertyChangedEventArgs(propName));
        }

        public ICase Case
        {
            get
            {
                var case_ = this.Broker.FlowManager.Peek().Case;
                logger.Debug(String.Format("Case: {0}", case_));
                return case_;  //なぜかこれを直接Bindingで呼び出したとき""が返るっぽい。
            }
        }

        public virtual void OnSubmit()
        {
        }

        public virtual async Task<ICase> Submit()
        {
            this.OnSubmit();
            var result = await this.Broker.Submit(this.Event).ConfigureAwait(false);
            this.OnPropertyChanged("CaseName");
            return result;
        }

        public string CaseName { get { return this.Case.ToString(); } }
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
            //hmm.
            var ctx = this.DataContext as InputDataContext;
            var case_ = await ctx.Submit();
            if (ctx.Event.Status == InternalEventStaus.success)
            {
                await ctx.Submit(); //Data Fetch
            }
            else
            {
                logger.Info("failure");
            }
           // MessageBox.Show(String.Format("name: {0}, password: {1}", ev.LoginName, ev.LoginPassword));
        }
    }
}
