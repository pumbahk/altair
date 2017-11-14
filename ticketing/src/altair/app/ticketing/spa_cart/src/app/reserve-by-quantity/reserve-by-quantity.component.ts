import { Component, NgModule, OnInit, Input, Output ,EventEmitter} from '@angular/core';
//component
import { SeatlistComponent } from '../reserve-by-seat/seat-list/seat-list.component';
import { VenuemapComponent } from '../reserve-by-seat/venue-map/venue-map.component';
//service
import { PerformancesService } from '../shared/services/performances.service';
import { StockTypesService } from '../shared/services/stock-types.service';
import { SeatStatusService } from '../shared/services/seat-status.service';
import { QuentityCheckService } from '../shared/services/quentity-check.service';
import { StockTypeDataService } from '../shared/services/stock-type-data.service';
import { ErrorModalDataService } from '../shared/services/error-modal-data.service';
import { FilterComponent } from '../reserve-by-seat/filter/filter.component';
import { SeatsService } from '../shared/services/seats.service';
import { CountSelectService } from '../shared/services/count-select.service';
import { AnimationEnableService } from '../shared/services/animation-enable.service';
import { SmartPhoneCheckService } from '../shared/services/smartPhone-check.service';
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
import { ApiConst } from '../app.constants';
//logger
import { Logger } from "angular2-logger/core";

@Component({
  selector: 'app-reserve-by-quantity',
  templateUrl: './reserve-by-quantity.component.html',
  styleUrls: ['./reserve-by-quantity.component.css']
})
@NgModule({
  imports: [
  ],
  declarations: [
    Component
  ],
  bootstrap: [Component]
})
export class ReserveByQuantityComponent implements OnInit {
  //Subscription
  private subscription: Subscription;
  //席種Id
  private selectStockTypeId: number;
  // 座席選択数
  private countSelectVenuemap: number = 0;

  //表示・非表示(venuemap,reserve-by-quentityで双方向データバインド)
  //(seat-listから呼び出されてtrue,false)
  @Input() private filterComponent: FilterComponent;
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
  selectedSalesUnitQuantitys: number[] = [];

  //枚数選択POST初期データ
  data: {} = {
    "reserve_type": "auto",
    "auto_select_conditions": {
      "stock_type_id": 0,
      "quantity": 0
    }
  }

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
  performanceOrderLimit: number;
  eventOrderLimit: number;
  defaultMaxQuantity: number = 10;
  //最小購入数
  minQuantity: number;

  //説明
  description: string;

  //ボタン表示・非表示
  nextButtonFlag: boolean = false;

  //座席確保飛び席モーダルフラグ
  separatDetailDisplay: boolean = false;

  constructor(private route: ActivatedRoute, private router: Router,
    private performances: PerformancesService, private stockTypes: StockTypesService,
    private seatStatus: SeatStatusService, private seats: SeatsService,
    private QuentityChecks: QuentityCheckService,
    private stockTypeDataService: StockTypeDataService,
    private errorModalDataService: ErrorModalDataService,
    private countSelectService: CountSelectService,
    private animationEnableService: AnimationEnableService,
    private smartPhoneCheckService: SmartPhoneCheckService,
    private _logger: Logger
  ) {
  }

  ngOnInit() {
    this.nextButtonFlag = false;
    this.stockTypeDataService.toQuentityData$.subscribe(
      stockTypeId => {
        this.selectStockTypeId = stockTypeId;
        this.loadPerformance();
      });
    this.countSelectService.toQuentityData$.subscribe(
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
            this.performanceOrderLimit = this.performance.order_limit;
            this.eventOrderLimit = response.data.event.order_limit;
            this.selesSegments = this.performance.sales_segments;
            this.selesSegmentId = this.selesSegments[0].sales_segment_id;

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
                  });
                  this.stockType = response.data.stock_types[0];
                  //席種名と商品情報取得
                  this.stockTypeName = this.stockType.stock_type_name;
                  this.selectedProducts = this.stockType.products;
                  this.selectedSalesUnitQuantitys = this.QuentityChecks.eraseOne(this.stockType.products);
                  this.description = this.stockType.description ? this.stockType.description : '';
                  this.minQuantity = this.stockType.min_quantity;
                  this.maxQuantity = this.stockType.max_quantity;
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
                      getMap = document.getElementById("venue-quentity");
                      if (getMap && getMap.firstElementChild) {
                        //二重色付け制限
                        if ($('#venue-quentity').find('.region').css({ 'fill': 'red' })) {
                          $('#venue-quentity').find('.region').css({
                            'fill': 'white'
                          });
                        }
                        //色付け
                        for (let i = 0; i < that.regions.length; i++) {
                          $('#venue-quentity').find('#' + that.regions[i]).css({
                            'fill': 'red'
                          });
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
                });
            } else {
              this.display = false;
              this.scrollAddCss();
              this._logger.error("パラメータに異常が発生しました。");
            }
          },
          (error) => {
            this.display = false;
            this.scrollAddCss();
            this._logger.error('performances error:' + error);
          });
      }
      else {
        this.display = false;
        this.scrollAddCss();
        this._logger.error('エラー', '公演IDを取得できません。');
        this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
      }

    });
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

  //閉じるボタン
  closeClick() {
    this.display = false;
    this.output.emit(false);
    this.nextButtonFlag = false;
    this.quantity = 1;
  }

  //チケット枚数減少
  minusClick() {
    if (this.QuentityChecks.minLimitCheck(this.minQuantity, this.quantity - 1)) {
      this.quantity--;
      $('#plus-btn').removeClass('disabled');
      if (!this.QuentityChecks.minLimitCheck(this.minQuantity, this.quantity - 1)) {
        $('#minus-btn').addClass('disabled');
      }
    } else {
      $('#minus-btn').addClass('disabled');
    }
  }

  //チケット枚数増加
  plusClick() {
    if (this.QuentityChecks.maxLimitCheck(this.maxQuantity, this.performanceOrderLimit, this.eventOrderLimit, this.quantity + 1)) {
      this.quantity++;
      $("#minus-btn").removeClass('disabled');
      if (!this.QuentityChecks.maxLimitCheck(this.maxQuantity, this.performanceOrderLimit, this.eventOrderLimit, this.quantity + 1)) {
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
      if (!this.QuentityChecks.salesUnitCheck(this.selectedProducts, this.quantity)) {
        this.dataUpdate();
        this.route.params.subscribe((params) => {
          if (params && params['performance_id']) {
            //パラメーター切り出し
            this.performanceId = +params['performance_id'];
            //座席確保api
            this.seatStatus.seatReserve(this.performanceId, this.selesSegmentId, this.data).subscribe((response: ISeatsReserveResponse) => {
              this._logger.debug(`get seatReserve(#${this.performanceId}) success`, response);
              this.resSeatIds = response.data.results.seats
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
                    this.router.navigate(["performances/" + this.performanceId + '/select-product/']);
                  }
                }
                //OKの場合、商品選択へ画面遷移
                this.animationEnableService.sendToRoadFlag(false);
                this.router.navigate(["performances/" + this.performanceId + '/select-product/']);
              } else {
                this.animationEnableService.sendToRoadFlag(false);
                $('#reservebutton').prop("disabled", false);
                this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');
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
        this.errorModalDataService.sendToErrorModal('エラー', this.QuentityChecks.salesUnitCheck(this.selectedProducts, this.quantity) + '席単位でご選択ください。');
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
    this.filterComponent.search();
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
    this.router.navigate(['performances/' + this.performanceId + '/select-product/']);
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
}