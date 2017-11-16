import { Component,Input,OnInit,Injectable,Output,EventEmitter,NgModule } from "@angular/core";
//router
import { ActivatedRoute,Router } from '@angular/router';
//observable
import { Observable } from 'rxjs/Rx';
//service
import { PerformancesService } from '../../shared/services/performances.service';
import { SeatsService } from '../../shared/services/seats.service';
import { StockTypesService } from '../../shared/services/stock-types.service';
import { StockTypeDataService } from '../../shared/services/stock-type-data.service';
import { ErrorModalDataService } from '../../shared/services/error-modal-data.service';
import { AnimationEnableService } from '../../shared/services/animation-enable.service';
//interface
import {
  IPerformanceInfoResponse,
  IPerformance,
  IStockTypesResponse,
  IStockTypesAllResponse,
  IStockType,
  IProducts,
  ISeatsRequest,
  ISeatsResponse,
  IStockTypeResponse,
  IRegion
} from '../../shared/services/interfaces';
//jquery
import * as $ from 'jquery';
//const
import { ApiConst } from '../../app.constants';
//logger
import { Logger } from "angular2-logger/core";
@Component({
  selector: 'app-filter',
  templateUrl: './filter.component.html',
  styleUrls: ['./filter.component.css'],
  providers: [],
})

@Injectable()
export class FilterComponent implements OnInit {

  //公演
  performance: IPerformance;
  //公演ID
  performanceId: number;
  //販売区分ID
  salesSegmentId: number;
  //席種情報
  stockTypes: IStockType[];

  //金額初期値
  min: number = 0;
  max: number = 50000;
  stepValue: number = 100;//区切り
  setPriceInitNumber: number = 0;
  setPriceInitFlag: boolean = false;
  //金額範囲
  seatPrices: number[] = [0, 50000];

  //席種名
  seatName: string = "";
  //席種チェックボックス（指定席、自由席）
  unreserved: boolean = true;//自由席
  reserved: boolean = true;//指定席
  seatValues: any[] = [this.unreserved, this.reserved];

  //検索中フラグ
  searching: boolean = false;
  //スライダーの有効・無効
  sliderBool: boolean = false;
  //スライダー値取得フラグ
  getSliderValue: boolean = false;

  //自由席regionId配列
  unreservedRegionIds: string[] = [];
  //指定席regionId配列
  reservedRegionIds: string[] = [];
  //検索有効無効
  isSearch: boolean = false;

  /**
   * EventEmitter
   */
  public searched$: EventEmitter<ISeatsResponse>;

  constructor(
    private performancesService: PerformancesService,
    private seats: SeatsService,
    private route: ActivatedRoute,
    private stockTypesService: StockTypesService,
    private errorModalDataService: ErrorModalDataService,
    private animationEnableService: AnimationEnableService,
    private stockTypeDataService: StockTypeDataService,
    private _logger: Logger) {

    this.searched$ = new EventEmitter<ISeatsResponse>();
  }

  ngOnInit() {
    //公演情報
    this.route.params.subscribe((params) => {
      if (params && params['performance_id']) {
        //パラメーター切り出し
        this.performanceId = +params['performance_id'];
        this.performancesService.getPerformance(this.performanceId).subscribe((response: IPerformanceInfoResponse) => {
          this._logger.debug(`get Performance(#${this.performanceId}) success`, response);

          this.performance = response.data.performance;
          this.performanceId = this.performance.performance_id;
          this.salesSegmentId = this.performance.sales_segments[0].sales_segment_id;
          //席種情報検索
          this.stockTypesService.findStockTypesByPerformanceId(this.performanceId).subscribe((response: IStockTypesResponse) => {
            this._logger.debug(`findStockTypesByPerformanceId(#${this.performanceId}) success`, response);
            this.stockTypes = response.data.stock_types;
            //初期金額セット＋検索処理
            this.setPriceInit();
          },
            (error) => {
              this._logger.error('findStockTypesByPerformanceId(#${this.performanceId}) error', error);
            });
        },
          (error) => {
            this._logger.error('get Performance(#${this.performanceId}) error', error);
            return;
          });
      }
    });

    this.stockTypeDataService.toIsSearchFlag$.subscribe(
      flag => {
        this.isSearch = flag;
      });

    //席種名検索時Enterキー無効化
    $(function () {
      $("input").keydown(function (e) {
        if ((e.which && e.which === 13) || (e.keyCode && e.keyCode === 13)) {
          return false;
        } else {
          return true;
        }
      });
    });
  }

  //Slider初期表示
  setPriceInit() {
    const that = this;
    let selesSegmentId: number = this.performance.sales_segments[0].sales_segment_id;
    let stockTypeIds: number[] = [];
    let products: IProducts[] = [];
    let resions: string[] = [];
    let allPrices: { [key: number]: number[]; } = [];
    let prices: number[] = [];
    let minPrice: number = 0;
    let maxPrice: number = 0;

    this.stockTypesService.getStockTypesAll(this.performanceId, selesSegmentId)
      .subscribe((response: IStockTypesAllResponse) => {
        this._logger.debug(`get StockTypesAll(#${this.performanceId}) success`, response);
        let stockTypes: IStockType[] = response.data.stock_types;
        if (this.stockTypes.length > 0) {
          for (let i = 0, len = stockTypes.length; i < len; i++) {
            let productPrice: number = 0;
            let resions: string[] = stockTypes[i].regions;
            if (stockTypes[i].products.length) {
              productPrice = +stockTypes[i].products[0].price;
            } else {
              continue;
            }
            if (resions.length > 0) {
              for (var l = 0, urlen = resions.length; l < urlen; l++) {
                if (stockTypes[i].is_quantity_only) {
                  this.unreservedRegionIds.push(resions[l]);//自由席のregionIdを取得
                } else {
                  this.reservedRegionIds.push(resions[l]);//指定席のregionIdを取得
                }
              }
            }
            if (!minPrice) {
              minPrice = productPrice;
            }
            if (maxPrice < productPrice) {
              maxPrice = productPrice;
            }
            if (minPrice > productPrice) {
              minPrice = productPrice;
            }
          }
          this.max = maxPrice;
          this.min = (minPrice == maxPrice) ? 0 : minPrice;
          this.seatPrices = [minPrice, maxPrice];
          this.setPriceInitFlag = true;
          //初期表示処理
          this.valueGetTime();
          this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
        } else {
          this.max = 100;
          this.min = 0;
          setTimeout(function () {
            that.seatPrices = [0, 100];
            that.setPriceInitFlag = true;
          }, 100);
          this.valueGetTime();
          this.search();
        }
      },
      (error) => {
        this._logger.error('[FilterComponent]getStockType error', error);
      });

    //初期表示処理
    if (this.stockTypes.length > 1) {
      let sliderStartTimer = setInterval(function () {
        if (that.getSliderValue) {
          //スライダーを動かしたときの処理
          $('.noUi-handle-lower')
            .mousedown(function () {//PC
              if ($(".noUi-handle-upper .noUi-active").length == 0) {
                that.moveLowerSlier();
              }
            })
            .bind('touchstart', function () {//SP
              if ($(".noUi-handle-upper .noUi-active").length == 0) {
                that.moveLowerSlier();
              }
            });
          $('.noUi-handle-upper')
            .mousedown(function () {//PC
              if ($(".noUi-handle-lower .noUi-active").length == 0) {
                that.moveUpperSlider();
              }
            })
            .bind('touchstart', function () {//SP
              if ($(".noUi-handle-lower .noUi-active").length == 0) {
                that.moveUpperSlider();
              }
            });
          clearInterval(sliderStartTimer);
        }
      }, 100);
    } else if (this.stockTypes.length == 1) {
      this.seatPrices = [0, this.max];
    } else {
      this.seatPrices = [0, 0];
    }
  }
  //スライダー値取得タイマー
  valueGetTime() {
    let valueGetTimer: any;
    let that = this;
    valueGetTimer = setInterval(function () {
      if ($(".noUi-tooltip").length > 0) {
        that.getSliderValue = true;
        clearInterval(valueGetTimer);
      }
    }, 100);
  }
  //左レンジ変更処理
  moveLowerSlier() {
    var valueTimer: any;
    const that = this;

    valueTimer = setInterval(function () {
      var tooltipElements = document.getElementsByClassName("noUi-tooltip");
      that.seatPrices[0] = that.lowerRounding(+tooltipElements[0].innerHTML);
      //スライダーを離したときの処理
      $('.noUi-handle-lower')

        .mouseup(function () {//PC
          clearInterval(valueTimer);
        })
        .bind('touchend', function () {//SP
          clearInterval(valueTimer);
        });
      if ($(".noUi-active").length == 0) {
        clearInterval(valueTimer);
      }
    }, 100);
  }
  //右レンジ変更処理
  moveUpperSlider() {
    var valueTimer: any;
    const that = this;

    valueTimer = setInterval(function () {
      var tooltipElements = document.getElementsByClassName("noUi-tooltip");
      that.seatPrices[1] = that.upperRounding(+tooltipElements[1].innerHTML);
      //スライダーを離したときの処理
      $('.noUi-handle-upper')
        .mouseup(function () {//PC
          clearInterval(valueTimer);
        })
        .bind('touchend', function () {//SP
          clearInterval(valueTimer);
        });
      if ($(".noUi-active").length == 0) {
        clearInterval(valueTimer);
      }
    }, 100);
  }
  //左レンジ値四捨五入処理
  lowerRounding(minNum: number) {
    var minCalNum: number;
    var connectElements: any = document.getElementsByClassName("noUi-connect");

    if (String(minNum).length >= 3) {
      minCalNum = minNum / 100;
      minCalNum = Math.round(minCalNum) * 100;
      if (connectElements[0].outerHTML.indexOf("left: 0%") > -1) {
        return this.min;
      } else if (connectElements[0].outerHTML.indexOf("left: 100%") > -1) {
        return this.max;
      }
      return minCalNum;
    } else {
      return minNum;
    }
  }
  //右レンジ値四捨五入処理
  upperRounding(maxNum: number) {
    var maxCalNum: number;
    var connectElements: any = document.getElementsByClassName("noUi-connect");

    if (String(maxNum).length >= 3) {
      maxCalNum = maxNum / 100;
      maxCalNum = Math.round(maxCalNum) * 100;
      if (connectElements[0].outerHTML.indexOf("right: 0%") > -1) {
        return this.max;
      } else if (connectElements[0].outerHTML.indexOf("right: 100%") > -1) {
        return this.min;
      }
      return maxCalNum;
    } else {
      if (connectElements[0].outerHTML.indexOf("right: 100%") > -1) {
        return this.min;
      }
      return maxNum
    }
  }
  searchClick() {
    $(".acd dd").css("display", "none");
    if (!this.searching) {
      this.getIsSearchFlag();
      if (!this.searching && !this.isSearch) {
        this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
      }
    }
  }

  //各項目を初期化
  clearClick() {
    $(".acd dd").css("display", "none");
    this.getIsSearchFlag();
    if (!this.searching && !this.isSearch) {
      this.seatPrices = [this.min, this.max];
      this.seatName = "";
      this.unreserved = true;
      this.reserved = true;
      this.seatValues = [true, true];
      this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
    }
  }

  getIsSearchFlag() {
    this.stockTypeDataService.toIsSearchFlag$.subscribe(
      flag => {
        this.isSearch = flag;
      });
    if (this.isSearch) {
      this.errorModalDataService.sendToErrorModal('エラー', '座席確保状態では絞込み検索をご利用いただけません');
    }
  }

  //スライダー値変更
  onChangeSlider(e) {
    if (document.getElementsByClassName("noUi-tooltip")) {
      var tooltipelements = document.getElementsByClassName("noUi-tooltip");
      this.seatPrices[0] = this.lowerRounding(+tooltipelements["0"].innerHTML);
      this.seatPrices[1] = this.upperRounding(+tooltipelements["1"].innerHTML);
    }
  }

  //自由席チェック変更
  onChangeUnreserved(unreserved: boolean) {
    if (unreserved) {
      this.seatValues[0] = false;
    } else {
      this.seatValues[0] = true;
    }
  }

  //指定席チェック変更
  onChangeReserved(reserved: boolean) {
    if (reserved) {
      this.seatValues[1] = false;
    } else {
      this.seatValues[1] = true;
    }
  }

  //座席選択時処理
  selectSeatSearch(name: string) {
    this.seatPrices = [this.min, this.max];
    this.unreserved = true;
    this.reserved = true;
    this.seatValues = [true, true];
    this.seatName = name;
    if (!this.searching) {
      this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
    }
  }

  //検索パラメータ取得処理
  getSearchParams(): ISeatsRequest {
    let params: ISeatsRequest = {
      fields: "",
      min_price: this.seatPrices[0],
      max_price: this.seatPrices[1],
      stock_type_name: this.seatName,
    };
    return params;
  }

  //検索処理
  public search(): Observable<ISeatsResponse> {
    this._logger.debug("seat search start");
    let find = null;
    this.searching = true;
    $('.reserve').prop("disabled", true);
    this.animationEnableService.sendToRoadFlag(true);
    if (this.performanceId) {
      find = this.seats.findSeatsByPerformanceId(this.performanceId, this.getSearchParams())
        .map((response: ISeatsResponse) => {
          for (var i = 0; i < response.data.stock_types.length; i++) {
            response.data.stock_types[i] = Object.assign(
              response.data.stock_types[i],
              this.stockTypes.find(obj => obj.stock_type_id == response.data.stock_types[i].stock_type_id)
            );
          }
          return response;
        });
    }
    find.subscribe((response: ISeatsResponse) => {
      this._logger.debug("seat search completed", response);
      $('.reserve').prop("disabled", false);
      this.searching = false;
      this.animationEnableService.sendToRoadFlag(false);
      this.sliderBool = false;
      this.searched$.emit(response);
    },
      (error) => {
        this.searching = false;
        $('.reserve').prop("disabled", false);
        this.animationEnableService.sendToRoadFlag(false);
        this._logger.error("seat search error", error);
      });
    return find;
  }

  //検索項目変更ディレイ（連打防止）
  public searchs(min: number, max: number, name: string, unreserved: boolean, reserved: boolean) {
    setTimeout(() => {
      if (min == this.seatPrices[0] && max == this.seatPrices[1] &&
        name == this.seatName && unreserved == this.seatValues[0] && reserved == this.seatValues[1]) {
        this.search();
      }
    }, 500);
  }
}
