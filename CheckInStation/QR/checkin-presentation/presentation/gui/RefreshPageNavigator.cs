using System;
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
    public enum RefreshPageStateEnum {
        StartPoint,
        QR,
        OrdernoOrderno,
        OrdernoTel
    }

    public class RefreshPageState{
        public RefreshPageStateEnum State {get;set;}
        public ICase Case { get; set; }

        public string Orderno { get; set; }
        public string Tel { get; set; }

        public RefreshPageState(ICase case_)
        {
            this.State = RefreshPageStateEnum.StartPoint;
            this.Case = case_;
        }

        public void Forward()
        {
            switch (this.State)
            {
                case RefreshPageStateEnum.QR:
                    this.State = RefreshPageStateEnum.StartPoint;
                    break;
                case RefreshPageStateEnum.OrdernoOrderno:
                    this.State = RefreshPageStateEnum.OrdernoTel;
                    break;
                case RefreshPageStateEnum.OrdernoTel:
                    this.State = RefreshPageStateEnum.StartPoint;
                    break;
                case RefreshPageStateEnum.StartPoint:
                    if(this.Case is CaseOrdernoOrdernoInput || this.Case is CaseOrdernoTelInput)
                    {
                        this.State = RefreshPageStateEnum.OrdernoOrderno;
                    } else {
                        this.State = RefreshPageStateEnum.QR;
                    }
                    break;
            }
        }

        public void Backward()
        {
            switch (this.State)
            {
                case RefreshPageStateEnum.QR:
                    this.State = RefreshPageStateEnum.StartPoint;
                    break;
                case RefreshPageStateEnum.OrdernoOrderno:
                    this.State = RefreshPageStateEnum.StartPoint;
                    break;
                case RefreshPageStateEnum.OrdernoTel:
                    this.State = RefreshPageStateEnum.OrdernoOrderno;
                    break;
                case RefreshPageStateEnum.StartPoint:
                    break;
            }
        }
    }

    public class RefreshPageNavigator
    {
        private Logger logger = LogManager.GetCurrentClassLogger();
        public readonly PageNavigator Navigator;

        public RefreshPageState State { get; set; }
        public RefreshPageNavigator(PageNavigator navigator)
        {
            this.Navigator = navigator;
        }

        public T CreateOrReUse<T> (Page previous) where T : Page, new()
        {
            if (previous is T)
                return previous as T;
            return new T();
        }

        public Page Choice(RefreshPageStateEnum state, Page previous){
            switch (state)
            {
               case RefreshPageStateEnum.QR:                     
                   return this.CreateOrReUse<PageQRRefresh>(previous);
                case RefreshPageStateEnum.StartPoint:
                   return this.Navigator.Choice(this.State.Case, previous);
                case RefreshPageStateEnum.OrdernoOrderno:
                   return this.CreateOrReUse<PageOrdernoRefreshOrdernoInput>(previous);
                case RefreshPageStateEnum.OrdernoTel:
                   return this.CreateOrReUse<PageOrodernoRefreshTelInput>(previous);
                default:
                   throw new InvalidOperationException("anything is wrong");
            }   
        }

        public void NavigateToMatchedPage(RefreshPageState state, Page previous)
        {
            this.State = state;
            this.NavigateToMatchedPage(previous);
        }

        public void NavigateToMatchedPage(Page previous)
        {
            previous.Dispatcher.Invoke(() =>
            {
                var nextPage = this.Choice(this.State.State, previous);
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
                        logger.Info("previous: {0}, state: {1}, NavigationService is not found".WithMachineName(), previous, this.State.State);
                    }
                }
            });
        }
    }
}
