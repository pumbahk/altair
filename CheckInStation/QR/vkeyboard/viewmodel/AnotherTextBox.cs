using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using System.Windows.Media;

namespace vkeyboard.viewmodel
{
    class AnotherTextBox : TextBox
    {
        public AnotherTextBox() : base()
        {
            this.Loaded += OnLoaded;
        }

        void AnotherTextBox_Initialized(object sender, EventArgs e)
        {
            this.AppendText("<this string is inserted automatically>");
            var cursor = new Border(){Width=10,Height=40, Background=new SolidColorBrush(Colors.Brown)};
            this.AddLogicalChild(cursor);
            this.AddVisualChild(cursor);
        }

        void OnLoaded(object sender, System.Windows.RoutedEventArgs e)
        {
            //this.AppendText("<this string is inserted automatically>");
            var cursor = new Border(){Width=10,Height=40, Background=new SolidColorBrush(Colors.Brown)};
            this.AddLogicalChild(cursor);
            this.AddVisualChild(cursor);
        }
    }
}
