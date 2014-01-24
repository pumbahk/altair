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

    class PageFinishDataContext : InputDataContext, INotifyPropertyChanged, IFinishStatusInfo
    {
        private FinishStatus _status;
        public FinishStatus Status
        {
            get { return this._status; }
            set { this._status = value; this.OnPropertyChanged("Status"); }
        }
        public BitmapImage AdImage { get; set; }

        public override void OnSubmit()
        {
            var ev = this.Event as IInternalEvent;
            base.OnSubmit();
        }
    }


    /// <summary>
    /// Interaction logic for PageFinish.xaml
    /// </summary>
    public partial class PageFinish : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageFinish()
        {
            InitializeComponent();
            this.DataContext = this.CreateDataContext();
        }

        private InputDataContext CreateDataContext()
        {
            var resource = AppUtil.GetCurrentResource();

            var ctx = new PageFinishDataContext()
            {
                AdImage =  resource.AdImageCollector.GetImage(),
                Broker = AppUtil.GetCurrentBroker(),
                Status = FinishStatus.starting
            };
            ctx.Event = new FinishEvent() { StatusInfo = ctx };
            ctx.PropertyChanged += OnStatusChangedSetRedirectCallback;
            return ctx;
        }

        void OnStatusChangedSetRedirectCallback(object sender, PropertyChangedEventArgs e)
        {
            var ctx = sender as PageFinishDataContext;
            if (e.PropertyName == "Status" && ctx.Status == FinishStatus.saved)
            {
                ctx.Status = FinishStatus.finished;
                this.Dispatcher.InvokeAsync(async () =>               
                {
                    await Task.Delay(500);
                    logger.Info(String.Format("stop case {0}", ctx.Broker.FlowManager.Peek()));
                    var case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();
                    AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
                });
            }
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            await (this.DataContext as PageFinishDataContext).VerifyAsync().ConfigureAwait(false);
        }
    }
}
