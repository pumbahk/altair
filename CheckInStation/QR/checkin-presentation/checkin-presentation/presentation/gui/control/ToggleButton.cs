using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows;
using System.Threading.Tasks;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Controls;
using checkin.presentation.gui.page;
using checkin.presentation.gui.viewmodel;
using checkin.core.models;

namespace checkin.presentation.gui.control
{
    partial class AddToggleButtonValidation
    {
        public void X(object sender, RoutedEventArgs e)
        {
            var binding = BindingOperations.GetBinding((DependencyObject)sender, ToggleButton.IsCheckedProperty);
            var displayTicketData = ((ToggleButton)sender).DataContext as DisplayTicketData;
            var pageConfirmAllDataContext = displayTicketData.ParentContext as PageConfirmAllDataContext;
            if (pageConfirmAllDataContext != null)
            {
                binding.ValidationRules.Add(new ToggleButtonValidationRule(pageConfirmAllDataContext, displayTicketData));
            }
        }
    }

    class ToggleButtonValidationRule: ValidationRule
    {
        private DisplayTicketData DisplayTicketData;

        private PageConfirmAllDataContext PageConfirmAllDataContext;

        public ToggleButtonValidationRule(page.PageConfirmAllDataContext pageConfirmAllDataContext, DisplayTicketData displayTicketData)
        {
            this.PageConfirmAllDataContext = pageConfirmAllDataContext;
            this.DisplayTicketData = displayTicketData;
        }

        public override ValidationResult Validate(object value, System.Globalization.CultureInfo cultureInfo)
        {
            /*
            if (this.PageConfirmAllDataContext.ReadTicketData.ordered_product_item_token_id == this.DisplayTicketData.TokenId)
            {
                return new ValidationResult(false, "must print ticket!!");
            }
            */
            Console.WriteLine(this);
            return new ValidationResult(true, "validation ok!!");
        }
    }
}
