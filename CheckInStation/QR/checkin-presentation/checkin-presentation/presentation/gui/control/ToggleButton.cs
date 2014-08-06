﻿using System;
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
                binding.ValidationRules.Add(new ToggleButtonValidationRule(pageConfirmAllDataContext));
            }
        }
    }

    class ToggleButtonValidationRule: ValidationRule
    {
        public PageConfirmAllDataContext PageConfirmAllDataContext { get; set; }

        public ToggleButtonValidationRule(PageConfirmAllDataContext context)
        {
            this.PageConfirmAllDataContext = context as PageConfirmAllDataContext;
        }

        public override ValidationResult Validate(object value, System.Globalization.CultureInfo cultureInfo)
        {

            //var ticketData = value as TicketData;
            //var ticketDat2a = value as DisplayTicketData;
            //Console.WriteLine(ticketData.ordered_product_item_token_id);
            return new ValidationResult(true, "hoge");
        }
    }
}
