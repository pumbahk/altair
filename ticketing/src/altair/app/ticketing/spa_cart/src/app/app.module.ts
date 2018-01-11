import { BrowserModule } from '@angular/platform-browser';
import { NgModule, isDevMode } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule,JsonpModule} from '@angular/http';
import { RouterModule, Routes } from '@angular/router';
import { Location } from '@angular/common';
//Component
import { AppComponent } from './app.component';
import { ReserveBySeatComponent } from './reserve-by-seat/reserve-by-seat.component';
import { PaymentComponent } from './payment/payment.component';
import { ReserveByQuantityComponent } from './reserve-by-quantity/reserve-by-quantity.component';
import { SelectProductComponent } from './select-product/select-product.component';
import { EventinfoComponent } from './reserve-by-seat/event-info/event-info.component';
import { FilterComponent } from './reserve-by-seat/filter/filter.component';
import { VenuemapComponent } from './reserve-by-seat/venue-map/venue-map.component';
import { SeatlistComponent } from './reserve-by-seat/seat-list/seat-list.component';
import { PageNotFoundComponent } from './errors/page-not-found/page-not-found.component';
import { ApiCommonErrorComponent } from './errors/api-common-error/api-common-error.component';
import { RoadAnimationComponent } from './shared/components/road-animation.component';
//Service
import { ApiBase } from './shared/services/api-base.service'
import { PerformancesService } from './shared/services/performances.service';
import { SeatStatusService } from './shared/services/seat-status.service';
import { StockTypesService } from './shared/services/stock-types.service';
import { SeatsService } from './shared/services/seats.service';
import { SelectProductService } from './shared/services/select-product.service';
import { QuentityCheckService } from './shared/services/quentity-check.service';
import { StockTypeDataService } from './shared/services/stock-type-data.service';
import { AnimationEnableService } from './shared/services/animation-enable.service';
import { ErrorModalDataService } from './shared/services/error-modal-data.service';
import { CountSelectService } from './shared/services/count-select.service';
import { SmartPhoneCheckService } from './shared/services/smartPhone-check.service';
import { SelectProductBrowserBackService } from './shared/services/select-product-browser-back.service';
import { ReserveBySeatBrowserBackService } from './shared/services/reserve-by-seat-browser-back.service';
import { SeatDataService } from './shared/services/seat-data.service';
//Ng-inline-svg
import { InlineSVGModule } from 'ng-inline-svg';
//Primeng
import {InputTextModule,ButtonModule,DialogModule,DropdownModule} from 'primeng/primeng';
//Loding-animation
import { LoadingAnimateModule, LoadingAnimateService } from 'ng2-loading-animate';
//Slider
import { NouisliderModule } from 'ng2-nouislider';
//Logger
import { Logger, Options } from 'angular2-logger/core';
import { environment }    from '../environments/environment';

const routes: Routes = [
  { path: 'performances/:performance_id',component: ReserveBySeatComponent, canDeactivate:[ReserveBySeatBrowserBackService] },
  { path: 'performances/:performance_id/reserve-by-quantity/:stock_type_id', component: ReserveByQuantityComponent },
  { path: 'performances/:performance_id/select-product', component: SelectProductComponent, canDeactivate:[SelectProductBrowserBackService] },
  { path: 'payment/', component: PaymentComponent },
  { path: '**', component: PageNotFoundComponent }
];

@NgModule({
  declarations: [
    AppComponent,
    EventinfoComponent,
    FilterComponent,
    VenuemapComponent,
    SeatlistComponent,
    ReserveBySeatComponent,
    PaymentComponent,
    ReserveByQuantityComponent,
    SelectProductComponent,
    PageNotFoundComponent,
    ApiCommonErrorComponent,
    RoadAnimationComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    JsonpModule,
    InlineSVGModule,
    BrowserModule,FormsModule,HttpModule,InputTextModule,ButtonModule,DialogModule,DropdownModule,
    LoadingAnimateModule.forRoot(),
    RouterModule.forRoot(routes),
    NouisliderModule,
    InputTextModule,
    NouisliderModule,
    DropdownModule,
  ],
  providers: [
    Logger,
    Options,
    LoadingAnimateService,
    ApiBase,
    SeatStatusService,
    StockTypesService,
    PerformancesService,
    SeatsService,
    SelectProductService,
    QuentityCheckService,
    StockTypeDataService,
    ErrorModalDataService,
    AnimationEnableService,
    CountSelectService,
    SmartPhoneCheckService,
    SelectProductBrowserBackService,
    ReserveBySeatBrowserBackService,
    SeatDataService
  ],
  bootstrap: [
    AppComponent
  ]
})

export class AppModule {
  constructor(private logger: Logger) {
    if (isDevMode()) {
      console.info('To see debug logs enter: \'logger.level = logger.Level.DEBUG;\' in your browser console');
    }
    this.logger.level = environment.logger.level;
  }
}
