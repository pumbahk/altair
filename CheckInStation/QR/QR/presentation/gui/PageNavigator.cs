using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;

using QR.presentation.gui.page;

namespace QR.presentation.gui
{
    /// <summary>
    /// case -> page
    /// </summary>
    public class PageNavigator
    {
        public T CreateOrReUse<T> (ICase CurrentCase, Page previous) where T : Page, new()
        {
            if (previous is T)
                return previous as T;
            return new T();
        }

        public Page Create(ICase CurrentCase, Page previous)
        {
            var c = CurrentCase;
            if (c is CaseAuthInput || c is CaseAuthDataFetch)
                return this.CreateOrReUse<PageAuthInput>(c, previous);
            else if (c is CaseInputStrategySelect)
                return this.CreateOrReUse<PageInputStrategySelect>(c, previous);
            throw new NotImplementedException("sorry");
        }

        public void NavigateNextPage(ICase case_, Page previous)
        {
            var nextPage = this.Choice(case_, previous);
            if (previous != nextPage)
            {
                previous.NavigationService.Navigate(nextPage);
            }
        }
    }
}
