using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;
using System.Windows.Media.Animation;
using WpfKb.Controls;
using WpfKb.LogicalKeys;

namespace vkeyboard.viewmodel
{

    //individusal border class. キーボードが有効・無効の際のstyleの分岐をTargetTypeで指定するためだけにある
    public sealed class KeyboardSurface : Border
    {
    }

    public sealed class MouseOverKeyboardSurface : Border
    {
    }

    public class KeyPadKeyLayout : IScreenKeyLayout
    {
        private Border _keySurface;
        private Border _mouseDownSurface;
        private TextBlock _keyText;
        private readonly OnScreenKey core;
        private readonly Func<TextBlock> CreateInnerTextBlock;

        public KeyPadKeyLayout(OnScreenKey key)
        {
            this.core = key;
            this.CreateInnerTextBlock = InnerTextCreate.OneLineText;
            this.SetupControl(key.Key);
        }

        public KeyPadKeyLayout(OnScreenKey key, Func<TextBlock> createText) {
            this.core = key;
            this.CreateInnerTextBlock = createText;
            this.SetupControl(key.Key);
        }

        private readonly SolidColorBrush _keyOutsideBorderBrush = new SolidColorBrush(Colors.Transparent);

        public void AnimateMouseDown()
        {
            _mouseDownSurface.BeginAnimation(OnScreenKey.OpacityProperty, new DoubleAnimation(1, new Duration(TimeSpan.Zero)));
            _keyText.Foreground = _keyOutsideBorderBrush;
        }

        public void AnimateMouseUp()
        {
            var core = this.core;
            if ((core.Key is TogglingModifierKey || core.Key is InstantaneousModifierKey) && ((ModifierKeyBase)core.Key).IsInEffect) return;
            _keyText.Foreground = Brushes.White;
            if (!core.AreAnimationsEnabled || core.Key is TogglingModifierKey || core.Key is InstantaneousModifierKey)
            {
                _mouseDownSurface.BeginAnimation(OnScreenKey.OpacityProperty, new DoubleAnimation(0, new Duration(TimeSpan.Zero)));
            }
            else
            {
                _mouseDownSurface.BeginAnimation(OnScreenKey.OpacityProperty, new DoubleAnimation(0, Duration.Automatic));
            }
        }

        public void OnMouseEnter()
        {
        }

        public void OnMouseLeave()
        {
        }
        
        public void BuildVisual()
        {
            var core = this.core;

            var conner_radius = 7;
            var border_thickness = 1;
            var margin = new Thickness(3);
            var content_padding = new Thickness(27, 19, 27, 19);

            core.CornerRadius = new CornerRadius(conner_radius);
            core.BorderBrush = _keyOutsideBorderBrush;
            core.BorderThickness = new Thickness(border_thickness);
            core.SnapsToDevicePixels = true;

            var g = new Grid();
            core.Child = g;

            _keySurface = new KeyboardSurface
            {
                Margin = margin,
                CornerRadius = new CornerRadius(conner_radius),
                BorderThickness = new Thickness(border_thickness),
                SnapsToDevicePixels = true
            };
            g.Children.Add(_keySurface);

            _mouseDownSurface = new MouseOverKeyboardSurface
            {
                Margin = margin,
                CornerRadius = new CornerRadius(conner_radius),
                Opacity = 0,
                SnapsToDevicePixels = true
            };
            g.Children.Add(_mouseDownSurface);

            _keyText = this.CreateInnerTextBlock();
        }

        public void SetupControl(ILogicalKey key)
        {
            this.BuildVisual();
            _keyText.SetBinding(TextBlock.TextProperty, new Binding("DisplayName") { Source = key });
            (this.core.Child as Grid).Children.Add(_keyText);
        }
    }


    class InnerTextCreate
    {
        public static Thickness OnelinePadding = new Thickness(27, 19, 27, 19);
        public static TextBlock OneLineText()
        {
            var font_size = 40;
            var content_padding = InnerTextCreate.OnelinePadding;
            return new TextBlock
            {
                FontSize = font_size,
                LineHeight = font_size,
                FontWeight = FontWeights.Bold,
                Foreground = Brushes.White,
                Padding = content_padding,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                SnapsToDevicePixels = true
            };
        }

        public static Thickness TwoLinePadding = new Thickness(22, 6, 22, 6);
        public static TextBlock TwoLineText()
        {
            var font_size = 18;
            var content_padding = InnerTextCreate.TwoLinePadding;
            return new TextBlock
            {
                FontSize = font_size,
                LineHeight = font_size,
                FontWeight = FontWeights.Bold,
                Foreground = Brushes.White,
                Padding = content_padding,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                TextWrapping = System.Windows.TextWrapping.Wrap,
                SnapsToDevicePixels = true
            };
        }
    }
}
