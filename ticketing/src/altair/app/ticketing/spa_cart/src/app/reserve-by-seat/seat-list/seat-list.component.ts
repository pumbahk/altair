import { Component, Input, OnInit, NgModule, Output, EventEmitter } from '@angular/core';
//platform
import { BrowserModule }  from '@angular/platform-browser';
//componet
import { FilterComponent } from '../../reserve-by-seat/filter/filter.component';
import { ReserveByQuantityComponent } from '../../reserve-by-quantity/reserve-by-quantity.component';
//service
import { StockTypesService } from '../../shared/services/stock-types.service';
import { StockTypeDataService } from '../../shared/services/stock-type-data.service';
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
  @Output() onClickSeatSelection = new EventEmitter();

  //公演
  performance: IPerformance;
  //公演ID
  performanceId: number;
  //席種情報
  stockTypes: IStockType[];
  //座席情報
  seatStockType: IStockType[]
  //処理後席種情報
  makeStockTypes: IStockType[];
  //席種情報Id
  stockTypeId: number;
  //seatList表示・非表示フラグ
  seatListDisply: boolean = true;
  //検索結果フラグ
  searchResultFlag: boolean = false;
  //Subscription
  private subscription: Subscription;
  //席種name,status配列
  stockTypesArr: { [key: number]: string[]; } = {};

  constructor(private route: ActivatedRoute,
    private reserveByQuantity: ReserveByQuantityComponent,
    private stockTypeDataService: StockTypeDataService,
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
            this.stockTypes = response.data.stock_types;
            this.filterComponent.searched$.subscribe((response: ISeatsResponse) => {
              that.searchResultFlag = false;
              if (response.data.stock_types) this.seatStockType = response.data.stock_types;
              this.stockTypesArr = this.makeStockTypeArr(this.stockTypes, this.seatStockType);
              this.makeStockTypes = this.divideList(this.stockTypes);

              //検索結果フラグ
              if (this.makeStockTypes.length == 0 || this.makeStockTypes[0].stock_type_name == null) {
                that.searchResultFlag = true;
              }
            });
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
  }
  /**
   * 席種idに紐づく席種名と席種状態を持つ配列を作る
   * @param  {IStockType[]} stockTypes - 席種情報検索
   * @param  {IStockType[]} seatStockTypes - 座席情報検索
   * @return {[key: number]: string[];}
   */
  makeStockTypeArr(stockTypes: IStockType[], seatStockTypes: IStockType[]) {
    let array: { [key: number]: string[]; } = {};

    //席種情報検索ベースに名前とステータスを配列に詰める
    for (let x in this.stockTypes) {
      array[stockTypes[x].stock_type_id] = [];
      array[stockTypes[x].stock_type_id].push(stockTypes[x].stock_type_name);
      for (let y in seatStockTypes) {
        if (stockTypes[x].stock_type_id == seatStockTypes[y].stock_type_id) {
          array[stockTypes[x].stock_type_id].push(seatStockTypes[y].stock_status);
        }
      }
      //デフォルトでステータスが無い物は"✕"を詰める
      if (!array[stockTypes[x].stock_type_id][1]) {
        array[stockTypes[x].stock_type_id].push("×");
      }
      //リストが非表示の時はステータス状態を"blank"にする
      if (!this.seatListDisply){
        for (let x in array) {
          array[x][1] = "blank";
        }
      }
    }

    return array;
  }

  /**
   * 指定席と自由席を内部構造でより分ける
   * @param  {IStockType[]} stockTypes - 席種情報検索
   * @return {IStockType[]}
   */
  divideList(stockTypes: IStockType[]) {
    let divideStockTypes: IStockType[];
    divideStockTypes = [];
    stockTypes.forEach((value, key) => {
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
  /**
* 席種のステータスからclass名を返す
* @param  {string} status - ステータス
*/
  private stockStatus(status) {
    switch (status) {
      case '◎': return 'circleW';
      case '△': return 'triangle';
      case '×': return 'close';
      case 'blank': return 'blank';
      default: return 'close';
    }
  }

  /**
* おまかせを押下時の処理
* @param  {number} stockTypeId - 席種ID
*/
  onAutoClick(stockTypeId) {
    $('html').css({
      'height': "",
      'overflow-y': "hidden"
    });
    $('body').css({
      'height': "",
      'overflow-y': "hidden"
    });
    $('body').scrollTop(0);
    if (this.countSelect == 0) {
      this.stockTypeDataService.sendToQuantity(stockTypeId);
      this.stockTypeId = stockTypeId;
    } else {
      this.confirmStockType.emit(true);
      this.stockTypeIdFromList.emit(stockTypeId);
    }
  }
 /**
* 座席を選んで購入を押下時の処理
* @param  {string} stockTypeName - 席種名
*/
  onSelectClick(stockTypeName){
    if (this.isInitialEnd) {
      this.onClickSeatSelection.emit();
      this.filterComponent.selectSeatSearch(stockTypeName, true);
      this.mapHome.emit();
    }

  }
}