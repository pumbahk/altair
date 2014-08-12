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
    /// MenuDialog.xaml の相互作用ロジック
    /// </summary>
    public partial class MenuDialog : UserControl, IDialog
    {
        public ICommand OpenCommand { get; private set; }
        public ICommand CloseCommand { get; private set; }

        public static readonly DependencyProperty TitleProperty =
        DependencyProperty.Register("Title", typeof(string), typeof(MenuDialog),
        new FrameworkPropertyMetadata(""));

        public string Title
        {
            get { return (string)this.GetValue(TitleProperty); }
            set { this.SetValue(TitleProperty, value); }
        }

        public static readonly DependencyProperty IsOpenProperty =
        DependencyProperty.Register("IsOpen", typeof(bool), typeof(MenuDialog),
        new FrameworkPropertyMetadata(false));

        public bool IsOpen
        {
            get { return (bool)this.GetValue(IsOpenProperty); }
            set { this.SetValue(IsOpenProperty, value); }
        }

        public static readonly DependencyProperty PlacementProperty =
        DependencyProperty.Register("Placement", typeof(PlacementMode), typeof(MenuDialog),
        new FrameworkPropertyMetadata(default(PlacementMode)));

        public PlacementMode Placement
        {
            get { return (PlacementMode)this.GetValue(PlacementProperty); }
            set { this.SetValue(PlacementProperty, value); }
        }

        public static readonly DependencyProperty PlacementTargetProperty =
        DependencyProperty.Register("PlacementTarget", typeof(UIElement), typeof(MenuDialog),
        new FrameworkPropertyMetadata(null));

        public UIElement PlacementTarget
        {
            get { return (UIElement)this.GetValue(PlacementTargetProperty); }
            set { this.SetValue(PlacementTargetProperty, value); }
        }
        public MenuDialog()
        {
            InitializeComponent();
            this.OpenCommand = new DialogOpenCommand();
            this.CloseCommand = new DialogCloseCommand();
        }

        public void Show()
        {
            this.IsOpen = true;
        }

        public void Hide()
        {
            this.IsOpen = false;
        }
    }
}
