using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
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
    public enum KeyPadPreviewType
    {
        raw,
        password
    }

    public class KeyPadPopupContext : DependencyObject
    {
        public static readonly DependencyProperty PreviewTypeProperty = DependencyProperty.Register(
            "KeyPadPreviewType", typeof(KeyPadPreviewType), typeof(KeyPadPopupContext), new PropertyMetadata(KeyPadPreviewType.raw));

        public KeyPadPreviewType PreviewType
        {
            get { return (KeyPadPreviewType)this.GetValue(PreviewTypeProperty); }
            set { this.SetValue(PreviewTypeProperty, value); }
        }

        public static readonly DependencyProperty InputStringProperty = DependencyProperty.Register(
        "InputString", typeof(string), typeof(KeyPadPopupContext), new FrameworkPropertyMetadata(new PropertyChangedCallback(OnInputStringPropertyChanged)));
        private static void OnInputStringPropertyChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var s = e.NewValue as string;
            var k = (KeyPadPreviewType)d.GetValue(PreviewTypeProperty);
            switch (k)
            {
                case KeyPadPreviewType.password:
                    d.SetValue(PreviewStringProperty, new String((s.Select(c => '*').ToArray<char>())));
                    break;
                case KeyPadPreviewType.raw:
                    d.SetValue(PreviewStringProperty, s);
                    break;
            }
        }
        public string InputString
        {
            get { return (string)this.GetValue(InputStringProperty); }
            set { this.SetValue(InputStringProperty, value); }
        }

        public static readonly DependencyProperty PreviewStringProperty = DependencyProperty.Register(
"PreviewString", typeof(string), typeof(KeyPadPopupContext), new PropertyMetadata(""));

        public string PreviewString
        {
            get { return (string)this.GetValue(PreviewStringProperty); }
            set { this.SetValue(PreviewStringProperty, value); }
        }

        public KeyPadPopupContext()
        {
            this.InputString = "";
        }
    }

    /// <summary>
    /// KeyPad.xaml の相互作用ロジック
    /// </summary>
    public partial class KeyPad : UserControl
    {            
        public KeyPad()
        {
            InitializeComponent();
        }
                
        public static readonly RoutedEvent KeyPadFinishEvent = EventManager.RegisterRoutedEvent(
            "KeyPadFinish", RoutingStrategy.Bubble, typeof(RoutedEventHandler), typeof(KeyPad));

        public event RoutedEventHandler KeyPadFinish
        {
            add { AddHandler(KeyPadFinishEvent, value); }
            remove { RemoveHandler(KeyPadFinishEvent, value); }
        }

        public string InputString { get {
            var ctx = this.DataContext as KeyPadPopupContext;
            return ctx.InputString;
        }}

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

