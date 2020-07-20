import { Component, NgModule, OnInit, Input, Output ,EventEmitter} from '@angular/core';
//component
import { SeatlistComponent } from '../reserve-by-seat/seat-list/seat-list.component';
import { VenuemapComponent } from '../reserve-by-seat/venue-map/venue-map.component';
//service
import { PerformancesService } from '../shared/services/performances.service';
import { StockTypesService } from '../shared/services/stock-types.service';
import { SeatStatusService } from '../shared/services/seat-status.service';
import { QuantityCheckService } from '../shared/services/quantity-check.service';
import { StockTypeDataService } from '../shared/services/stock-type-data.service';
import { ErrorModalDataService } from '../shared/services/error-modal-data.service';
import { FilterComponent } from '../reserve-by-seat/filter/filter.component';
import { SeatsService } from '../shared/services/seats.service';
import { CountSelectService } from '../shared/services/count-select.service';
import { AnimationEnableService } from '../shared/services/animation-enable.service';
import { SmartPhoneCheckService } from '../shared/services/smartPhone-check.service';
import { ReserveBySeatBrowserBackService } from '../shared/services/reserve-by-seat-browser-back.service';
import { I18nService } from '../shared/services/i18n-service';
import {TranslateService} from "ng2-translate";
//interface
import { IPerformance, IPerformanceInfoResponse,
         IStockTypeResponse, IStockTypesResponse, IStockType,
         ISeatsReserveResponse,ISeatsReleaseResponse,IResult,
         ISeatsResponse,ISalesSegment,IRegion,ISeat,IProducts
       } from '../shared/services/interfaces';
//router
import { ActivatedRoute,Router } from '@angular/router';
//jquery
import * as $ from 'jquery';
//Subscription
import { Subscription } from 'rxjs/Subscription';
//const
import { ApiConst, SearchConst } from '../app.constants';
//logger
import { Logger } from "angular2-logger/core";

const REGION_COLOR_SELECTED = 'rgb(255, 0, 0)';
const REGION_COLOR_WHITE = 'rgb(255, 255, 255)';
const WINDOW_SM = 768; // スマホか否かの判定に用いる

@Component({
  selector: 'app-reserve-by-quantity',
  templateUrl: './reserve-by-quantity.component.html',
  styleUrls: ['./reserve-by-quantity.component.css']
})
export class ReserveByQuantityComponent implements OnInit {
  //Subscription
  private subscription: Subscription;
  //席種Id
  private selectStockTypeId: number;
  // 座席選択数
  private countSelectVenuemap: number = 0;

  //表示・非表示(venuemap,reserve-by-quantityで双方向データバインド)
  //(seat-listから呼び出されてtrue,false)
  @Input() filterComponent: FilterComponent;
  @Input() display: boolean = false;
  @Output() output = new EventEmitter<boolean>();
  @Output() confirmStockType = new EventEmitter<boolean>();

  //MapUrl
  mapURL: string;

  //チケット枚数
  quantity: number = 1;//初期値

  //公演ID
  performanceId: number;

  //公演情報
  performance: IPerformance;

  //販売セグメント
  selesSegments: ISalesSegment[];

  //販売セグメントID
  selesSegmentId: number;

  //席種
  stockType: IStockType;

  //席種名
  stockTypeName: string;

  // 選択した座席の商品配列
  selectedProducts: IProducts[];
  // 選択した座席表示用の商品販売単位配列
  selectedSalesUnitQuantities: number[] = [];

  //枚数選択POST初期データ
  data: {} = {
    "reserve_type": "auto",
    "auto_select_conditions": {
      "stock_type_id": 0,
      "quantity": 0
    }
  };

  //座席確保ステータス
  seatPostStatus: string;

  //ブロック情報
  regions: string[];

  //取得座席配列
  resSeatIds: ISeat[];

  //svgから取得する座席配列
  resResult: any;

  //svgから取得する座席配列
  seatNameList: string[] = [];

  //最大購入数
  maxQuantity: number;
  upperLimit: number;
  //最小購入数
  minQuantity: number = 1;
  //最小単位
  minSalesUnitNumber: number = null;

  //説明
  description: string;

  //ボタン表示・非表示
  nextButtonFlag: boolean = false;

  //座席確保飛び席モーダルフラグ
  separatDetailDisplay: boolean = false;

  //+ボタンに追加するクラス　disabled用
  plusBtnClass: string = '';

  constructor(
      private route: ActivatedRoute,
      private router: Router,
      private performances: PerformancesService, private stockTypes: StockTypesService,
      private seatStatus: SeatStatusService, private seats: SeatsService,
      private quantityCheckService: QuantityCheckService,
      private stockTypeDataService: StockTypeDataService,
      private errorModalDataService: ErrorModalDataService,
      private countSelectService: CountSelectService,
      private animationEnableService: AnimationEnableService,
      private smartPhoneCheckService: SmartPhoneCheckService,
      private reserveBySeatBrowserBackService: ReserveBySeatBrowserBackService,
      private _logger: Logger,
      public i18nService: I18nService,
      private translateService: TranslateService
  ) {
  }

  ngOnInit() {
    this.nextButtonFlag = false;
    this.stockTypeDataService.toQuantityData$.subscribe(
      stockTypeId => {
        this.selectStockTypeId = stockTypeId;
        this.loadPerformance();
      });
    this.countSelectService.toQuantityData$.subscribe(
      countSelect => {
        this.countSelectVenuemap = countSelect;
      });
  }

  //公演情報API呼び出し
  private loadPerformance() {
    const that = this;
    var timer;
    var regionId: string;
    this.route.params.subscribe((params) => {
      if (params && params['performance_id']) {
        //パラメーター切り出し
        this.performanceId = +params['performance_id'];
        //公演情報取得
        this.performances.getPerformance(this.performanceId)
          .subscribe((response: IPerformanceInfoResponse) => {
            this._logger.debug(`get performance(#${this.performanceId}) success`, response);
            this.performance = response.data.performance;
            this.mapURL = this.performance.mini_venue_map_url;
            this.selesSegments = this.performance.sales_segments;
            this.selesSegmentId = this.selesSegments[0].sales_segment_id;
            this.upperLimit = this.performance.sales_segments[0].upper_limit;

            //席種情報取得
            if (this.performanceId && this.selesSegmentId && this.selectStockTypeId) {
              this.stockTypes.getStockType(this.performanceId, this.selesSegmentId, this.selectStockTypeId)
                .subscribe((response: IStockTypeResponse) => {
                  this._logger.debug(`get stockType(#${this.performanceId}) success`, response);
                  //レスポンスが正常に返ってくれば表示
                  this.display = true;
                  $('html,body').css({
                    'width': '100%',
                    'height': '100%',
                    'overflow-y': 'hidden'
                  });
                  //おまかせ表示前デザイン設定
                  if ($(window).width() <= WINDOW_SM) {
                    this.modalSizeObtained();
                  } else if (!this.mapURL) {
                    setTimeout(function () {
                      $('#venue-quantity').css({
                        'height': '0',
                      });
                    }, 0);
                  }
                  this.stockType = response.data.stock_types[0];
                  //席種名と商品情報取得
                  this.stockTypeName = this.stockType.stock_type_name;
                  this.selectedProducts = this.stockType.products;
                  this.selectedSalesUnitQuantities = this.quantityCheckService.eraseOne(this.stockType.products);
                  this.description = this.stockType.description ? this.stockType.description : '';
                  this.minQuantity = this.stockType.min_quantity;
                  //初期表示時に購入下限枚数を選択状態として設定
                  if (this.stockType.min_quantity) {
                    this.quantity = this.stockType.min_quantity;
                  }
                  this.maxQuantity = this.stockType.max_quantity;
                  //最小の単位を取得
                  let salesUnitNumber: number = null;
                  this.minSalesUnitNumber = null;
                  for (let i = 0, len = this.selectedProducts.length; i < len; i++) {
                    salesUnitNumber = null;
                    for (let j = 0, len = this.selectedProducts[i].product_items.length; j < len; j++) {
                      if (this.selectedProducts[i].product_items[j].sales_unit_quantity) {
                        salesUnitNumber += this.selectedProducts[i].product_items[j].sales_unit_quantity;
                      }
                    }
                    if (!this.minSalesUnitNumber || this.minSalesUnitNumber > salesUnitNumber) {
                      this.minSalesUnitNumber = salesUnitNumber;
                    }
                  }
                  //初期選択枚数が最小単位で割り切れなかった場合調整
                  if (this.quantity % this.minSalesUnitNumber != 0) {
                    this.quantity = Math.ceil(this.quantity / this.minSalesUnitNumber) * this.minSalesUnitNumber;
                  }
                  //+ボタンのdisabled
                  this.plusBtnClass = '';
                  if (!this.quantityCheckService.stockTypeQuantityMaxLimitCheck(this.upperLimit, this.maxQuantity, this.quantity + this.minSalesUnitNumber)) {
                    this.plusBtnClass = 'disabled';
                  }
                  //regions取得
                  that.regions = this.stockType.regions;
                  this.modalTopCss();
                  //regionsがある時のみ色付けインターバル開始
                  if (that.regions.length > 0) {
                    startTimer();
                  }
                  that.nextButtonFlag = true;

                  //インターバル処理
                  function startTimer() {
                    let getMap: any;
                    timer = setInterval(function () {
                      getMap = document.getElementById("venue-quantity");
                      if (getMap && getMap.firstElementChild) {
                        //二重色付け制限
                        $('#venue-quantity').find('.region').css({ 'fill': REGION_COLOR_WHITE });
                        $('#venue-quantity').find('.region').find('.coloring_region').css({ 'fill': REGION_COLOR_WHITE });
                        //色付け
                        for (let i = 0; i < that.regions.length; i++) {
                          $('#venue-quantity').find('#' + that.regions[i]).css({ 'fill': REGION_COLOR_SELECTED });
                          $('#venue-quantity').find('#' + that.regions[i]).find('.coloring_region').css({ 'fill': REGION_COLOR_SELECTED });
                        }
                        //インターバル処理終了
                        clearInterval(timer);
                      }
                    }, 100);
                  }
                },
                (error) => {
                  this._logger.error('stockType error:' + error);
                  //レスポンスがエラーの場合は非表示
                  this.display = false;
                  this.scrollAddCss();
                  this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
                });
            } else {
              this.display = false;
              this._logger.error("パラメータに異常が発生しました。");
            }
          },
          (error) => {
            this.display = false;
            this._logger.error('performances error:' + error);
          });
      }
      else {
        this.display = false;
        this._logger.error('エラー', '公演IDを取得できません。');
        this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
      }

    });
  }

  //閉じるボタン
  closeClick() {
    this.display = false;
    this.output.emit(false);
    this.nextButtonFlag = false;
    this.quantity = 1;
    this.scrollAddCss();
  }

  //チケット枚数減少
  minusClick() {
    if (this.quantityCheckService.stockTypeQuantityMinLimitCheck(this.minQuantity, this.quantity - this.minSalesUnitNumber)) {
      this.quantity = this.quantity - this.minSalesUnitNumber;
      $('#plus-btn').removeClass('disabled');
      if (!this.quantityCheckService.stockTypeQuantityMinLimitCheck(this.minQuantity, this.quantity - this.minSalesUnitNumber)) {
        $('#minus-btn').addClass('disabled');
      }
    } else {
      $('#minus-btn').addClass('disabled');
    }
  }

  //チケット枚数増加
  plusClick() {
    if (this.quantityCheckService.stockTypeQuantityMaxLimitCheck(this.upperLimit, this.maxQuantity, this.quantity + this.minSalesUnitNumber)) {
      this.quantity = this.quantity + this.minSalesUnitNumber;
      $("#minus-btn").removeClass('disabled');
      if (!this.quantityCheckService.stockTypeQuantityMaxLimitCheck(this.upperLimit, this.maxQuantity, this.quantity + this.minSalesUnitNumber)) {
        $("#plus-btn").addClass('disabled');
      }
    } else {
      $("#plus-btn").addClass('disabled');
    }
  }

  //座席確保ボタン選択
  seatReserveClick() {
    let isSeparated: boolean;
    this.animationEnableService.sendToRoadFlag(true);
    $('#reservebutton').prop("disabled", true);
    if (this.countSelectVenuemap == 0) {
      if (!this.quantityCheckService.salesUnitCheck(this.selectedProducts, this.quantity)) {
        this.dataUpdate();
        this.route.params.subscribe((params) => {
          if (params && params['performance_id']) {
            //パラメーター切り出し
            this.performanceId = +params['performance_id'];
            //座席確保api
            this.seatStatus.seatReserve(this.performanceId, this.selesSegmentId, this.data).subscribe((response: ISeatsReserveResponse) => {
              this._logger.debug(`get seatReserve(#${this.performanceId}) success`, response);
              this.resSeatIds = response.data.results.seats;
              this.seatStatus.seatReserveResponse = response;
              this.seatPostStatus = response.data.results.status;
              isSeparated = response.data.results.is_separated;
              if (this.seatPostStatus == "OK") {
                // //座席選択の場合、座席名取得
                this.seatNameList = [];
                if (!response.data.results.is_quantity_only) {
                  for (let i = 0; i < this.resSeatIds.length; i++) {
                    this.seatNameList[i] = this.resSeatIds[i].seat_name;
                  }
                  this.resResult = response.data.results;
                  this.resResult.seat_name = this.seatNameList;
                  response.data.results = this.resResult;
                  if (isSeparated) {
                    this.animationEnableService.sendToRoadFlag(false);
                    $('#reservebutton').prop("disabled", false);
                    this.separatDetailDisplay = true;
                    return;
                  } else {
                    this.animationEnableService.sendToRoadFlag(false);
                    this.scrollAddCss();
                    this.reserveBySeatBrowserBackService.deactivate = true;
                    this.router.navigate(["performances/" + this.performanceId + '/select-product/']);
                  }
                }
                //OKの場合、商品選択へ画面遷移
                this.animationEnableService.sendToRoadFlag(false);
                this.scrollAddCss();
                this.reserveBySeatBrowserBackService.deactivate = true;
                this.router.navigate(["performances/" + this.performanceId + '/select-product/']);
              } else {
                this.animationEnableService.sendToRoadFlag(false);
                $('#reservebutton').prop("disabled", false);
                if (response.data.results.reason == "no enough adjacency exception") {
                  this.errorModalDataService.sendToErrorModal('連席で座席を確保できません', '連席でお席をご用意することができません。改めて席をお選び直しください。');
                } else {
                  this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');                  
                }
                this.seatUpdate();//座席情報最新化
              }
            },
              (error) => {
                this.animationEnableService.sendToRoadFlag(false);
                $('#reservebutton').prop("disabled", false);
                this._logger.error('seatReserve error:' + error);
                this.seatUpdate();//座席情報最新化
              });
          }
          else {
            this.animationEnableService.sendToRoadFlag(false);
            $('#reservebutton').prop("disabled", false);
            this._logger.error("エラー:公演IDを取得できません");
            this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
          }
        });
      } else {
        this.animationEnableService.sendToRoadFlag(false);
        $('#reservebutton').prop("disabled", false);
        this.errorModalDataService.sendToErrorModal(
            'エラー',
            this.translateService.instant('{num}席単位でご選択ください。',
            {num:this.quantityCheckService.salesUnitCheck(this.selectedProducts, this.quantity)}));
      }
    } else {
      this.animationEnableService.sendToRoadFlag(false);
      $('#reservebutton').prop("disabled", false);
      this.confirmStockType.emit(true);
    }
  }

  //data更新
  dataUpdate() {
    this.data = {
      "reserve_type": "auto",
      "auto_select_conditions": {
        "stock_type_id": this.selectStockTypeId,
        "quantity": this.quantity
      }
    }
  }

  //NGorERRORの場合、座席情報検索apiを呼び、空席情報を更新する処理
  seatUpdate() {
    let item = this.filterComponent.isSeatDisplay ? SearchConst.SEARCH_TARGET_ITEM.ALL : SearchConst.SEARCH_TARGET_ITEM.STOCKTYPE;
    //キャッシュの削除
    this.filterComponent.cacheClear$.emit(this.filterComponent.activeRegions);
    this.filterComponent.search(item, this.filterComponent.activeRegions.join(','));
  }

  //飛び席モーダル「選び直す」ボタン
  separatedSelectAgain() {
    let releaseResponse: IResult;
    //座席開放API
    this.seatStatus.seatRelease(this.performanceId)
      .subscribe((response: ISeatsReleaseResponse) => {
        this._logger.debug(`seat release(#${this.performanceId}) success`, response);
        releaseResponse = response.data.results;
        if (releaseResponse.status == "NG") {
          this._logger.debug(`seat release error`, response);
          this.errorModalDataService.sendToErrorModal('エラー', '座席を解放できません。');
        }
      },
      (error) => {
        this._logger.debug(`seat release error`, error);
      });
    //モーダル非表示
    this.separatDetailDisplay = false;
  }
  //飛び席モーダル「次へ」ボタン
  separatedNext() {
    this.animationEnableService.sendToRoadFlag(false);
    $('#reservebutton').prop("disabled", false);
    this.reserveBySeatBrowserBackService.deactivate = true;
    this.router.navigate(['performances/' + this.performanceId + '/select-product/']);
    this.scrollAddCss();
  }

  //SP、検索エリアがアクティブ時のモーダルのトップ調整
  modalTopCss() {
    if (this.smartPhoneCheckService.isSmartPhone()) {
      if ($(".choiceAreaAcdBox").css('display') == "block") {
        setTimeout(function () {
          $("#modalWindowAlertBox").css({
            'top': "-220px",
          });
        }, 100);
      } else {
        setTimeout(function () {
          $("#modalWindowAlertBox").css({
            'top': "-37px",
          });
        }, 100);
      }
    }
  }

  modalSizeObtained() {
    let windowHeight: number = $(window).height();
    let headHeight: number = $('header').height() + $('.headArea').height();
    let footerHeight: number = 96;
    //スクロール領域のサイズ
    let scrollSize: number = 0;
    //マップ領域のサイズ
    let mapSize: number = 0;
    //スクロール領域+10px取得
    scrollSize = windowHeight - (headHeight + footerHeight);
    scrollSize += 10;
    //スクロール領域の80%をマップのサイズとして取得
    mapSize = scrollSize * 0.8;
    //ミニマップがない場合は0にする
    if (!this.mapURL) mapSize = 0;
    setTimeout(function () {
      $('.modalWindow-quantity').css({
        'height': scrollSize
      });
      $('#venue-quantity').css({
        'height': mapSize,
      });
      $('#venue-quantity').children("svg").css({
        'height': mapSize,
      });
    }, 0);
  }

  scrollAddCss() {
    //スクロール解除
    $('html').css({
      'height': "100%",
      'overflow-y': "hidden"
    });
    $('body').css({
      'height': "100%",
      'overflow-y': "auto"
    });
  }
}
