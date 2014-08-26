using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace checkin.presentation.gui.control
{      
    /// <summary>
    /// MessageDialog.xaml の相互作用ロジック
    /// </summary>
    public partial class MessageDialog : Popup, IDialog
    {
        public ICommand OpenCommand { get; private set; }
        public ICommand CloseCommand { get; private set; }

        public static readonly RoutedEvent MessageDialogCompleteEvent = EventManager.RegisterRoutedEvent(
            "MessageDialogComplete", RoutingStrategy.Direct, typeof(RoutedEventHandler), typeof(MessageDialog));

        public event RoutedEventHandler MessageDialogComplete
        {
            add { AddHandler(MessageDialogCompleteEvent, value); }
            remove { AddHandler(MessageDialogCompleteEvent, value); }
        }

        public void RaiseMessageDialogComplete()
        {
            var e = new RoutedEventArgs(MessageDialog.MessageDialogCompleteEvent);
            this.RaiseEvent(e);
        }

        public static readonly DependencyProperty MessageTextProperty =
        DependencyProperty.Register("MessageText", typeof(string), typeof(MessageDialog),
        new FrameworkPropertyMetadata("<MessageText>？"));


        public string MessageText
        {
            get { return (string)this.GetValue(MessageTextProperty); }
            set { this.SetValue(MessageTextProperty, value); }
        }

        public static readonly DependencyProperty ButtonTextProperty =
        DependencyProperty.Register("ButtonText", typeof(string), typeof(MessageDialog),
        new FrameworkPropertyMetadata("OK"));

        public string ButtonText
        {
            get { return (string)this.GetValue(ButtonTextProperty); }
            set { this.SetValue(ButtonTextProperty, value); }
        }

        public static Brush DefaultBackground = new SolidColorBrush() { Color = Colors.White, Opacity = 0.8 };
        public static readonly DependencyProperty BackgroundProperty =
        DependencyProperty.Register("Background", typeof(Brush), typeof(MessageDialog),
        new FrameworkPropertyMetadata(DefaultBackground));


        public Brush Background
        {
            get { return (Brush)this.GetValue(BackgroundProperty); }
            set { this.SetValue(BackgroundProperty, value); }
        }

        public static readonly DependencyProperty InnerBackgroundProperty =
        DependencyProperty.Register("InnerBackground", typeof(Brush), typeof(MessageDialog),
        new FrameworkPropertyMetadata(Brushes.AntiqueWhite));


        public Brush InnerBackground
        {
            get { return (Brush)this.GetValue(InnerBackgroundProperty); }
            set { this.SetValue(InnerBackgroundProperty, value); }
        }

        public void Show()
        {
            this.IsOpen = true;
        }

        public void Hide()
        {
            this.IsOpen = false;
        }

        public void OnCompleteClose(object sender, RoutedEventArgs e)
        {
            this.Hide();
        }

        public MessageDialog()
        {
            InitializeComponent();
            this.MessageDialogComplete += this.OnCompleteClose;
            this.OpenCommand = new DialogOpenCommand();
            this.CloseCommand = new DialogCloseCommand();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            this.RaiseMessageDialogComplete();
        }
    }
}
