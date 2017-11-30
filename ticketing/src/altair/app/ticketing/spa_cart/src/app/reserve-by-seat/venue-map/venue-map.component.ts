import {
  Component,
  Input,
  ElementRef,
  AfterContentInit,
  AfterViewInit,
  OnInit,
  OnDestroy,
  NgModule,
  ViewChild
} from '@angular/core';

import {
  ActivatedRoute,
  Router
} from '@angular/router';

import { BrowserModule }  from '@angular/platform-browser';

import { InlineSVGModule } from 'ng-inline-svg';

// interfaces
import {
  IPerformance,
  IPerformanceInfoResponse,
  IStockType,
  IStockTypeResponse,
  IStockTypesResponse,
  IStockTypesAllResponse,
  IProducts,
  ISeatsReserveResponse,
  ISeatsReleaseResponse,
  IResult,
  ISeatsResponse,
  ISeat,
  IRegion,
  ISalesSegment,
  IEvent,
  ISeatGroup,
  IProductItems
} from '../../shared/services/interfaces';

// components
import { FilterComponent } from '../../reserve-by-seat/filter/filter.component';
import { SeatlistComponent } from '../../reserve-by-seat/seat-list/seat-list.component';
import { ReserveByQuantityComponent } from '../../reserve-by-quantity/reserve-by-quantity.component';

// services
import { PerformancesService } from '../../shared/services/performances.service';
import { SeatStatusService } from '../../shared/services/seat-status.service';
import { SeatsService } from '../../shared/services/seats.service';
import { StockTypesService } from '../../shared/services/stock-types.service';
import { QuentityCheckService } from '../../shared/services/quentity-check.service';
import { StockTypeDataService } from '../../shared/services/stock-type-data.service';
import { ErrorModalDataService } from '../../shared/services/error-modal-data.service';
import { AnimationEnableService } from '../../shared/services/animation-enable.service';
import { CountSelectService } from '../../shared/services/count-select.service';
import { SmartPhoneCheckService } from '../../shared/services/smartPhone-check.service';
import { ReserveBySeatBrowserBackService } from '../../shared/services/reserve-by-seat-browser-back.service';
import { SeatDataService } from '../../shared/services/seatData.service';

// jquery
import * as $ from 'jquery';

// hammer
require('jquery-hammerjs');

//logger
import { Logger } from "angular2-logger/core";

// constants
import { ApiConst } from '../../app.constants';

import { Observable } from 'rxjs/Observable';

const SEAT_COLOR_AVAILABLE = 'rgb(0, 128, 255)';
const SEAT_COLOR_SELECTED = 'rgb(236, 13, 80)';
const SEAT_COLOR_NA = 'rgb(128, 128, 128)';
const REGION_COLOR_NA = 'rgb(128, 128, 128)';
const REGION_COLOR_FEW_SEATS = 'rgb(76, 195, 255)';
const REGION_COLOR_MANY_SEATS = 'rgb(0, 0, 255)';
const STOCK_STATUS_MANY = "◎";
const STOCK_STATUS_FEW = "△";

const SCALE_SEAT = 1.0; // 表示倍率2倍個席表示
const SCALE_MAX = 5.0;  // 表示倍率の最大値

const WINDOW_SM = 768; // スマホか否かの判定に用いる
const SIDE_HEIGHT = 200; //横画面時エラーを出す最大値
const MAX_QUANTITY_DEFAULT = 10; // デフォルトの選択可能枚数

@Component({
  providers: [FilterComponent, ReserveByQuantityComponent],
  selector: 'app-venue-map',
  templateUrl: './venue-map.component.html',
  styleUrls: ['./venue-map.component.css'],
})

export class VenuemapComponent implements OnInit, AfterViewInit {

  @Input() filterComponent: FilterComponent;
  @Input() mapAreaLeftH: number; // reserve-by-seat.component.tsからのマップ領域の高さ設定値
  @ViewChild(ReserveByQuantityComponent)
  quantity: ReserveByQuantityComponent;

  stockTypeIdFromList: number;
  private element: HTMLElement;
  display: boolean = false;
  constructor(
    private el: ElementRef,
    private route: ActivatedRoute,
    private performancesService: PerformancesService,
    private seatStatus: SeatStatusService,
    private stockTypesService: StockTypesService,
    private QuentityChecks: QuentityCheckService,
    private router: Router,
    private reserveByQuantity: ReserveByQuantityComponent,
    private stockTypeDataService: StockTypeDataService,
    private errorModalDataService: ErrorModalDataService,
    private animationEnableService: AnimationEnableService,
    private countSelectService: CountSelectService,
    private smartPhoneCheckService: SmartPhoneCheckService,
    private reserveBySeatBrowserBackService: ReserveBySeatBrowserBackService,
    private seatDataService: SeatDataService,
    private _logger: Logger) {
    this.element = this.el.nativeElement;
  }

  // イベント
  event: IEvent;
  // 公演ID
  performanceId: number;
  // 席種情報
  stockType: IStockType[];
  // 説明
  description: string = '';
  // 選択した座席の説明
  selectedDescription: string = '';
  // 席種名
  stockTypeName: string;
  // 席種ID
  stockTypeId: number;
  // 選択した座席の商品配列
  selectedProducts: IProducts[];
  // 会場図URL
  venueURL: string;
  // 個席データURL
  seatDataURL: string;
  //色ナビurl
  colorNavi: string;
  // 会場図ミニマップURL
  wholemapURL: string;
  // 会場図グリッドサイズ
  venueGridSize: number = 100;
  // 詳細表示フラグ
  displayDetail: boolean = false;
  // 選択した座席情報フラグ
  ticketDetail: boolean = false;
  // ミニマップの表示フラグ
  wholemapFlag: boolean = false;
  // 同一席種かどうかのフラグ
  sameStockType: boolean = true;
  // 選択した座席リストの+-を切り替えるクラス
  active: string = 'active';
  // カート破棄のダイアログを表示するフラグ
  confirmStockType: boolean = false;
  // 選択した座席のid
  selectedSeatId: string = null;
  // 選択した座席とそれに紐づくid
  selectedGroupIds: string[] = [];
  // 選択した座席の座席名
  selectedSeatName: string = null;
  // 選択した座席の座席名
  selectedSeatGroupNames: string[] = [];
  // 選択した座席の席種id
  selectedStockTypeId: number = null;
  // 選択した席種名
  selectedStockTypeName: string;
  // 選択した席種の最大購入数
  selectedStockTypeMaxQuantity: number = null;
  // 選択した席種の最小購入数
  selectedStockTypeMinQuantity: number = null;
  // 選択した座席リスト
  selectedSeatList: string[] = [];
  // 選択した座席の座席名リスト
  selectedSeatNameList: string[] = [];
  // 選択した回数
  countSelect: number = 0;
  // カート破棄確認メッセージ
  confirmationMassage = 'こちらは選択中の座席の席種とは異なりますが、選択中の座席をキャンセルしてこちらの座席を選択しますか？';
  // 1つ前に選択した座席id
  prevSeatId: string = null;
  // 1つ前に選択した席種
  prevStockType: number = null;
  // 選択したブロックのid
  selectedRegionId: string = null;
  // 席種情報
  stockTypeRes: IStockType[];
  // 数受けの席種Id
  quantityStockTypeIds: number[] = [];
  // 席種Id+regionIds
  stockTypeRegionIds: { [key: number]: string[]; } = {};
  // 公演
  performance: IPerformance;
  // 座席情報
  seats: ISeat[];
  // ブロック情報
  regions: IRegion[];
  // 座席選択POST初期データ
  data: {} = {
    'reserve_type': 'seat_choise',
    'selected_seats': []
  }
  // 座席確保ステータス
  seatPostStatus: string;
  // 販売セグメント
  salesSegments: ISalesSegment[];
  // responseに結果を渡すための変数
  resResult: any;
  // 全体の拡大縮小率
  scaleTotal = 1.0;
  // ミニマップ用四角
  rectViewBox: number[];
  // regionId（数受けの席のregion Id）
  regionIds: string[] = [];
  // viewBoxの初期値を格納
  originalViewBox: any[] = null;
  // 表示領域のwidthとheightを求めるため
  svgMap: any;
  D_Width: number;    // 表示領域のwidth
  D_Height: number;   // 表示領域のheigh
  DA: number;         // 表示領域のaspect比
  TA: number;         // 描画領域のaspect比
  SCALE_MIN: number;  // 表示倍率の最小値格納（初期表示の表示倍率）
  // ドラッグ（スワイプ）フラグ
  panFlag: boolean = false;
  originalX: number;
  originalY: number;
  // touchとclickを同時に発生させないため
  touchFlag: boolean = false;
  // pinch時のフラグ
  pinchFlag: boolean = false;
  // pinchスケール
  pinchScale = 1;
  // 表示領域のaspect比に対応するviewBox
  displayViewBox: any[] = null;

  // 座席Element情報
  seat_elements: any = {};

  // 表示中のグリッド
  active_grid: string[] = [];

  //横画面表示エラーモーダルフラグ
  sideProhibition: boolean = false;

  //座席図表示エリア高さ
  seatAreaHeight: number;

  //選択単位フラグ 1席ずつ:true/2席以上ずつ:false
  isGroupedSeats: boolean = true;

  //座席グループ情報
  seatGroups: ISeatGroup[];

  //最終座席情報検索呼び出しチェック状態
  reservedFlag: boolean = true;
  unreservedFlag: boolean = true;

  //region取得完了フラグ
  isRegionObtained: boolean = false;

  //ツールチップ用席種
  tooltipStockType: { name: string; min: number; max: number; region: string[] }[] = [];

  //初期表示測定
  startTime: any;
  endTime: any;

  //ブラウザバックフラグ
  returnFlag = false;

  //ブラウザバック確認モーダルを出さないフラグ
  returnUnconfirmFlag = false;

  ngOnInit() {
    this.startTime = new Date();
    const that = this;
    let drawingRegionTimer;
    let drawingSeatTimer;
    let regionIds = Array();
    this.animationEnableService.sendToRoadFlag(true);

    this.route.params.subscribe((params) => {
      if (params && params['performance_id']) {
        //パラメーター切り出し
        this.performanceId = +params['performance_id'];
        this.performancesService.getPerformance(this.performanceId).subscribe((response: IPerformanceInfoResponse) => {
          this._logger.debug(`get Performance(#${this.performanceId}) success`, response);
          let performanceRes = response;
          this.event = performanceRes.data.event;
          this.performance = performanceRes.data.performance;
          this.performanceId = this.performance.performance_id;
          //this.venueURL = this.performance.venue_map_url;
          //this.seatDataURL = this.performance.seat_data;
          //ダミーURL
          this.venueURL = "../assets/kobo-park-miyagi-2017-spa-no-seats.svg";
          this.seatDataURL = "../assets/newSeatElements.gz";
          //ダミーURL

          // 個席データ取得
          if (this.isSeatDataGet(this.seatDataURL)) {
            this.seatDataService.getSeatData(this.seatDataURL).subscribe((response: any) => {
              this.seat_elements = response;
            });
          }

          this.colorNavi = "https://s3-ap-northeast-1.amazonaws.com/tstar/cart_api/color_sample.svg";
          this.wholemapURL = this.performance.mini_venue_map_url;
          this.salesSegments = this.performance.sales_segments;
          let selesSegmentId: number = this.salesSegments[0].sales_segment_id;
          this.stockTypesService.getStockTypesAll(this.performanceId, selesSegmentId)
            .subscribe((response: IStockTypesAllResponse) => {
              this._logger.debug(`get StockTypesAll(#${this.performanceId}) success`, response);
              let stockTypes: IStockType[] = response.data.stock_types;
              for (let i = 0, len = stockTypes.length; i < len; i++) {
                if (!this.smartPhoneCheckService.isSmartPhone()) {
                  //紐づく商品の最小価格、最大価格を求める
                  let minPrice: number;
                  let maxPrice: number;
                  for (let j = 0, len = stockTypes[i].products.length; j < len; j++) {
                    let price = +stockTypes[i].products[j].price;
                    if (j == 0 || minPrice > price) {
                      minPrice = price;
                    }
                    if (j == 0 || maxPrice < price) {
                      maxPrice = price;
                    }
                  }

                  //tooltip用のデータを作成する
                  this.tooltipStockType[stockTypes[i].stock_type_id] = {
                    name: stockTypes[i].stock_type_name,
                    min: minPrice,
                    max: maxPrice,
                    region: []
                  };
                  for (let j = 0, len = stockTypes[i].regions.length; j < len; j++) {
                    this.tooltipStockType[stockTypes[i].stock_type_id].region.push(stockTypes[i].regions[j]);
                  }
                }

                if (stockTypes[i].is_quantity_only) {
                  let regions: string[] = stockTypes[i].regions;
                  let stockTypeId: number = stockTypes[i].stock_type_id;
                  if (regions.length > 0) {
                    that.stockTypeRegionIds[stockTypeId] = regions;
                    Array.prototype.push.apply(this.regionIds, regions);
                  }
                }
              }
              this.isRegionObtained = true;
              this.stockTypesService.findStockTypesByPerformanceId(this.performanceId).subscribe((response: IStockTypesResponse) => {
                this._logger.debug(`findStockTypesByPerformanceId(#${this.performanceId}) success`, response);
                this.stockType = response.data.stock_types;
              },
                (error) => {
                  this._logger.error('findStockTypesByPerformanceId(#${this.performanceId}) error', error);
                });
              (error) => {
                this._logger.error('[VenueMapComponent]getStockType error', error);
              }
            });
        },
          (error) => {
            this._logger.error('get Performance(#${this.performanceId}) error', error);
            return;
          });
      }
    });

    this.filterComponent.searched$.subscribe((response: ISeatsResponse) => {
      that.seatGroups = response.data.seat_groups;
      that.regions = response.data.regions;
      that.seats = response.data.seats;
      this.reservedFlag = this.filterComponent.reserved;
      this.unreservedFlag = this.filterComponent.unreserved;

      let drawingRegions: IRegion[] = [];
      let drawingRegionIds: string[] = [];

      // フィルタで指定席がONの場合の色付け対象region設定
      if (this.reservedFlag) {
        for (let i = 0, len = that.regions.length; i < len; i++) {
          for (let j = 0, fLen = this.filterComponent.reservedRegionIds.length; j < fLen; j++) {
            if (that.regions[i].region_id == this.filterComponent.reservedRegionIds[j]) {
              let seatRegion: IRegion = { 'region_id': '', 'stock_status': '' };
              seatRegion.region_id = that.regions[i].region_id;
              seatRegion.stock_status = that.regions[i].stock_status;
              drawingRegions.push(seatRegion);
            }
          }
        }
      }

      // フィルタで自由席がONの場合の色付け対象region設定
      if (this.unreservedFlag) {
        for (let i = 0, len = that.regions.length; i < len; i++) {
          for (let j = 0, fLen = this.filterComponent.unreservedRegionIds.length; j < fLen; j++) {
            if (that.regions[i].region_id == this.filterComponent.unreservedRegionIds[j]) {
              let seatRegion: IRegion = { 'region_id': '', 'stock_status': '' };
              seatRegion.region_id = that.regions[i].region_id;
              seatRegion.stock_status = that.regions[i].stock_status;
              drawingRegions.push(seatRegion);
            }
          }
        }
      }

      // regionの色付け開始
      startDrawingRegionTimer(drawingRegions);

      function startDrawingRegionTimer(regions: IRegion[]) {
        drawingRegionTimer = setInterval(function () {
          if (that.svgMap) {
            clearInterval(drawingRegionTimer);
            $(that.svgMap).find('.region').css({ 'fill': REGION_COLOR_NA });
            $(that.svgMap).find('.coloring_region').css({ 'fill': REGION_COLOR_NA });
            for (let i = 0, len = regions.length; i < len; i++) {
              if (regions[i].stock_status == '△') {
                $(that.svgMap).find('#' + regions[i].region_id).css({ 'fill': REGION_COLOR_FEW_SEATS });
                $(that.svgMap).find('#' + regions[i].region_id).find('.coloring_region').css({ 'fill': REGION_COLOR_FEW_SEATS });
              } else if (regions[i].stock_status == '◎') {
                $(that.svgMap).find('#' + regions[i].region_id).css({ 'fill': REGION_COLOR_MANY_SEATS });
                $(that.svgMap).find('#' + regions[i].region_id).find('.coloring_region').css({ 'fill': REGION_COLOR_MANY_SEATS });
              }
            }

            if (!that.smartPhoneCheckService.isSmartPhone()) {
              //ツールチップ用属性の設定
              that.tooltipStockType.forEach(function (value) {
                if (value.region) {
                  for (let j = 0, len = value.region.length; j < len; j++) {
                    $('#' + value.region[j]).attr({
                      stockType: value.name,
                      min: value.min,
                      max: value.max
                    });
                  }
                }
              });
            }
            that.animationEnableService.sendToRoadFlag(false);
          }
        }, 100);
      }

      // seatの色付け開始
      startDrawingSeatTimer();

      function startDrawingSeatTimer() {
        drawingSeatTimer = setInterval(function () {
          if (that.svgMap) {
            clearInterval(drawingSeatTimer);
            that.drawingSeats();
          }
        }, 100);
      }
    });
    // SVGのロード完了チェック
    let svgLoadCompleteTimer = setInterval(function () {
      that.originalViewBox = that.getPresentViewBox();
      if (that.isSeatDataGet(that.seatDataURL)) {
        // viewBox取得　且つ　reserve-by-seatの高さが取得　且つ　seat_elements取得
        if ((that.originalViewBox) && (that.mapAreaLeftH != 0) && (Object.keys(that.seat_elements).length > 0)) {
          clearInterval(svgLoadCompleteTimer);
          that.seatAreaHeight = $("#mapImgBox").height();
          that.svgMap = document.getElementById('mapImgBox').firstElementChild;
          that.mapHome();
          that.endTime = new Date();
          that._logger.info(that.endTime - that.startTime + "ms");
        }
      } else {
        // viewBox取得　且つ　reserve-by-seatの高さが取得
        if ((that.originalViewBox) && (that.mapAreaLeftH != 0)) {
          clearInterval(svgLoadCompleteTimer);
          that.seatAreaHeight = $("#mapImgBox").height();
          that.svgMap = document.getElementById('mapImgBox').firstElementChild;
          that.saveSeatData();
          that.mapHome();
          that.endTime = new Date();
          that._logger.info(that.endTime - that.startTime + "ms");
        }
      }
    }, 200);
    if (!this.smartPhoneCheckService.isSmartPhone()) {
      //ツールチップの表示
      $('#mapAreaLeft').on('mouseenter', '.region', function (e) {
        let tooltip = '';
        if ($(this).attr('stockType')) {
          tooltip += $(this).attr('stockType');
          tooltip += '<br />' + $(this).attr('min') + '円～' + $(this).attr('max') + '円';
        }
        if (tooltip) {
          $('body').append('<div id="tooltip">' + tooltip + '</div>');
          if (e.pageY + 10 + $('#tooltip').height() > $('body').height()) {
            $('#tooltip').css({
              'top': e.pageY - $('#tooltip').height(),
              'left': e.pageX + 10
            });
          } else {
            $('#tooltip').css({
              'top': e.pageY + 10,
              'left': e.pageX + 10
            });
          }
        }
      });
      //ツールチップの移動　ブロック
      $('#mapAreaLeft').on('mousemove', '.region', function (e) {
        if (e.pageY + 10 + $('#tooltip').height() > $('body').height()) {
          $('#tooltip').css({
            'top': e.pageY - $('#tooltip').height(),
            'left': e.pageX + 10
          });
        } else {
          $('#tooltip').css({
            'top': e.pageY + 10,
            'left': e.pageX + 10
          });
        }
      });
      //ツールチップの削除
      $('#mapAreaLeft').on('mouseleave', 'rect, .region', function () {
        $('[id=tooltip]').remove();
      });
    }

    $('#mapAreaLeft').on('mouseenter', 'rect', function (e) {
      let tooltip = '';
      let that = $(this);
      if ($(this).attr('stockType')) {
        tooltip += $(this).attr('stockType');
        tooltip += '<br />' + $(this).attr('min') + '円～' + $(this).attr('max') + '円';
      }

      let text = $(this).text().trim();
      if (text) {
        $(this).attr('title', $(this).text().trim());
        $(this).children().remove();
      }

      if ($(this).attr('title')) {
        if (tooltip) tooltip += '<br />'
        tooltip += decodeURIComponent($(this).attr('title'));
      }
      if (tooltip) {
        $('body').append('<div id="tooltip">' + tooltip + '</div>');
        if (e.pageY + 10 + $('#tooltip').height() > $('body').height()) {
          $('#tooltip').css({
            'top': e.pageY - $('#tooltip').height(),
            'left': e.pageX + 10
          });
        } else {
          $('#tooltip').css({
            'top': e.pageY + 10,
            'left': e.pageX + 10
          });
        }
      }
    });
  }

  //初期ロード完了判定メソッド
  isInitialEnd() {
    let result: boolean = false;
    //全ての初期ロード判定
    if (this.originalViewBox && this.seats && this.isRegionObtained) {
      result = true;
    }

    return result;
  }

  ngAfterViewInit() {
    let FastClick = require('fastclick');
    FastClick.attach(document.body);

    // ホームボタン
    $('#mapBtnHome').on('mousedown touchstart', (event) => {
      if (this.isInitialEnd()) {
        this.touchFlag = true;
        event.preventDefault();
      }
    });
    $('#mapBtnHome').on('mouseup touchend', (event) => {
      if (this.isInitialEnd()) {
        if (this.touchFlag) this.mapHome();
        this.touchFlag = false;
        event.preventDefault();
      }
    });

    // 拡大ボタン
    $('#mapBtnPlus').on('mousedown touchstart', (event) => {
      if (this.isInitialEnd()) {
        this.touchFlag = true;
        event.preventDefault();
      }
    });
    $('#mapBtnPlus').on('mouseup touchend', (event) => {
      if (this.isInitialEnd()) {
        if (this.touchFlag) this.enlargeMap();
        this.touchFlag = false;
        event.preventDefault();
      }
    });

    // 縮小ボタン
    $('#mapBtnMinus').on('mousedown touchstart', (event) => {
      if (this.isInitialEnd()) {
        this.touchFlag = true;
        event.preventDefault();
      }
    });
    $('#mapBtnMinus').on('mouseup touchend', (event) => {
      if (this.isInitialEnd()) {
        if (this.touchFlag) this.shrinkMap();
        this.touchFlag = false;
        event.preventDefault();
      }
    });

    // ブロック・座席のタップ
    $('#mapImgBox').on('mousedown touchstart', (event) => {
      if (this.isInitialEnd()) {
        this.touchFlag = true;
        event.preventDefault();
      }
    });
    $('#mapImgBox').on('mouseup touchend', (event) => {
      if (this.isInitialEnd()) {
        if (this.touchFlag) {
          if ($(event.target).hasClass('region') || $(event.target).parents().hasClass('region')) {
            this.tapRegion(event);
          } else if ($(event.target).hasClass('seat')) {
            this.tapSeat(event);
          }
        }
        this.touchFlag = false;
        event.preventDefault();
      }
    });

    let gestureObj = new Hammer($('#mapImgBox')[0]);
    gestureObj.get('pan').set({ enable: true, threshold: 0, direction: Hammer.DIRECTION_ALL });
    gestureObj.get('pinch').set({ enable: true });

    // パン操作
    gestureObj.on('panstart panmove panend', (event) => {
      if (this.isInitialEnd()) {
        let venueObj = $('#mapImgBox');
        let x, y, viewBoxVals;
        let offsetX = venueObj.offset().left;
        let offsetY = venueObj.offset().top;
        let x_pos = event.center.x - offsetX;
        let y_pos = event.center.y - offsetY;

        switch (event.type) {
          case 'panstart':
            this.originalX = event.deltaX;
            this.originalY = event.deltaY;
            this.panFlag = true;
            break;
          case 'panmove':
            if (this.panFlag) {
              x = event.deltaX - this.originalX;
              y = event.deltaY - this.originalY;
              viewBoxVals = this.getDragViewBox(-x, -y);
              venueObj.children().attr('viewBox', viewBoxVals.join(' ')); // set the viewBox
              this.originalX = event.deltaX;
              this.originalY = event.deltaY;
              if (x_pos < 0 || x_pos > this.D_Width) {
                this.panFlag = false;
              }
              if (y_pos < 0 || y_pos > this.D_Height) {
                this.panFlag = false;
              }
            }
            this.touchFlag = false;
            break;
          case 'panend':
            this.panFlag = false;
            this.setActiveGrid();
            break;
        }
      }
    });

    // ピンチ操作
    gestureObj.on('pinchstart pinchmove pinchend', (event) => {
      if (this.isInitialEnd()) {
        let viewBoxVals: any[];
        let venueObj = $('#mapImgBox');
        let offsetX = venueObj.offset().left;
        let offsetY = venueObj.offset().top;
        let x = event.center.x - offsetX;
        let y = event.center.y - offsetY;
        let scale: number;

        switch (event.type) {
          case 'pinchstart':
            this.pinchFlag = true;
            this.pinchScale = event.scale;
            break;
          case 'pinchmove':
            if (this.pinchFlag) {
              scale = (event.scale - this.pinchScale) + 1;
              viewBoxVals = this.getZoomViewBox(x, y, 1 / scale);
              this.scaleTotal = this.getPresentScale(viewBoxVals);
              if (this.scaleTotal > SCALE_MAX) {
                scale = this.scaleTotal / SCALE_MAX * (1 / scale);
                this.scaleTotal = SCALE_MAX;
                viewBoxVals = this.getZoomViewBox(x, y, scale);
              } else {
                if (this.scaleTotal < this.SCALE_MIN) {
                  this.mapHome();
                  return;
                }
              }
              venueObj.children().attr('viewBox', viewBoxVals.join(' '));
              if (this.scaleTotal >= SCALE_SEAT && !(this.wholemapFlag)) {
                if (($(window).width() <= WINDOW_SM) || (this.countSelect != 0)) {
                  this.stockTypeDataService.sendToSeatListFlag(false);
                  this.seatSelectDisplay(false);

                }
                this.wholemapFlag = true;
                this.onoffRegion(this.regionIds);
              } else {
                if (this.scaleTotal < SCALE_SEAT) {
                  this.onoffRegion(this.regionIds);
                  if (this.countSelect == 0) {
                    this.stockTypeDataService.sendToSeatListFlag(true);
                    this.seatSelectDisplay(true);
                  }
                  this.wholemapFlag = false;
                }
              }
            }
            this.pinchScale = event.scale;
            this.touchFlag = false;
            break;
          case 'pinchend':
            this.pinchFlag = false;
            this.pinchScale = 1;
            break;
        }
        event.preventDefault();
      }
    });

    // マウスホイールの移動量取得
    function extractDelta(e) {
      if (e.wheelDelta) {
        return e.wheelDelta;
      }
      if (e.originalEvent.detail) {
        return e.originalEvent.detail * -40;
      }
      if (e.originalEvent && e.originalEvent.wheelDelta) {
        return e.originalEvent.wheelDelta;
      }
    }

    // マウスホイールによる拡大・縮小
    $('#mapImgBox').bind('mousewheel DOMMouseScroll', (e) => {
      if (this.isInitialEnd()) {
        let viewBoxVals;
        let offsetX = $('#mapImgBox').offset().left;
        let offsetY = $('#mapImgBox').offset().top;
        let x = e.pageX - offsetX;
        let y = e.pageY - offsetY;
        let scale;
        let d = extractDelta(e);
        let venueObj = $(document).find('#mapImgBox');
        if (d > 0) {
          scale = 0.8;
          viewBoxVals = this.getZoomViewBox(x, y, scale);
          this.scaleTotal = this.getPresentScale(viewBoxVals);
          if (this.scaleTotal > SCALE_MAX) {
            if (this.scaleTotal == SCALE_MAX) {
              return;
            } else {
              scale = this.scaleTotal / SCALE_MAX * scale;
              this.scaleTotal = SCALE_MAX;
              viewBoxVals = this.getZoomViewBox(x, y, scale);
            }
          }
          venueObj.children().attr('viewBox', viewBoxVals.join(' '));
          if (this.scaleTotal >= SCALE_SEAT && !(this.wholemapFlag)) {
            if (($(window).width() <= WINDOW_SM) || (this.countSelect != 0)) {
              this.stockTypeDataService.sendToSeatListFlag(false);
              this.seatSelectDisplay(false);
            }
            this.wholemapFlag = true;
            this.onoffRegion(this.regionIds);
            $('[id=tooltip]').remove();
          }
        } else {
          scale = 1.2;
          viewBoxVals = this.getZoomViewBox(x, y, scale);
          this.scaleTotal = this.getPresentScale(viewBoxVals);
          if (this.scaleTotal < this.SCALE_MIN) {
            this.mapHome();
            return;
          }
          venueObj.children().attr('viewBox', viewBoxVals.join(' '));
          if (this.scaleTotal < SCALE_SEAT) {
            this.onoffRegion(this.regionIds);
            if (this.countSelect == 0) {
              this.stockTypeDataService.sendToSeatListFlag(true);
              this.seatSelectDisplay(true);
            }
            this.wholemapFlag = false;
            $('#tooltip').remove();
          }
        }
        e.stopPropagation();
        e.preventDefault();
      }
      e.stopPropagation();
      e.preventDefault();
    });

    // リサイズ処理
    let getHightTimer = null;
    let resizeTimer = null;
    let orientation = window.orientation;
    const that = this;
    //初期表示時横の場合
    getHightTimer = setInterval(() => {
      that.seatAreaHeight = $("#mapImgBox").height();
      if (that.seatAreaHeight > 0) {
        that.sideError();
        clearTimeout(getHightTimer);
      } else if (that.seatAreaHeight == 0 && orientation == 90 || orientation == -90 && this.smartPhoneCheckService.isSmartPhone()) {
        that.sideError();
        clearTimeout(getHightTimer);
      }
    }, 100);

    $(window).resize(() => {
      if (resizeTimer !== false) {
        clearTimeout(resizeTimer);
      }
      resizeTimer = setTimeout(() => {
        this.sideError();
        if (that.originalViewBox && that.mapAreaLeftH != 0) {
          if (this.countSelect == 0) {
            if (!this.smartPhoneCheckService.isSmartPhone()) {
              //席種リストの表示
              this.stockTypeDataService.sendToSeatListFlag(true);
            }
          } else {
            //席を選択していた場合
            if ($('.seatNumberBox').css('display') == 'none') {
              $('#mapAreaRight .closeBtnBox').removeClass('active');
            } else {
              $('#mapAreaRight .closeBtnBox').addClass('active');
            }
          }

          //viewboxの調整
          let resizeViewBox = this.getPresentViewBox(); //調整後のviewbox
          //viewboxがとれたら処理を行う
          if (resizeViewBox) {
            let beforeWidth = this.D_Width; //リサイズ前の表示領域のwidth
            let beforeHeight = this.D_Height; //リサイズ前の表示領域のheight
            this.D_Width = $(this.svgMap).innerWidth(); // 現在の表示領域のwidth
            this.D_Height = $(this.svgMap).innerHeight(); // 現在の表示領域のheight
            this.DA = this.D_Width / this.D_Height; //現在の表示領域のアスペクト比

            //倍率が変わらないようviewboxを現在の表示領域に合わせる
            resizeViewBox[3] = String(parseFloat(resizeViewBox[3]) * this.D_Height / beforeHeight);
            resizeViewBox[2] = String(parseFloat(resizeViewBox[2]) * this.D_Width / beforeWidth);
            $('#mapImgBox').children().attr('viewBox', resizeViewBox.join(' '));

            //アスペクト比の調整と個席表示/非表示の切り替え
            this.setAspectRatio();

            //描画領域が初期領域をはみ出た場合初期表示に戻す
            if (parseFloat(this.displayViewBox[0]) > parseFloat(resizeViewBox[0])) {
              this.mapHome();
            } else if (parseFloat(this.displayViewBox[1]) > parseFloat(resizeViewBox[1])) {
              this.mapHome();
            } else if (parseFloat(this.displayViewBox[0]) + parseFloat(this.displayViewBox[2]) < parseFloat(resizeViewBox[0]) + parseFloat(resizeViewBox[2])) {
              this.mapHome();
            } else if (parseFloat(this.displayViewBox[1]) + parseFloat(this.displayViewBox[3]) < parseFloat(resizeViewBox[1]) + parseFloat(resizeViewBox[3])) {
              this.mapHome();
            }
          }
        }
      }, 200);
    });

    //ブラウザ判別用にユーザーエージェント取得
    let ua = navigator.userAgent.toLowerCase();

    //セッションストレージに履歴数を保持
    if (!sessionStorage.getItem('historyCount')) {
      sessionStorage.setItem('historyCount', history.length.toString());
    } else if (ua.match(/crios/i) && !sessionStorage.getItem('stay') && sessionStorage.getItem('maxHistory')) {
      //iOS+chrome
      if (sessionStorage.getItem('maxHistory') == history.length.toString()) {
        //進むで来た可能性があるためモーダルを表示しない
        that.returnUnconfirmFlag = true;
        //進むで来ていない場合の対策
        let historyCountTemp = history.length.toString();
        setTimeout(function(){
          //まだtrueの場合は開きなおしたため履歴数を更新
          if (that.returnUnconfirmFlag) {
            that.returnUnconfirmFlag = false;
            sessionStorage.setItem('historyCount', historyCountTemp);
          }
        },1000);
      } else {
        //開きなおした場合履歴数を更新する
        sessionStorage.setItem('historyCount', history.length.toString());
      }
    }

    //商品選択へのブラウザバック
    this.reserveBySeatBrowserBackService.modal.subscribe((value)=>{
      that.confirmReturn();
    });

    //他画面へのブラウザバック
    if (ua.match(/crios/i)) {
      $(document).on('click', function(){
        history.pushState(null, null, null);
        $(document).off('click');
      });
    } else {
      let beforeHistory = history.length;
      history.pushState(null, null, null);
      let afterHistory = history.length;
      //pushState前後でhistory.lengthが増えていれば履歴数を更新
      if (!sessionStorage.getItem('stay')) {
        if (beforeHistory < afterHistory) {
          sessionStorage.setItem('historyCount', beforeHistory.toString());
        } else {
          //進まれた場合再読み込み
          if (ua.indexOf('firefox') == -1 || ua.indexOf('android') !== -1 || /iP(hone|(o|a)d)/.test(navigator.userAgent)) {
            location.href = location.href;
          }
        }
      }
    }

    //セッションストレージに滞在フラグを登録
    sessionStorage.setItem('stay', 'true');

    //ブラウザの戻る・進むで発火
    window.addEventListener('popstate', function (e) {
      if (that.returnUnconfirmFlag) {
        that.returnUnconfirmFlag = false;
      } else {
        that.confirmReturn();
        if (ua.match(/crios/i)) {
          history.forward();
        } else {
          history.pushState(null, null, null);
        }
      }
    }, false);
  }

  ngOnDestroy() {
    //リサイズのイベントハンドラを削除
    $(window).off('resize');
  }

  //画面が横向きだった場合エラーモーダルを出す
  sideError() {
    let orientation = window.orientation;
    if ($("#mapImgBox").height() < SIDE_HEIGHT && (orientation == 90 || orientation == -90)) {//座席図領域<定数
      this.sideProhibition = true;
      this.resizeCssTrue();
    } else {
      this.sideProhibition = false;
      this.resizeCssFalse();
    }
  }

  resizeCssTrue() {
    $('html').css({
      'height': "",
      'overflow-y': ""
    });
    $('.choiceArea').css({
      'display': 'none'
    });

    $('html,body').css({
      'width': '100%',
      'height': '100%',
      'overflow-y': 'hidden'
    });
  }

  resizeCssFalse() {
    //スクロール解除
    $('html').css({
      'height': "100%",
      'overflow-y': "hidden"
    });
    $('body').css({
      'height': "100%",
      'overflow-y': "auto"
    });
    $('.choiceArea').css({
      'display': 'block'
    });
  }

  // ブロックのタップ操作
  tapRegion(e: any) {
    let selectedRegionId: string = null;

    if (e.target.id && $(e.target).hasClass('region')) {
      selectedRegionId = e.target.id;
    } else if ($(e.target).parents().hasClass('region')) {
      selectedRegionId = $(e.target).parents('.region')[0].id;
    } else {
      return;
    }
    if (stockStatusCheck(selectedRegionId, this.regions)) {
      if ($.inArray(selectedRegionId, this.regionIds) != -1) {
        // regionIdsを回し、選んだregionIdと同じなら遷移
        for (let x in this.stockTypeRegionIds) {
          for (let i = 0, len = this.stockTypeRegionIds[x][i].length; i < len; i++) {
            if (this.stockTypeRegionIds[x][i] === selectedRegionId) {
              $('html,body').css({
                'height': "",
                'overflow-y': ""
              });
              this.stockTypeDataService.sendToQuentity(+x);
            }
          }
        }
        this.countSelectService.sendToQuentity(this.countSelect);
      } else {
        let scale = this.scaleTotal / SCALE_SEAT; // 1辺の長さの拡大率
        this.scaleTotal = SCALE_SEAT;
        let x_pos = getPositionX(e);
        let y_pos = getPositionY(e);
        let viewBoxVals = this.getZoomViewBox(x_pos, y_pos, scale);
        $('#mapImgBox').children().attr('viewBox', viewBoxVals.join(' '));
        if (($(window).width() <= WINDOW_SM) || (this.countSelect != 0)) {
          this.stockTypeDataService.sendToSeatListFlag(false);
          this.seatSelectDisplay(false);
        }
        this.wholemapFlag = true;
        this.onoffRegion(this.regionIds);
        $('[id=tooltip]').remove();
      }
    }
    function stockStatusCheck(selectedRegionId: string, regions: IRegion[]) {
      let result: boolean = false;
      for (let i = 0, len = regions.length; i < len; i++) {
        if (selectedRegionId == regions[i].region_id) {
          if (regions[i].stock_status == STOCK_STATUS_MANY || regions[i].stock_status == STOCK_STATUS_FEW) {
            result = true;
          }
        }
      }
      return result;
    }
    function getPositionX(e) {
      let offsetX = $('#mapImgBox').offset().left;
      if (e.type == 'touchend') {
        return e.changedTouches[0].pageX - offsetX;
      } else {
        return e.pageX - offsetX;
      }
    }
    function getPositionY(e) {
      let offsetY = $('#mapImgBox').offset().top;
      if (e.type == 'touchend') {
        return e.changedTouches[0].pageY - offsetY;
      } else {
        return e.pageY - offsetY;
      }
    }
  }

  // 座席のタップ操作
  tapSeat(e: any) {
    //初期化
    this.selectedSeatId = e.target.id;
    this.selectedGroupIds = [];
    this.selectedSeatGroupNames = [];
    this.selectedStockTypeMaxQuantity = null;
    //席種id取得
    for (let i = 0; i < this.seats.length; i++) {
      if (this.seats[i].seat_l0_id == this.selectedSeatId) {
        this.selectedStockTypeId = this.seats[i].stock_type_id;
        break;
      }
    }
    //1席ずつか2席以上ずつか判定
    this.isGroupedSeats = true;
    for (let i = 0, len = this.seatGroups.length; i < len; i++) {
      if ($.inArray(this.selectedSeatId, this.seatGroups[i].seat_l0_ids) != -1) {
        this.isGroupedSeats = false;
        this.selectedGroupIds = this.seatGroups[i].seat_l0_ids;
        break;
      }
    }
    //席種に紐づく最大購入数取得＋無い場合1.公演2.イベントの順でセット
    for (let i = 0, len = this.stockType.length; i < len; i++) {
      if (this.selectedStockTypeId == this.stockType[i].stock_type_id) {
        this.selectedStockTypeMaxQuantity = this.stockType[i].max_quantity;
        break;
      }
    }
    if (!this.selectedStockTypeMaxQuantity) {
      this.selectedStockTypeMaxQuantity = this.performance.order_limit;
      if (!this.selectedStockTypeMaxQuantity) {
        this.selectedStockTypeMaxQuantity = this.event.order_limit;
        if (!this.selectedStockTypeMaxQuantity) {
          this.selectedStockTypeMaxQuantity = MAX_QUANTITY_DEFAULT;
        }
      }
    }
    //メイン処理へ
    if (this.isGroupedSeats) {
      this.tapOneSeats(e);
    } else {
      this.tapMultipleSeats(e);
    }
  }

  tapOneSeats(e: any) {
    if (this.changeRgb($(e.target).css('fill')) == SEAT_COLOR_AVAILABLE) {
      if (this.QuentityChecks.maxLimitCheck(this.selectedStockTypeMaxQuantity, this.performance.order_limit, this.event.order_limit, this.selectedSeatList.length + 1)) {
        $(e.target).css({ 'fill': SEAT_COLOR_SELECTED });
        this.selectedSeatName = this.smartPhoneCheckService.isSmartPhone() ? decodeURIComponent($(e.target).children('title').text()) : decodeURIComponent($(e.target).attr('title'));
        this.selectTimes();
      } else {
        this.errorModalDataService.sendToErrorModal('エラー', this.selectedStockTypeMaxQuantity + '席以下でご選択ください。');
      }
    } else if (this.changeRgb($(e.target).css('fill')) == SEAT_COLOR_SELECTED) { // 既に選択した座席を再選択してキャンセル
      let findNum: number = $.inArray(this.selectedSeatId, this.selectedSeatList);
      if (findNum != -1) {
        for (let i = 0; i < this.countSelect; i++) {
          if (this.selectedSeatList[i] == this.selectedSeatId) {
            this.selectedSeatList.splice(i, 1);
            this.selectedSeatNameList.splice(i, 1);
            this.countSelect--;
            break;
          }
        }
      }
      this.selectedCancel();
      if (this.reservedFlag) {
        for (let i = 0; i < this.seats.length; i++) {
          if (this.selectedSeatId == this.seats[i].seat_l0_id) {
            $(e.target).css({ 'fill': SEAT_COLOR_AVAILABLE });
            break;
          }
        }
      }
      this.displayDetail = false;
    }
  }
  tapMultipleSeats(e: any) {
    if (this.changeRgb($(e.target).css('fill')) == SEAT_COLOR_AVAILABLE) {
      if (this.selectedStockTypeId == this.prevStockType) {
        if (this.QuentityChecks.maxLimitCheck(this.selectedStockTypeMaxQuantity, this.performance.order_limit, this.event.order_limit, this.selectedSeatList.length + this.selectedGroupIds.length)) {
          for (let i = 0, len = this.selectedGroupIds.length; i < len; i++) {
            $(this.svgMap).find('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_SELECTED });
            if (this.smartPhoneCheckService.isSmartPhone()) {
              this.selectedSeatGroupNames.push(decodeURIComponent($(this.svgMap).find('#' + this.selectedGroupIds[i]).children('title').text()));
            } else {
              this.selectedSeatGroupNames.push(decodeURIComponent($(this.svgMap).find('#' + this.selectedGroupIds[i]).attr('title')));
            }

          }
          this.selectTimes();
        } else {
          this.errorModalDataService.sendToErrorModal('エラー', this.selectedStockTypeMaxQuantity + '席以下でご選択ください。');
        }
      } else {
        for (let i = 0, len = this.selectedGroupIds.length; i < len; i++) {
          $(this.svgMap).find('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_SELECTED });
          if (this.smartPhoneCheckService.isSmartPhone()) {
            this.selectedSeatGroupNames.push(decodeURIComponent($(this.svgMap).find('#' + this.selectedGroupIds[i]).children('title').text()));
          } else {
            this.selectedSeatGroupNames.push(decodeURIComponent($(this.svgMap).find('#' + this.selectedGroupIds[i]).attr('title')));
          }
        }
        this.selectTimes();
      }
    } else if (this.changeRgb($(e.target).css('fill')) == SEAT_COLOR_SELECTED) { // 既に選択した座席を再選択してキャンセル
      let findNum: number = $.inArray(this.selectedGroupIds[0], this.selectedSeatList);
      if (findNum != -1) {
        this.selectedSeatList.splice(findNum, this.selectedGroupIds.length);
        this.selectedSeatNameList.splice(findNum, this.selectedGroupIds.length);
        this.countSelect = this.selectedSeatList.length;
      }
      this.selectedCancel();
      if (this.reservedFlag) {
        for (let i = 0; i < this.seats.length; i++) {
          if (this.selectedSeatId == this.seats[i].seat_l0_id) {
            for (let j = 0, len = this.selectedGroupIds.length; j < len; j++) {
              $('#' + this.selectedGroupIds[j]).css({ 'fill': SEAT_COLOR_AVAILABLE });
            }
          }
        }
      }
      this.displayDetail = false;
    }
  }
  selectTimes() {
    if (this.countSelect == 0) {
      // 1席目の座席選択
      this.stockTypeId = this.selectedStockTypeId;
      this.getStockTypeInforamtion();
      $('.seatNumberBox').slideDown(300);
      if ($(window).width() <= WINDOW_SM) {
        this.active = '';
      }
      this.sameStockType = true;
    } else {
      if (this.selectedStockTypeId != this.prevStockType) {
        // 席種の異なる座席選択
        this.stockTypeId = this.selectedStockTypeId;
        this.getStockTypeInforamtion();
        this.sameStockType = false;
      } else {
        // 2席目の座席選択，同一席種
        this.displayDetail = false;
        this.sameStockType = true;
        this.addSeatList();
      }
    }
  }
  selectedCancel() {
    if (this.countSelect == 0) {
      $('.seatNumberBox').slideUp(300);
      $('.buyChoiceSeatBox .selectBoxBtn .closeBtnBox').removeClass('active');
      this.ticketDetail = false;
      this.countSelect = 0;
      this.sameStockType = true;
      this.stockTypeId = null;
      this.stockTypeName = '';
      this.filterComponent.selectSeatSearch(this.stockTypeName);
      if ($(window).width() > WINDOW_SM) {
        this.stockTypeDataService.sendToSeatListFlag(true);
        this.seatSelectDisplay(true);
      }
    }
  }
  // ボタンによる拡大
  enlargeMap() {
    if (this.isInitialEnd()) {
      let viewBoxVals = this.getPresentViewBox();
      let venueObj = $('#mapImgBox');
      let x = this.D_Width / 2; // 中心x
      let y = this.D_Height / 2; // 中心y
      let scale = 0.5;  // 1辺の長さの拡大率
      viewBoxVals = this.getZoomViewBox(x, y, scale);
      this.scaleTotal = this.getPresentScale(viewBoxVals);
      if (this.scaleTotal > SCALE_MAX) {
        if (this.scaleTotal == SCALE_MAX) {
          return;
        } else {
          scale = this.scaleTotal / SCALE_MAX * scale;
          this.scaleTotal = SCALE_MAX;
          viewBoxVals = this.getZoomViewBox(x, y, scale);
        }
      }
      venueObj.children().attr('viewBox', viewBoxVals.join(' ')); // viewBoxを設定する
      if (this.scaleTotal >= SCALE_SEAT && !(this.wholemapFlag)) {
        if (($(window).width() <= WINDOW_SM) || (this.countSelect != 0)) {
          this.stockTypeDataService.sendToSeatListFlag(false);
          this.seatSelectDisplay(false);
        }
        this.wholemapFlag = true;
        this.onoffRegion(this.regionIds);
      }
    }
  }

  // ボタンによる縮小
  shrinkMap() {
    if (this.isInitialEnd()) {
      let viewBoxVals = this.getPresentViewBox();
      let venueObj = $('#mapImgBox');
      let x = this.D_Width / 2; // 中心x
      let y = this.D_Height / 2; // 中心y
      let scale = 2.0; // 1辺の長さの拡大率
      viewBoxVals = this.getZoomViewBox(x, y, scale);
      this.scaleTotal = this.getPresentScale(viewBoxVals);
      if (this.scaleTotal < this.SCALE_MIN) {
        this.mapHome();
        return;
      }
      venueObj.children().attr('viewBox', viewBoxVals.join(' ')); // viewBoxを設定する
      if (this.scaleTotal < SCALE_SEAT) {
        this.onoffRegion(this.regionIds);
        if (this.countSelect == 0) {
          this.stockTypeDataService.sendToSeatListFlag(true);
          this.seatSelectDisplay(true);
        }
        this.wholemapFlag = false;
      }
    }
  }

  // 初期状態
  mapHome() {
    if (this.countSelect == 0) {
      this.stockTypeDataService.sendToSeatListFlag(true);
      this.seatSelectDisplay(true);
    }

    let resizeTimer = setTimeout(() => {
      this.D_Width = $(this.svgMap).innerWidth(); // 表示窓のwidth
      this.D_Height = $(this.svgMap).innerHeight(); // 表示窓のheight
      this.DA = this.D_Width / this.D_Height;
      this.scaleTotal = this.getPresentScale(this.originalViewBox);
      this.SCALE_MIN = this.scaleTotal;
      this.wholemapFlag = false;
      // svgのoriginalViweBoxと表示領域のアスペクト比を合わせる
      this.displayViewBox = this.originalViewBox.concat();
      this.TA = parseFloat(this.originalViewBox[2]) / parseFloat(this.originalViewBox[3]);
      if (this.DA >= this.TA) {
        this.displayViewBox[2] = String(this.D_Width * parseFloat(this.displayViewBox[3]) / this.D_Height);
        this.displayViewBox[0] = String(parseFloat(this.displayViewBox[0]) - (parseFloat(this.displayViewBox[2]) - parseFloat(this.originalViewBox[2])) / 2);
      } else {
        this.displayViewBox[3] = String(this.D_Height * parseFloat(this.displayViewBox[2]) / this.D_Width);
        this.displayViewBox[1] = String(parseFloat(this.displayViewBox[1]) - (parseFloat(this.displayViewBox[3]) - parseFloat(this.originalViewBox[3])) / 2);
      }
      $('#mapImgBox').children().attr('viewBox', this.displayViewBox.join(' ')); // viewBoxを初期値に設定
      this.onoffRegion(this.regionIds);
    }, 0);
  }

  // 現在のviewBoxの値を取得
  getPresentViewBox(): any {
    let viewBox = $('#mapImgBox').children().attr('viewBox');
    return (viewBox) ? viewBox.split(' ') : null;
  }

  //座席選択時の画面拡大縮小
  seatSelectDisplay(flag: boolean) {
    let windowHeight = $(window).height();
    let allHead: number = $('header').height(); + $('.headArea').height(); + $('.choiceArea').height();;
    let orientation = window.orientation;
    if (flag) {
      if (this.smartPhoneCheckService.isSmartPhone()) {
        if (orientation == 0 || orientation == 180) {//縦向き
          if (this.seatAreaHeight) {
            $('#mapAreaLeft').css({
              'height': this.seatAreaHeight,
            });
            let resizeTimer = setTimeout(() => {
              this.setAspectRatio();
            }, 0);
          }
        }
      }
    } else {
      if (this.smartPhoneCheckService.isSmartPhone()) {
        if (orientation == 0 || orientation == 180) {//縦向き
          $('#mapAreaLeft').css({
            'height': windowHeight - allHead,
          });
          let resizeTimer = setTimeout(() => {
            this.setAspectRatio();
          }, 0);
        }
      }
    }
  }
  //現在のアスペクト比を合わせる
  setAspectRatio() {
    this.D_Width = $(this.svgMap).innerWidth(); // 表示窓のwidth
    this.D_Height = $(this.svgMap).innerHeight(); // 表示窓のheight
    this.DA = this.D_Width / this.D_Height;
    // svgのoriginalViweBoxと表示領域のアスペクト比を合わせる
    this.displayViewBox = this.originalViewBox.concat();
    this.TA = parseFloat(this.originalViewBox[2]) / parseFloat(this.originalViewBox[3]);
    if (this.DA >= this.TA) {
      this.displayViewBox[2] = String(this.D_Width * parseFloat(this.displayViewBox[3]) / this.D_Height);
      this.displayViewBox[0] = String(parseFloat(this.displayViewBox[0]) - (parseFloat(this.displayViewBox[2]) - parseFloat(this.originalViewBox[2])) / 2);
    } else {
      this.displayViewBox[3] = String(this.D_Height * parseFloat(this.displayViewBox[2]) / this.D_Width);
      this.displayViewBox[1] = String(parseFloat(this.displayViewBox[1]) - (parseFloat(this.displayViewBox[3]) - parseFloat(this.originalViewBox[3])) / 2);
    }
    this.onoffRegion(this.regionIds);
  }


  // 現在の画像width/表示窓widthの比
  getPresentRatioW(viewBoxValues: any): number {
    let ratioW = parseFloat(viewBoxValues[2]) / this.D_Width; // 拡大前の 画像width/表示窓width
    return ratioW;
  }

  // 現在の画像height/表示窓heightの比
  getPresentRatioH(viewBoxValues: any): number {
    let ratioH = parseFloat(viewBoxValues[3]) / this.D_Height; // 拡大前の 画像height/表示窓height
    return ratioH;
  }

  // 現在の表示倍率を求める
  getPresentScale(viewBoxValues: any): number {
    this.TA = parseFloat(viewBoxValues[2]) / parseFloat(viewBoxValues[3]);
    if (this.DA >= this.TA) {
      return (this.D_Height / parseFloat(viewBoxValues[3]));
    } else {
      return (this.D_Width / parseFloat(viewBoxValues[2]));
    }
  }

  // 拡大・縮小後ののviewBoxの値を取得
  getZoomViewBox(x: number, y: number, scale: number): any {
    let viewBoxValues = this.getPresentViewBox();
    let viewBoxVals = [];
    let ratioW = this.getPresentRatioW(viewBoxValues); // 拡大前の 画像width/表示窓width
    let ratioH = this.getPresentRatioH(viewBoxValues); // 拡大前の 画像height/表示窓height
    viewBoxVals[2] = scale * parseFloat(viewBoxValues[2]); // 拡大後のwidth
    viewBoxVals[3] = scale * parseFloat(viewBoxValues[3]); // 拡大後のheight
    // 拡大前と後でダブルクリックした点が表示窓上の同じ点になるようにviewBoxの始点を求める
    // （拡大前）－（拡大後）の差が拡大後の始点x, y　
    viewBoxVals[0] = (x * ratioW + parseFloat(viewBoxValues[0])) - (viewBoxVals[2] / this.D_Width * x);
    viewBoxVals[1] = (y * ratioH + parseFloat(viewBoxValues[1])) - (viewBoxVals[3] / this.D_Height * y);
    return viewBoxVals;
  }

  // ドラッグ処理のviewBoxの値を取得
  getDragViewBox(x: number, y: number): any {
    let viewBoxValues = this.getPresentViewBox();
    let viewBoxVals = [];
    let scale = this.getPresentScale(viewBoxValues);
    viewBoxVals[0] = parseFloat(viewBoxValues[0]);    // Convert string 'numeric' values to actual numeric values.
    viewBoxVals[1] = parseFloat(viewBoxValues[1]);
    viewBoxVals[2] = parseFloat(viewBoxValues[2]);
    viewBoxVals[3] = parseFloat(viewBoxValues[3]);
    viewBoxVals[0] += (x / scale);
    if (viewBoxVals[0] < parseFloat(this.displayViewBox[0])) {
      viewBoxVals[0] = parseFloat(this.displayViewBox[0]);
    } else {
      if ((viewBoxVals[0] + viewBoxVals[2]) > (parseFloat(this.displayViewBox[0]) + parseFloat(this.displayViewBox[2]))) {
        viewBoxVals[0] -= (viewBoxVals[0] + viewBoxVals[2]) - (parseFloat(this.displayViewBox[0]) + parseFloat(this.displayViewBox[2]));
      }
    }
    viewBoxVals[1] += (y / scale);
    if (viewBoxVals[1] < parseFloat(this.displayViewBox[1])) {
      viewBoxVals[1] = parseFloat(this.displayViewBox[1]);
    } else {
      if ((viewBoxVals[1] + viewBoxVals[3]) > (parseFloat(this.displayViewBox[1]) + parseFloat(this.displayViewBox[3]))) {
        viewBoxVals[1] -= (viewBoxVals[1] + viewBoxVals[3]) - (parseFloat(this.displayViewBox[1]) + parseFloat(this.displayViewBox[3]));
      }
    }
    return viewBoxVals;
  }

  // 個席表示/非表示処理
  onoffRegion(regionIds: any) {
    let region: string;
    let flag: number;

    if (this.scaleTotal < SCALE_SEAT) {
      $(".region").each(function () {
        region = $(this).attr('id');
        flag = $.inArray(region, regionIds);
        if (flag == -1) {
          $(this).css({ 'display': 'inline' });
        }
      });
    } else {
      $(".region").each(function () {
        region = $(this).attr('id');
        flag = $.inArray(region, regionIds);
        if (flag == -1) {
          $(this).css({ 'display': 'none' });
        }
      });
    }
    this.setActiveGrid();
  }

  // SVGの座席データを[連席ID, Element]として保持してDOMツリーから削除
  saveSeatData() {
    let els = document.querySelectorAll('.seat');

    let seat_data = {};
    for (let i = 0; i < els.length; i++) {
      let grid_class = (<SVGAnimatedString>(<SVGElement>els[i]).className).baseVal;
      grid_class = grid_class.substr(grid_class.indexOf('grid'), 13);
      let row_id = $(els[i].parentNode).attr('id');

      if (!(grid_class in seat_data)) {
        seat_data[grid_class] = {};
      }
      if (!(row_id in seat_data[grid_class])) {
        seat_data[grid_class][row_id] = [];
      }

      (<HTMLElement>els[i]).style.display = 'inline';
      let seat_id = $(els[i]).attr('id');
      let title = $(els[i]).find('title').text();
      $(els[i]).find('title').text(encodeURIComponent(title));
      let seat_el_str = new XMLSerializer().serializeToString(els[i]);
      seat_el_str = seat_el_str.replace('xmlns="http://www.w3.org/2000/svg" ', '');
      seat_el_str = seat_el_str.replace(/\r?\n/g, '').replace(/ +/g,' ');
      let seat_el = {};
      seat_el[seat_id] = seat_el_str;
      seat_data[grid_class][row_id].push(seat_el);
      this.seat_elements = seat_data;
    }
    $('.seat').remove();
    if (!this.smartPhoneCheckService.isSmartPhone()) $('svg').find('title').remove();
  }

  // 現在の描画サイズに合わせて表示するグリッドを決定し、座席データを動的に追加・削除
  setActiveGrid() {
    if (this.scaleTotal >= SCALE_SEAT) {
      let viewBox = this.getPresentViewBox();
      let grid_x_from = Math.floor(viewBox[0] / this.venueGridSize) - 1;
      let grid_y_from = Math.floor(viewBox[1] / this.venueGridSize) - 1;
      let grid_x_to = Math.floor((Number(viewBox[0]) + Number(viewBox[2])) / this.venueGridSize) + 1;
      let grid_y_to = Math.floor((Number(viewBox[1]) + Number(viewBox[3])) / this.venueGridSize) + 1;
      let $svg = $(this.svgMap);
      let next_active_grid: string[] = [];
      let isRedrawSeats: boolean = false;
      for (let x = grid_x_from; x <= grid_x_to; x++) {
        for (let y = grid_y_from; y <= grid_y_to; y++) {
          let grid_class: string = 'grid_';
          grid_class += (x >= 0) ? 'p' : 'm';
          grid_class += ('000' + x).slice(-3);
          grid_class += (y >= 0) ? 'p' : 'm';
          grid_class += ('000' + y).slice(-3);
          if (this.seat_elements[grid_class]) {
            next_active_grid.push(grid_class);
          }
        }
      }

      // 表示から非表示
      for (let i = 0; i < this.active_grid.length; i++) {
        if (next_active_grid.indexOf(this.active_grid[i]) == -1) {
          let row_data = this.seat_elements[this.active_grid[i]];
          for (let row_id in row_data) {
            let seat_data = row_data[row_id];
            let content = "";
            for (let seat_idx = 0; seat_idx < seat_data.length; seat_idx++) {
              for (let seat_id in seat_data[seat_idx]) {
                let delete_el = document.getElementById(seat_id);
                delete_el.parentNode.removeChild(delete_el);
              }
            }
          }
        }
      }

      // 非表示から表示
      for (let i in next_active_grid) {
        if (this.active_grid.indexOf(next_active_grid[i]) == -1) {
          let row_data = this.seat_elements[next_active_grid[i]];
          for (let row_id in row_data) {
            let seat_data = row_data[row_id];
            let content = "";
            for (let seat_idx = 0; seat_idx < seat_data.length; seat_idx++) {
              for (let seat_id in seat_data[seat_idx]) {
                content += seat_data[seat_idx][seat_id];
              }
            }
            document.getElementById(row_id).innerHTML += content;
            isRedrawSeats = true;
          }
        }
      }
      this.active_grid = next_active_grid;
      if (isRedrawSeats) this.drawingSeats();
    } else {
      for (let i = 0; i < this.active_grid.length; i++) {
        let els = this.seat_elements[this.active_grid[i]];
        for (let key in els) {
          document.getElementById(key).textContent = null;
        }
      }
      this.active_grid = [];
    }
  }

  // 座席要素の色付け
  drawingSeats() {
    if (!(this.seats)) return;
    $(this.svgMap).find('.seat').css({ 'fill': SEAT_COLOR_NA });


    // フィルタで指定席がONの場合のみ空席の色付け
    if (this.reservedFlag) {
      // 空席の色付け
      for (let i = 0, len = this.seats.length; i < len; i++) {
        if (this.seats[i].is_available) {
          $('#' + this.seats[i].seat_l0_id).css({ 'fill': SEAT_COLOR_AVAILABLE });
        }

        if (!this.smartPhoneCheckService.isSmartPhone()) {
          let stockType = this.seats[i].stock_type_id ? this.tooltipStockType[this.seats[i].stock_type_id] : null;
          if (stockType) {
            $('#' + this.seats[i].seat_l0_id).attr({
              stockType: stockType.name,
              min: stockType.min,
              max: stockType.max
            });
          }
        }
      }
    }

    // 座席が選択されていた場合の色付け
    for (let i = 0; i < this.selectedSeatList.length; i++) {
      $('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_SELECTED });
    }
  }

  // 詳細情報の表示
  showDialog(value: any) {
    this.displayDetail = true;
    this.modalTopCss();
    // 押下したボタンの座席名
    this.selectedSeatName = value;
    let flag = $.inArray(this.selectedSeatName, this.selectedSeatNameList);
    this.selectedSeatId = this.selectedSeatList[flag];
    this.selectedStockTypeName = this.stockTypeName;
    this.selectedDescription = this.description;
    // 押下したボタンの座席idの席種
    for (let i = 0; i < this.countSelect; i++) {
      if (this.selectedSeatId == this.seats[i].seat_l0_id) {
        this.selectedStockTypeId = this.seats[i].stock_type_id;
        break;
      }
    }
  }

  // ダイアログの消去
  removeDialog() {
    if (this.isGroupedSeats) {
      $('#' + this.selectedSeatId).css({ 'fill': SEAT_COLOR_NA });
      if (this.reservedFlag) {
        for (let i = 0; i < this.seats.length; i++) {
          if (this.selectedSeatId == this.seats[i].seat_l0_id) {
            $('#' + this.seats[i].seat_l0_id).css({ 'fill': SEAT_COLOR_AVAILABLE });
            break;
          }
        }
      }
      let findNum: number = $.inArray(this.selectedSeatId, this.selectedSeatList);
      if (findNum != -1) {
        this.selectedSeatList.splice(findNum, 1);
        this.selectedSeatNameList.splice(findNum, 1);
        this.countSelect--;
      }
    } else {
      for (let i = 0, len = this.selectedGroupIds.length; i < len; i++) {
        $('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_NA });
      }
      if (this.reservedFlag) {
        for (let i = 0, len = this.selectedGroupIds.length; i < len; i++) {
          $('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
        }
      }
      let findNum: number = $.inArray(this.selectedGroupIds[0], this.selectedSeatList);
      if (findNum != -1) {
        this.selectedSeatList.splice(findNum, this.selectedGroupIds.length);
        this.selectedSeatNameList.splice(findNum, this.selectedGroupIds.length);
        this.countSelect = this.selectedSeatList.length;
      }
    }
    this.displayDetail = false;
    if (this.countSelect == 0) {
      this.ticketDetail = false;
      if (($(window).width() > WINDOW_SM) || (this.scaleTotal < SCALE_SEAT)) {
        this.seatSelectDisplay(false);
      }
    }
  }

  // リストへの追加
  addSeatList() {
    this.displayDetail = false;
    this.ticketDetail = true;
    this.stockTypeDataService.sendToIsSearchFlag(true);
    this.stockTypeDataService.sendToSeatListFlag(false);
    if (this.sameStockType) {
      if (this.selectedSeatList.length == 0) {
        this.stockTypeName = this.selectedStockTypeName;

        this.description = this.selectedDescription;
        this.filterComponent.selectSeatSearch(this.stockTypeName);
      }
      if (this.isGroupedSeats) {
        let findNum: number = $.inArray(this.selectedSeatId, this.selectedSeatList);
        if (findNum == -1) {
          this.selectedSeatList[this.countSelect] = this.selectedSeatId;
          this.selectedSeatNameList[this.countSelect] = this.selectedSeatName;
          this.countSelect++;
          this.prevSeatId = this.selectedSeatId;
          this.prevStockType = this.selectedStockTypeId;
        }
      } else {
        let findNum: number = $.inArray(this.selectedSeatId, this.selectedSeatList);
        if (findNum == -1) {
          Array.prototype.push.apply(this.selectedSeatList, this.selectedGroupIds);
          Array.prototype.push.apply(this.selectedSeatNameList, this.selectedSeatGroupNames);
          this.countSelect = this.selectedSeatList.length;
          this.prevSeatId = this.selectedSeatId;
          this.prevStockType = this.selectedStockTypeId;
        }
      }
    } else {
      this.confirmStockType = true;
    }
  }

  // リストから削除（席種の異なる座席を選択した場合）
  removeSeatList() {
    this.stockTypeName = this.selectedStockTypeName;
    this.description = this.selectedDescription;
    for (let i = 0; i <= this.countSelect; i++) {
      $('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_NA });
      if (this.isGroupedSeats) {
        for (let j = 0; j < this.seats.length; j++) {
          if (this.selectedSeatList[i] == this.seats[j].seat_l0_id) {
            $('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
            break;
          }
        }
      } else {
        for (let j = 0; j < this.seats.length; j++) {
          if (this.selectedSeatList[i] == this.seats[j].seat_l0_id) {
            $('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
          }
        }
      }
    }
    this.selectedSeatList.length = 0;
    this.selectedSeatNameList.length = 0;
    this.countSelect = 0;
    if (!this.sameStockType) { // region選択された場合を除くため
      if (this.isGroupedSeats) {
        this.selectedSeatList[this.countSelect] = this.selectedSeatId;
        this.selectedSeatNameList[this.countSelect] = this.selectedSeatName;
        this.countSelect++;
      } else {
        Array.prototype.push.apply(this.selectedSeatList, this.selectedGroupIds);
        Array.prototype.push.apply(this.selectedSeatNameList, this.selectedSeatGroupNames);
        this.countSelect = this.selectedSeatList.length;
      }
      this.confirmStockType = false;
      this.prevSeatId = this.selectedSeatId;
      this.prevStockType = this.selectedStockTypeId;
      this.sameStockType = true;
      this.filterComponent.selectSeatSearch(this.stockTypeName);
    } else { // region選択された場合を数受の処理へ
      if (this.stockTypeIdFromList) { // seat-listのおまかせで購入が押された場合
        this.stockTypeDataService.sendToQuentity(this.stockTypeIdFromList);
      } else {
        this.display = false;
        this.countSelectService.sendToQuentity(this.countSelect);
        this.quantity.seatReserveClick();
      }
      this.confirmStockType = false;
      this.ticketDetail = false;
      this.stockTypeDataService.sendToIsSearchFlag(false);
    }
  }

  // 座席ボタンのｘ印から除去
  removeSeatListFromBtn(value: any, event) {
    let rmSeatIds: string[] = [];
    // 押下したボタンの座席名
    event.stopPropagation();
    this.selectedSeatName = value;
    for (let i = 0; i < this.countSelect; i++) {
      if (this.selectedSeatName == this.selectedSeatNameList[i]) {
        this.selectedSeatId = this.selectedSeatList[i];
        break;
      }
    }
    // 押下したボタンの座席idの席種
    for (let i = 0; i < this.countSelect; i++) {
      if (this.selectedSeatId == this.seats[i].seat_l0_id) {
        this.selectedStockTypeId = this.seats[i].stock_type_id;
        break;
      }
    }
    if (this.isGroupedSeats) {
      $('#' + this.selectedSeatId).css({ 'fill': SEAT_COLOR_AVAILABLE });
      let findNum: number = $.inArray(this.selectedSeatId, this.selectedSeatList);
      if (findNum != -1) {
        this.selectedSeatList.splice(findNum, 1);
        this.selectedSeatNameList.splice(findNum, 1);
        this.countSelect--;
      }
    } else {
      for (let i = 0, len = this.seatGroups.length; i < len; i++) {
        if ($.inArray(this.selectedSeatId, this.seatGroups[i].seat_l0_ids) != -1) {
          rmSeatIds = this.seatGroups[i].seat_l0_ids;
        }
      }
      for (let i = 0, len = rmSeatIds.length; i < len; i++) {
        $(this.svgMap).find('#' + rmSeatIds[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
      }
      let findNum: number = $.inArray(rmSeatIds[0], this.selectedSeatList);
      if (findNum != -1) {
        this.selectedSeatList.splice(findNum, rmSeatIds.length);
        this.selectedSeatNameList.splice(findNum, rmSeatIds.length);
        this.countSelect = this.selectedSeatList.length;
      }
    }
    if (this.countSelect == 0) {
      this.ticketDetail = false;
      this.stockTypeDataService.sendToIsSearchFlag(false);
      this.sameStockType = true;
      this.stockTypeName = '';
      this.filterComponent.selectSeatSearch(this.stockTypeName);
      if (($(window).width() > WINDOW_SM) || (this.scaleTotal < SCALE_SEAT)) {
        this.stockTypeDataService.sendToSeatListFlag(true);
        this.seatSelectDisplay(true);
      }
    }
    this.displayDetail = false;
  }

  // カート破棄のダイアログの非表示
  removeConfirmation() {
    this.confirmStockType = false;
    this.display = false;
  }

  // 席種情報取得
  getStockTypeInforamtion() {
    if (this.performanceId && this.salesSegments[0].sales_segment_id && this.stockTypeId) {
      this.stockTypesService.getStockType(this.performanceId, this.salesSegments[0].sales_segment_id, this.stockTypeId)
        .subscribe((response: IStockTypeResponse) => {
          this._logger.debug(`get stockType(#${this.performanceId}) success`, response);
          let stockType: IStockType = response.data.stock_types[0];
          this.selectedStockTypeName = stockType.stock_type_name;
          this.selectedProducts = stockType.products;
          this.selectedDescription = stockType.description ? stockType.description : '';
          this.displayDetail = true;
          this.modalTopCss();
        },
        (error) => {
          this.removeDialog();
          this._logger.error('stockType error', error);
        });
    } else {
      this.removeDialog();
      this._logger.error("パラメータに異常が発生しました。");
      this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
    }
  }

  //選択中の座席クリア
  seatClearClick() {
    //色クリア
    for (let i = 0; i <= this.countSelect; i++) {
      $('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_NA });
    }
    //選択クリア
    this.selectedSeatList = [];
    this.selectedSeatNameList = [];
    this.countSelect = 0;
    this.stockTypeDataService.sendToIsSearchFlag(false);
    this.ticketDetail = false;
    this.mapHome();
    this.filterComponent.clearClick();
  }

  // 座席確保ボタン選択
  seatReserveClick() {
    this.animationEnableService.sendToRoadFlag(true);
    $('.reserve').prop("disabled", true);
    this.selectedStockTypeMinQuantity = null;
    let quantity = this.selectedSeatList.length;

    for (let i = 0, len = this.stockType.length; i < len; i++) {
      if (this.selectedStockTypeId == this.stockType[i].stock_type_id) {
        this.selectedStockTypeMinQuantity = this.stockType[i].min_quantity;
        break;
      }
    }
    if (this.QuentityChecks.minLimitCheck(this.selectedStockTypeMinQuantity, quantity)) {
      if (!this.QuentityChecks.salesUnitCheck(this.selectedProducts, quantity)) {
        // 選択した座席を設定
        this.dataUpdate();
        this.seatStatus.seatReserve(this.performanceId, this.salesSegments[0].sales_segment_id, this.data).subscribe((response: ISeatsReserveResponse) => {
          this._logger.debug(`get seatReserve(#${this.performanceId}) success`, response);
          this.resResult = response.data.results;
          this.resResult.seat_name = this.selectedSeatNameList;
          response.data.results = this.resResult;
          this.seatStatus.seatReserveResponse = response;
          this.seatPostStatus = response.data.results.status;
          if (this.seatPostStatus == 'NG') {
            this.animationEnableService.sendToRoadFlag(false);
            $('.reserve').prop("disabled", false);
            this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');
            this.seatUpdate();  // 座席情報最新化
          } else {
            this.animationEnableService.sendToRoadFlag(false);
            this.reserveBySeatBrowserBackService.deactivate = true;
            this.router.navigate(['performances/' + this.performanceId + '/select-product/']);
          }
        },
          (error) => {
            this.animationEnableService.sendToRoadFlag(false);
            $('.reserve').prop("disabled", false);
            this._logger.error('seatReserve error', error);
            this.seatUpdate();//座席情報最新化
          });
      } else {
        this.animationEnableService.sendToRoadFlag(false);
        $('.reserve').prop("disabled", false);
        this.errorModalDataService.sendToErrorModal('エラー', this.QuentityChecks.salesUnitCheck(this.selectedProducts, quantity) + '席単位でご選択ください。');
      }
    } else {
      this.animationEnableService.sendToRoadFlag(false);
      $('.reserve').prop("disabled", false);
      if (quantity) {
        this.errorModalDataService.sendToErrorModal('エラー', this.selectedStockTypeMinQuantity + '席以上でご選択ください。');
      } else {
        this.errorModalDataService.sendToErrorModal('エラー', 1 + '席以上でご選択ください。');
      }
    }
  }

  // 選択した座席をポストするためのデータに格納
  dataUpdate() {
    this.data = {
      'reserve_type': 'seat_choise',
      'selected_seats': this.selectedSeatList
    }
  }

  // 座席情報検索更新
  seatUpdate() {
    // NGorERRORの場合、座席情報検索apiを呼び、空席情報を更新する処理
    this.filterComponent.search();
  }

  // モーダルウィンドウを閉じる
  removeModalWindow() {
    if (this.isGroupedSeats) {
      if ($.inArray(this.selectedSeatId, this.selectedSeatList) == -1) {
        $('#' + this.selectedSeatId).css({ 'fill': SEAT_COLOR_AVAILABLE });
      }
    } else {
      let rmSeatIds: string[] = [];
      for (let i = 0, len = this.seatGroups.length; i < len; i++) {
        if ($.inArray(this.selectedSeatId, this.seatGroups[i].seat_l0_ids) != -1) {
          rmSeatIds = this.seatGroups[i].seat_l0_ids;
        }
      }
      for (let i = 0, len = rmSeatIds.length; i < len; i++) {
        $('#' + rmSeatIds[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
      }
    }
    this.displayDetail = false;
  }

  // ミニマップ用四角
  ngAfterViewChecked() {
    if (this.wholemapFlag) {
      let svg = document.getElementById('mapImgBoxS').firstElementChild;
      if (svg) {
        let viewRect = document.getElementById('minimap-rect');
        if (viewRect) {
          this.moveRect(viewRect);
        } else {
          this.makeRect(svg);
        }
      }
    }
  }

  private makeRect(svg) {
    let viewBox = this.getPresentViewBox();
    let rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', viewBox[0]);
    rect.setAttribute('y', viewBox[1]);
    rect.setAttribute('width', viewBox[2]);
    rect.setAttribute('height', viewBox[3]);
    rect.setAttribute('style', 'fill:##c63f44;opacity:0.8;');
    rect.setAttribute('id', 'minimap-rect');
    svg.appendChild(rect);
  }

  private moveRect(viewRect) {
    let viewBox = this.getPresentViewBox();
    viewRect.setAttribute('x', viewBox[0]);
    viewRect.setAttribute('y', viewBox[1]);
    viewRect.setAttribute('width', viewBox[2]);
    viewRect.setAttribute('height', viewBox[3]);
  }
  //cssが16進数か判定する
  changeRgb(value: any) {
    let text = value.substr(0, 3);
    if (text != "rgb") {
      let red = parseInt(value.substring(1, 3), 16);
      let green = parseInt(value.substring(3, 5), 16);
      let blue = parseInt(value.substring(5, 7), 16);
      return "rgb(" + red + ", " + green + ", " + blue + ")";
    }
    return value;
  }
  //SP、検索エリアがアクティブ時のモーダルのトップ調整
  modalTopCss() {
    if (this.smartPhoneCheckService.isSmartPhone()) {
      if ($(".choiceAreaAcdBox").css('display') == "block") {
        setTimeout(function () {
          $("#modalWindowAlertBox").css({
            'top': "-250px",
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

  //ブラウザバック確認モーダルを出す
  public confirmReturn() {
    this.confirmStockType = true;
    this.returnFlag = true;
  }

  //直前のサイトへ戻る
  returnPrevious() {
    window.removeEventListener('popstate');
    var ua = window.navigator.userAgent.toLowerCase();
    if (ua.match(/crios/i)) {
      //進む判定用に履歴数を保持
      sessionStorage.setItem('maxHistory', history.length.toString());
    }

    //滞在フラグを削除
    sessionStorage.removeItem('stay');

    let backCount = -(history.length - Number(sessionStorage.getItem('historyCount')) + 1);
    if(ua.indexOf('msie') != -1 || ua.indexOf('trident') != -1) {
      window.addEventListener('popstate', function(){
        history.go(backCount);
      });
      history.go(-(this.reserveBySeatBrowserBackService.selectProductCount + 1));
    } else {
      history.go(backCount);
    }
  }
}