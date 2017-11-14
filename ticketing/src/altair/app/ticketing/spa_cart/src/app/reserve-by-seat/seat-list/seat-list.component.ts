import { Component, Input, OnInit, NgModule, Output, EventEmitter } from '@angular/core';
//platform
import { BrowserModule }  from '@angular/platform-browser';
//componet
import { FilterComponent } from '../../reserve-by-seat/filter/filter.component';
import { ReserveByQuantityComponent } from '../../reserve-by-quantity/reserve-by-quantity.component';
//service
import { StockTypeDataService } from '../../shared/services/stock-type-data.service';
import { StockTypesService } from '../../shared/services/stock-types.service';
import { PerformancesService } from '../../shared/services/performances.service';
import { ErrorModalDataService } from '../../shared/services/error-modal-data.service';
import { Subscription } from 'rxjs/Subscription';
//interface
import {
  IPerformance,
  IPerformanceInfoResponse,
  ISeatsRequest,
  ISeatsResponse,
  IStockType,
  IStockTypeResponse,
  IStockTypesResponse,
} from '../../shared/services/interfaces';
//router
import { ActivatedRoute,Router } from '@angular/router';
import * as $ from 'jquery';
//logger
import { Logger } from "angular2-logger/core";
// constants
import { ApiConst } from '../../app.constants';


@Component({
  providers: [FilterComponent,ReserveByQuantityComponent],
  selector: 'app-seat-list',
  templateUrl: './seat-list.component.html',
  styleUrls: ['./seat-list.component.css']
})
export class SeatlistComponent implements OnInit {

  //input属性
  @Input() filterComponent: FilterComponent;
  @Input() countSelect: number;
  @Input() reserveByQuantityComponent: ReserveByQuantityComponent;
  @Input('isInitialEnd') isInitialEnd: boolean;
  @Output() mapHome = new EventEmitter();

  @Output() confirmStockType = new EventEmitter<boolean>();
  @Output() stockTypeIdFromList = new EventEmitter<number>();

  //公演
  performance: IPerformance;
  //公演ID
  performanceId: number;
  //席種情報
  stockTypes: IStockType[];
  //席種情報
  makeStockTypes: IStockType[];
  //席種情報Id
  stockTypeId: number;
  //席種情報検索
  stockTypesRes: IStockTypesResponse;
  //seatList表示・非表示フラグ
  seatListDisply: boolean = true;
  //検索結果フラグ
  searchResultFlag: boolean = false;
  //Subscription
  private subscription: Subscription;

  constructor(private route: ActivatedRoute,
    private reserveByQuantity: ReserveByQuantityComponent,
    private stockTypeDataService: StockTypeDataService,
    private Venuemap: VenuemapComponent,
    private performancesService: PerformancesService,
    private _logger: Logger,
    private errorModalDataService: ErrorModalDataService,
    private stockTypesService: StockTypesService) {
  }
　
  　//公演情報・席種情報取得
  ngOnInit() {

    this.stockTypeDataService.toSeatListFlag$.subscribe(
      flag => {
        this.seatListDisply = flag;
      }
    );

    const that = this;
    this.route.params.subscribe((params) => {
      if (params && params['performance_id']) {
        //パラメーター切り出し
        this.performanceId = +params['performance_id'];
        this.performancesService.getPerformance(this.performanceId).subscribe((response: IPerformanceInfoResponse) => {
          this._logger.debug(`get Performance(#${this.performanceId}) success`, response);
          this.performance = response.data.performance;
          this.stockTypesService.findStockTypesByPerformanceId(this.performanceId).subscribe((response: IStockTypesResponse) => {
            this._logger.debug(`findStockTypesByPerformanceId(#${this.performanceId}) success`, response);
            this.stockTypes = response.data.stock_types
          },
            (error) => {
              this._logger.error('findStockTypesByPerformanceId(#${this.performanceId}) error', error);
            });
        },
          (error) => {
            this._logger.error('get Performance(#${this.performanceId}) error', error);
          });
      }
    });

    this.filterComponent.searched$.subscribe((response: ISeatsResponse) => {
      that.searchResultFlag = false;
      let divideStockTypes = this.divideList(response.data.stock_types);
      this.makeStockTypes = this.sortList(divideStockTypes, that.stockTypes);
      //検索結果フラグ
      if (this.makeStockTypes.length == 0 || this.makeStockTypes[0].stock_type_name == null) {
        that.searchResultFlag = true;
      }
    });

  }
  //自由席と指定席を内部構造でより分ける
  divideList(response: IStockType[]) {
    let divideStockTypes: IStockType[];
    divideStockTypes = [];
    response.forEach((value, key) => {
      if (value.is_quantity_only) {
        if (this.filterComponent.unreserved) {
          divideStockTypes.push(value);
        }
      } else {
        if (this.filterComponent.reserved) {
          divideStockTypes.push(value);
        }
      }
    });

    return divideStockTypes;
  }

  //席種情報検索のレスポンスと同じ順番に変更
  sortList(divideStockTypes: IStockType[], stockTypes: IStockType[]) {
    let sortStockTypes: IStockType[];
    sortStockTypes = [];
    for (var i = 0, len = stockTypes.length; i < len; i++) {
      for (var l = 0, dlen = divideStockTypes.length; l < dlen; l++)
        if (stockTypes[i].stock_type_id == divideStockTypes[l].stock_type_id) {
          sortStockTypes.push(divideStockTypes[l]);
        }
    }
    return sortStockTypes;
  }
　
  　//statusに合わせたクラス名を返す
  private stockStatus(status) {
    switch (status) {
      case '◎': return 'circleW';
      case '△': return 'triangle';
      case '×': return 'close';
      default: return 'unknown';
    }
  }

  //おまかせで購入を選択
  onAutoClick(stockTypeId) {
    $('html').css({
      'height': "",
      'overflow-y': "hidden"
    });
    $('body').css({
      'height': "",
      'overflow-y': "auto"
    });
    $('body').scrollTop(0);
    if (this.countSelect == 0) {
      this.stockTypeDataService.sendToQuentity(stockTypeId);
      this.stockTypeId = stockTypeId;
    } else {
      this.confirmStockType.emit(true);
      this.stockTypeIdFromList.emit(stockTypeId);
    }
  }
  //座席を選んで購入を選択
  onSelectClick(stockTypeName){
    if (this.isInitialEnd) {
      this.filterComponent.selectSeatSearch(stockTypeName);
      this.mapHome.emit();
    }
  }
}