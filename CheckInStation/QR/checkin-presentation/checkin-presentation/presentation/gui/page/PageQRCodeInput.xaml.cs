using NLog;
using System;
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
using checkin.core.support;
using checkin.core.events;
using checkin.core.flow;

namespace checkin.presentation.gui.page
{

    class PageQRCodeInputDataContext : InputDataContext
    {
        public PageQRCodeInputDataContext(Page page): base(page){}

        private string _QRCode;
        public string QRCode
        {
            get { return this._QRCode; }
            set { this._QRCode = value; this.OnPropertyChanged("QRCode"); }
        }

        private Visibility _IsWaiting;
        public Visibility IsWaiting
        {
            get { return this._IsWaiting; }
            set { this._IsWaiting = value; this.OnPropertyChanged("IsWaiting"); }
        }

        private Visibility _IsIdle;
        public Visibility IsIdle
        {
            get { return this._IsIdle; }
            set { this._IsIdle = value; this.OnPropertyChanged("IsIdle"); }
        }

        private string _DescriptionInfo;
        public string DescriptionInfo
        {
            get { return this._DescriptionInfo; }
            set { this._DescriptionInfo = value; this.OnPropertyChanged("DescriptionInfo"); }
        }
        public override void OnSubmit()
        {
            var ev = this.Event as QRInputEvent;
            ev.QRCode = this.QRCode;
            this.QRCode = ""; //QRのsubmitに失敗した時のことを見越して空にしておく
            base.OnSubmit();
        }
        private Visibility _refreshModeVisibility;
        public Visibility RefreshModeVisibility
        {
            get { return this._refreshModeVisibility; }
            set { this._refreshModeVisibility = value; this.OnPropertyChanged("RefreshModeVisibility"); }
        }

        private string _subDescription;
        public string SubDescription
        {
            get { return this._subDescription; }
            set
            {
                this._subDescription = value;
                this.OnPropertyChanged("SubDescription");
            }
        }
    }


    /// <summary>
    /// Interaction logic for PageQRCodeInput.xaml
    /// </summary>
    public partial class PageQRCodeInput : Page//, IDataContextHasCase
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public PageQRCodeInput()
        {
            InitializeComponent();
            //disable IME!!!!!!!!!!!!
            InputMethod.Current.ImeState = InputMethodState.Off;

            this.DataContext = this.CreateDataContext();
            logger.Info("!initialize page: {0}, context: {1}, event: {2}, case: ".WithMachineName(), this, this.DataContext, (this.DataContext as PageQRCodeInputDataContext).Event, (this.DataContext as PageQRCodeInputDataContext).Case);
        }

        private InputDataContext CreateDataContext()
        {
            return new PageQRCodeInputDataContext(this)
            {
                Broker = AppUtil.GetCurrentBroker(),
                Event = new QRInputEvent(),
                IsWaiting = Visibility.Hidden,
                IsIdle = Visibility.Visible,
                RefreshModeVisibility = Visibility.Hidden,
            };
        }

        private async void OnLoaded(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageQRCodeInputDataContext;
            await ctx.PrepareAsync().ConfigureAwait(true);
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
            if (AppUtil.GetCurrentResource().RefreshMode)
            {
                ctx.RefreshModeVisibility = Visibility.Visible;
            }
            new BindingErrorDialogAction(ctx, this.ErrorDialog).Bind();
            ctx.DescriptionInfo = "QRリーダーにQRコードをかざしてください";
            this.buttonsubmit.Visibility = Visibility.Hidden;
        }

        private async void OnSubmitWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as PageQRCodeInputDataContext;
            logger.Info("PRessed!!".WithMachineName());
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                ctx.QRCode = this.QRCodeInput.Text;
                //QRのsubmitに失敗した時のことを見越して空にしておく            
                this.QRCodeInput.Text= "";
                var case_ = await ctx.SubmitAsync();
                ctx.TreatErrorMessage();              
                if (ctx.Event.Status == InternalEventStaus.success)
                {
                    case_ = await ctx.SubmitAsync();
                    ctx.TreatErrorMessage();

                    if (ctx.Event.Status == InternalEventStaus.failure)
                    {
                        ctx.IsIdle = Visibility.Visible;
                        ctx.IsWaiting = Visibility.Hidden;
                        this.LoadingAdorner.HideAdorner();
                        ctx.DescriptionInfo = "QRリーダーにQRコードをかざしてください";
                        /*
                        var ctx_ = new PageConfirmAllDataContext(this)
                        {
                            Broker = AppUtil.GetCurrentBroker(),
                            Status = ConfirmAllStatus.starting
                        };
                        ctx_.Event = new ConfirmAllEvent() { StatusInfo = ctx_ };
                        case_ = await ctx_.SubmitAsync();
                        ctx_.TreatErrorMessage();
                         * */
                    }
                     
                }
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }

        private async void OnBackwardWithBoundContext(object sender, RoutedEventArgs e)
        {
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                var case_ = await ctx.BackwardAsync();
                ctx.TreatErrorMessage();
                AppUtil.GetNavigator().NavigateToMatchedPage(case_, this);
            });
        }

        private void OnKeyDownHandler(object sender, KeyEventArgs e)
        {
            this.LoadingAdorner.ShowAdorner();
            var ctx = this.DataContext as PageQRCodeInputDataContext;
            ctx.IsIdle = Visibility.Hidden;
            ctx.DescriptionInfo = "しばらくお待ちください";
            if (this.QRCodeInput.Text.Length < 60)
            {
                ctx.Description = "QRコードを読込中です";
                ctx.SubDescription = "読み込みに時間がかかる場合は\r\nもう一度最初からやり直してQRコードをしっかりかざしてください";
                ctx.IsWaiting = Visibility.Visible;
            }
            if (this.QRCodeInput.Text.Length >= 60)
            {
                this.buttonsubmit.Visibility = Visibility.Visible;
            }
            if (e.Key == Key.Return)
            {
                ctx.SubDescription = "";
                this.Dispatcher.InvokeAsync(() => {
                    this.OnSubmitWithBoundContext(this, new RoutedEventArgs());
                });
            }
        }

        private async void OnGotoAnotherMode(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                AppUtil.GotoWelcome(this);
            });
        }

        private async void OnGotoWelcome(object sender, RoutedEventArgs e)
        {
            e.Handled = true;
            var ctx = this.DataContext as InputDataContext;
            await ProgressSingletonAction.ExecuteWhenWaiting(ctx, async () =>
            {
                AppUtil.GotoWelcome(this);
            });
        }

        private void ErrorDialog_MessageDialogComplete(object sender, RoutedEventArgs e)
        {
            this.QRCodeInput.Focus();
        }
    }
}
