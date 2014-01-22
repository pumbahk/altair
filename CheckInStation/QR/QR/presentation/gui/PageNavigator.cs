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

        public Page Choice(ICase CurrentCase, Page previous)
        {
            var c = CurrentCase;
            if (c is CaseAuthInput || c is CaseAuthDataFetch)
                return this.CreateOrReUse<PageAuthInput>(c, previous);

            else if (c is CaseInputStrategySelect)
                return this.CreateOrReUse<PageInputStrategySelect>(c, previous);

            else if (c is CaseFailureRedirect)
                return this.CreateOrReUse<PageFailure>(c, previous);

            else if (c is CaseQRCodeInput || c is CaseQRDataFetch)
                return this.CreateOrReUse<PageQRCodeInput>(c, previous);
            else if (c is CaseQRConfirmForOne)
                return this.CreateOrReUse<PageConfirmOne>(c, previous);
            else if (c is CaseQRConfirmForAll)
                return this.CreateOrReUse<PageConfirmAll>(c, previous);

            else if (c is CaseOrdernoOrdernoInput)
                return this.CreateOrReUse<PageOrdernoOrdernoInput>(c, previous);
            else if (c is CaseOrdernoTelInput)
                return this.CreateOrReUse<PageOrdernoTelInput>(c, previous);
            else if (c is CaseOrdernoVerifyRequestData)
                return this.CreateOrReUse<PageOrdernoTelInput>(c, previous); //xxx:
            else if (c is CaseOrdernoConfirmForAll)
                return this.CreateOrReUse<PageConfirmAll>(c, previous);

            else if (c is CasePrintForOne || c is CasePrintForAll)
                return this.CreateOrReUse<PagePrinting>(c, previous);
            else if (c is CasePrintFinish)
                return this.CreateOrReUse<PageFinish>(c, previous);
            throw new NotImplementedException("sorry");
        }

        public void NavigateToMatchedPage(ICase case_, Page previous)
        {
            var nextPage = this.Choice(case_, previous);
            if (previous != nextPage)
            {
                previous.NavigationService.Navigate(nextPage);
            }
        }
    }
}
