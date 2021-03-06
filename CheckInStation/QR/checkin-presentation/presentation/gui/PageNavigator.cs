﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;

using checkin.presentation.gui.page;
using NLog;
using checkin.core.support;
using checkin.core.flow;

namespace checkin.presentation.gui
{
    /// <summary>
    /// case -> page
    /// </summary>
    public class PageNavigator
    {
        private Logger logger = LogManager.GetCurrentClassLogger();

        public T CreateOrReUse<T> (ICase CurrentCase, Page previous) where T : Page, new()
        {
            if (previous is T)
                return previous as T;
            return new T();
        }

        public Page ReturnPrev(AbstractCase CurrentCase)
        {
            return new PageConfirmAll(CurrentCase);
        }

        public Page Choice(ICase CurrentCase, Page previous)
        {
            var c = CurrentCase;
            if (c is CaseAuthInput || c is CaseAuthDataFetch)
                return this.CreateOrReUse<PageAuthInput>(c, previous);
            else if (c is CaseAuthPassword)
                return this.CreateOrReUse<PageAuthPassword>(c, previous);

            else if (c is CaseInputStrategySelect)
                return this.CreateOrReUse<PageInputStrategySelect>(c, previous);

            else if (c is CaseFailureRedirect)
                return this.CreateOrReUse<PageFailure>(c, previous);

            else if (c is CaseWelcome)
                return this.CreateOrReUse<PageWelcome>(c, previous);
            else if (c is CaseOneOrPart)
                return this.CreateOrReUse<PageOneOrPart>(c, previous);
            else if (c is CasePartOrAll)
                return this.CreateOrReUse<PagePartOrAll>(c, previous);
            else if (c is CaseConfirmListForOne)
                return this.CreateOrReUse<PageConfirmListOne>(c, previous);
            else if (c is CaseConfirmListForPart)
                return this.CreateOrReUse<PageConfirmListPart>(c, previous);

            else if (c is CaseQRCodeInput || c is CaseQRDataFetch || c is CaseQRConfirmForAllHidden)
                return this.CreateOrReUse<PageQRCodeInput>(c, previous);
            else if (c is CaseQRConfirmForOne)
                return this.CreateOrReUse<PageConfirmOne>(c, previous);
            else if (c is CaseQRConfirmForAll)
            {
                if ((c as CaseQRConfirmForAll).PartOrAll == 0)
                {
                    if(previous is PageConfirmListPart)
                        return this.ReturnPrev(c as AbstractCase);
                    return this.CreateOrReUse<PageConfirmAll>(c, previous);
                }
                else
                {
                    return this.CreateOrReUse<PageConfirmListAll>(c, previous);
                }
                
            }
            else if (c is CaseOrdernoOrdernoInput)
                return this.CreateOrReUse<PageOrdernoOrdernoInput>(c, previous);
            else if (c is CaseOrdernoTelInput || c is CaseOrdernoConfirmForAllHidden)
                return this.CreateOrReUse<PageOrdernoTelInput>(c, previous);
            else if (c is CaseOrdernoVerifyRequestData)
                return this.CreateOrReUse<PageOrdernoTelInput>(c, previous); //xxx:
            else if (c is CaseOrdernoConfirmForAll)
            {
                if ((c as CaseOrdernoConfirmForAll).PartOrAll == 0)
                {
                    if (previous is PageConfirmListPart)
                        return this.ReturnPrev(c as AbstractCase);
                    return this.CreateOrReUse<PageConfirmAll>(c, previous);
                }
                else
                {
                    return this.CreateOrReUse<PageConfirmListAll>(c, previous);
                }
                
            }
            else if (c is CasePrintForOne)
                return this.CreateOrReUse<PagePrinting>(c, previous);
            else if (c is CasePrintForAll)
            {
                if (AppUtil.GetCurrentResource().FlowDefinition is OneStepFlowDefinition)
                    return this.CreateOrReUse<PagePrinting2>(c, previous);
                else
                    return this.CreateOrReUse<PagePrinting>(c, previous);
            }
            else if (c is CasePrintFinish)
            {
                if(AppUtil.GetCurrentResource().FlowDefinition is OneStepFlowDefinition)
                    return this.CreateOrReUse<PageFinish2>(c, previous);
                else
                    return this.CreateOrReUse<PageFinish>(c, previous);
            }
            throw new NotImplementedException("sorry");
        }

        public void NavigateToMatchedPage(ICase case_, Page previous, string errorMessage)
        {
            previous.Dispatcher.Invoke(() =>
            {
                var nextPage = this.Choice(case_, previous);
                if (previous != nextPage)
                {
                    logger.Debug("navigate page: {0}".WithMachineName(), nextPage);
                    var service = previous.NavigationService;
                    if (service != null)
                    {
                        service.Navigate(nextPage);
                        nextPage.Dispatcher.Invoke(() => {
                            (nextPage.DataContext as InputDataContext).PassingErrorMessage(errorMessage);
                        }
                            );
                    }
                    else
                    {
                        logger.Info("previous: {0}, case: {1}, NavigationService is not found".WithMachineName(), previous, case_);
                    }
                }
            });
        }

        public void  NavigateToMatchedPage(ICase case_, Page previous)
        {
            previous.Dispatcher.Invoke(() =>
            {
                var nextPage = this.Choice(case_, previous);
                if (previous != nextPage)
                {
                    logger.Debug("navigate page: {0}".WithMachineName(), nextPage);
                    var service = previous.NavigationService;
                    if (service != null)
                    {
                        service.Navigate(nextPage);
                    }
                    else
                    {
                        logger.Info("previous: {0}, case: {1}, NavigationService is not found".WithMachineName(), previous, case_);
                    }
                }
            });
        }
    }
}
