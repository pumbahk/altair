using System;
using System.Collections.Generic;
using System.ComponentModel;
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

namespace QR.presentation.gui.control
{
    public class KeyPadPopupContext : INotifyPropertyChanged
    {
        private string _InputString;

        public string InputString
        {
            get { return this._InputString; }
            set { this._InputString = value; this.OnPropertyChanged("InputString"); }
        }
        public event PropertyChangedEventHandler PropertyChanged;
        public void OnPropertyChanged(string name)
        {
            if (this.PropertyChanged != null)
            {
                this.PropertyChanged(this, new PropertyChangedEventArgs(name));
            }
        }
        //public bool EnableDebug { get; set; }
    }

    /// <summary>
    /// KeyPad.xaml の相互作用ロジック
    /// </summary>
    public partial class KeyPad : UserControl
    {
        public KeyPad()
        {
            InitializeComponent();
            this.DataContext = new KeyPadPopupContext();
        }
                
        public static readonly RoutedEvent KeyPadFinishEvent = EventManager.RegisterRoutedEvent(
            "KeyPadFinish", RoutingStrategy.Bubble, typeof(RoutedEventHandler), typeof(KeyPad));

        public event RoutedEventHandler KeyPadFinish
        {
            add { AddHandler(KeyPadFinishEvent, value); }
            remove { RemoveHandler(KeyPadFinishEvent, value); }
        }

        void RaiseKeyPadFinishEvent()
        {
            var e = new RoutedEventArgs(KeyPad.KeyPadFinishEvent);
            RaiseEvent(e);
        }


        private void OnKeyDownHandler(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Return)
            {
                this.Dispatcher.InvokeAsync(() =>
                {
                    var v = (sender as TextBox).Text;
                    (this.DataContext as KeyPadPopupContext).InputString = v;
                    RaiseKeyPadFinishEvent();
                });
            }
        }
    }
}

