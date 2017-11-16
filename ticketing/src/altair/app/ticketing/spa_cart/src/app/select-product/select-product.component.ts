import { Component,NgModule, OnInit } from '@angular/core';
//router
import { ActivatedRoute,Router } from '@angular/router';
//prime
import { DropdownModule,SelectItem } from 'primeng/primeng';
//service
import { SeatStatusService } from '../shared/services/seat-status.service';
import { PerformancesService } from '../shared/services/performances.service';
import { StockTypesService } from '../shared/services/stock-types.service';
import { ErrorModalDataService } from '../shared/services/error-modal-data.service';
import { SelectProductService } from '../shared/services/select-product.service';
import { SmartPhoneCheckService } from '../shared/services/smartPhone-check.service';
import { AnimationEnableService } from '../shared/services/animation-enable.service';
//interface
import {
        ISeatsReserveResponse,ISeatsReleaseResponse,IResult,
        IPerformance, IPerformanceInfoResponse, IStockType,
        IStockTypeResponse, ISelectProductResponse, IProducts, ISeat,
        IProductsRequest, ISelectedProducts
       } from '../shared/services/interfaces';
//jquery
import * as $ from 'jquery';
//observable
import { Observable } from 'rxjs/Rx';
//const
import { ApiConst, AppConstService } from '../app.constants';
//logger
import { Logger } from "angular2-logger/core";

@Component({
  selector: 'app-select-product',
  templateUrl: './select-product.component.html',
  styleUrls: ['./select-product.component.css']
})
@NgModule({
  imports: [
    DropdownModule,
  ],
  declarations: [
    Component
  ],
  bootstrap: [Component]
})
export class SelectProductComponent implements OnInit {
  //ページタイトル（公演名）
  pageTitle: string;
  //公演ID
  performanceId: number;
  //公演情報
  performance: IPerformance;
  //販売区分ID
  salesSegmentId: number;
  //席種ID
  stockTypeId: number;
  //席種情報
  stockType: IStockType;

  //レスポンス
  response: ISeatsReserveResponse;
  releaseResponse: IResult;
  selectProduct: ISelectProductResponse;

  //判定フラグ　席受け:false,数受け:true
  isQuantityOnly: boolean;
  //確保座席結果　席受け,数受け　
  seatResult: IResult;
  //確保座席商品　席受け,数受け
  products: IProducts[] = [];
  //販売単位(HTML表示用)　席受け,数受け
  salesUnitQuantitysV: number[] = [];
  //販売単位(TS処理用)　席受け,数受け
  salesUnitQuantitys: number[] = [];
  //未割当枚数　席受け,数受け
  unAssignedQuantity: number = 0;
  //割当済枚数　席受け,数受け
  assignedQuantity: number = 0;
  //合計金額　席受け,数受け
  fee: number = 0;

  //割当済座席名配列　席受け
  selectedSeatResults: { [key: number]: string[]; } = {};
  //次の座席名
  nextSeat: string = null;
  //割当済座席枚数配列　数受け
  selectedQuantitys: number[] = [];

  //モーダル
  modalVisible: boolean = false;
  modalMessage: string = '';
  modalTitle: string = '選択エラー';

  //時間表示
  timer: any;
  timeoutFlag: boolean = false;
  startOnTime: any;
  year: any;
  month: any;
  day: any;

  constructor(private seatStatus: SeatStatusService,
    private route: ActivatedRoute,
    private router: Router,
    private performances: PerformancesService,
    private stockTypes: StockTypesService,
    private selectProducts: SelectProductService,
    private errorModalDataService: ErrorModalDataService,
    private smartPhoneCheckService: SmartPhoneCheckService,
    private animationEnableService: AnimationEnableService,
    private _logger: Logger) {
    this.response = this.seatStatus.seatReserveResponse;
  }

  ngOnInit() {
    const that = this;
    this.timer = Observable.timer(900000);
    this.timer = this.timer.subscribe(function () {
      that.cancel();
      that.timeout();
    });
    if (!this.response) {
      this.route.params.subscribe((params) => {
        if (params && params['performance_id']) {
          this.performanceId = +params['performance_id'];
          this.router.navigate(["performances/" + this.performanceId]);
        } else {
          this._logger.error("エラー:公演IDを取得できません");
          this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
        }
      });
    } else {
      this.seatResult = this.response.data.results;
      this.stockTypeId = this.response.data.results.stock_type_id;
      this.isQuantityOnly = this.response.data.results.is_quantity_only;
      this.loadPerformance();
    }
  }

  ngOnDestroy() {
    this.timer.unsubscribe();
  }

  private timeout() {
    this.timeoutFlag = true;
    this.modalVisible = true;
    this.modalTitle = 'タイムアウトエラー';
    this.modalMessage = '座席確保から15分経過しました。もう一度最初からやり直してください。';
  }

  private loadPerformance() {
    this.route.params.subscribe((params) => {
      if (params && params['performance_id']) {
        //パラメーター切り出し
        this.performanceId = +params['performance_id'];
        //公演情報取得
        this.performances.getPerformance(this.performanceId)
          .subscribe((response: IPerformanceInfoResponse) => {
            this._logger.debug(`get performance(#${this.performanceId}) success`, response);
            this.performance = response.data.performance;
            let startOn = new Date(this.performance.start_on + '+09:00');
            this.startOnTime = startOn.getHours() + '時';
            if (startOn.getMinutes() != 0) {
              this.startOnTime += startOn.getMinutes() + '分';
            }
            this.year = startOn.getFullYear();
            this.month = startOn.getMonth() + 1;
            this.day = startOn.getDate();
            this.salesSegmentId = response.data.sales_segments[0].sales_segment_id;
            this.pageTitle = this.performance.performance_name;
            this.loadStockType();
          },
          (error) => {
            this._logger.error('performances error', error);
          });
      }
      else {
        this._logger.error("エラー:公演IDを取得できません");
        this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
      }
    });
  }

  private loadStockType() {
    if (this.performanceId && this.salesSegmentId && this.stockTypeId) {
      this.stockTypes.getStockType(this.performanceId, this.salesSegmentId, this.stockTypeId)
        .subscribe((response: IStockTypeResponse) => {
          this._logger.debug(`get stockType(#${this.performanceId}) success`, response);
          this.stockType = response.data.stock_types[0];
          this.initialSetting();
        },
        (error) => {
          this._logger.error('stockType error', error);
        });
    } else {
      this._logger.error("パラメータに異常が発生しました。");
      this.errorModalDataService.sendToErrorModal('席種情報を取得できません。', 'インターネットに未接続または通信が不安定な可能性があります。通信環境の良いところでページを再読込してください。');
    }
  }

  //初期設定
  private initialSetting() {
    let that = this;
    //商品一覧,販売単位取得
    this.stockType.products.forEach((value, key) => {
      let sumQuantity: number = 0;
      this.products.push(value);
      for (let i = 0, len = this.products[key].product_items.length; i < len; i++) {
        sumQuantity += this.products[key].product_items[i].sales_unit_quantity;
      }
      this.salesUnitQuantitys.push(sumQuantity);
    });
    //販売単位表示用配列（1 == null）
    for (let i = 0, len = this.salesUnitQuantitys.length; i < len; i++) {
      if (this.salesUnitQuantitys[i] == 1) {
        this.salesUnitQuantitysV[i] = null;
      } else {
        this.salesUnitQuantitysV[i] = this.salesUnitQuantitys[i];
      }
    }

    if (this.isQuantityOnly) {//数受け
      let productCount: number = this.products.length;
      if (productCount == 1) {//商品数 == 1 なら割当
        this.unAssignedQuantity = this.seatResult.quantity;
        if (this.salesUnitQuantitys[0] == 1) {//初期割当（初期販売単位が1の時）
          this.selectedQuantitys[0] = this.unAssignedQuantity;
          this.unAssignedQuantity = 0;
        } else {//（初期販売単位が2以上の時）
          let divisionResult: number = Math.floor(this.unAssignedQuantity / this.salesUnitQuantitys[0]);
          let setFirstProduct: number = divisionResult * this.salesUnitQuantitys[0];
          this.selectedQuantitys[0] = setFirstProduct;
          this.unAssignedQuantity -= setFirstProduct;
        }
      } else {
        this.unAssignedQuantity = this.seatResult.quantity;
      }
    } else {//席受け
      let productCount: number = this.products.length;
      if (productCount == 1) {//商品数 ==1 なら割当
        if (this.salesUnitQuantitys[0] == 1) {//初期割当（初期販売単位が1の時）
          for (let i = 0, len = this.seatResult.seat_name.length; i < len; i++) {
            if (this.selectedSeatResults[i] == null) {
              this.selectedSeatResults[i] = [];
            }
            this.selectedSeatResults[0].push(this.seatResult.seat_name[0]);
            this.seatResult.seat_name.shift();
          }
        } else {//（初期販売単位が2以上の時）
          let divisionResult: number = Math.floor(this.seatResult.seat_name.length / this.salesUnitQuantitys[0]);
          let setFirstProduct: number = divisionResult * this.salesUnitQuantitys[0];
          for (let i = 0, len = setFirstProduct; i < len; i++) {
            if (this.selectedSeatResults[i] == null) {
              this.selectedSeatResults[i] = [];
            }
            this.selectedSeatResults[0].push(this.seatResult.seat_name[0]);
            this.seatResult.seat_name.shift();
          }
        }
      }
    }
    setTimeout(function() {
      that.recalculation();
    }, 0);
  }
  //-押下
  private minusClick(key) {
    if (this.isQuantityOnly) {//数受け割当解除
      for (let i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
        this.selectedQuantitys[key] -= 1;
        this.unAssignedQuantity++;
      }
    } else {//席受け割当解除
      if (this.selectedSeatResults[key] == null) {
        this.selectedSeatResults[key] = [];
      }
      if (this.salesUnitQuantitys[key] == 1) {
        for (let i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
          let rmSeatName: string = this.selectedSeatResults[key][this.selectedSeatResults[key].length - 1];
          this.selectedSeatResults[key].pop();
          this.seatResult.seat_name.push(rmSeatName);
        }
      } else {
        let rmSeatNames: string[] = [];
        for (let i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
          let rmSeatName: string = this.selectedSeatResults[key][this.selectedSeatResults[key].length - 1];
          rmSeatNames.push(this.selectedSeatResults[key][this.selectedSeatResults[key].length - 1]);
          this.selectedSeatResults[key].pop();
        }
        rmSeatNames.reverse();
        Array.prototype.push.apply(this.seatResult.seat_name, rmSeatNames);
      }
    }
    this.recalculation();
  }

  //+押下
  private plusClick(key) {
    if (this.isQuantityOnly) {//数受け割当
      if (!this.selectedQuantitys[key]) {
        this.selectedQuantitys[key] = 0;
      }
      for (let i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
        this.selectedQuantitys[key] += 1;
        this.unAssignedQuantity--;
      }
    } else {//席受け割当
      if (this.selectedSeatResults[key] == null) {
        this.selectedSeatResults[key] = [];
      }
      for (let i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
        this.selectedSeatResults[key].push(this.seatResult.seat_name[0]);
        this.seatResult.seat_name.shift();
      }
    }
    this.recalculation();
  }
  //残席数・合計金額・選択済み座席数・±ボタン有効無効
  private recalculation() {
    const disabledNumber: number = 1;
    this.assignedQuantity = 0;
    this.fee = 0;

    if (this.isQuantityOnly) {//数受け
      //+ボタン有効無効
      for (let x in this.products) {
        if (this.unAssignedQuantity < this.salesUnitQuantitys[x]) {
          addClass(x, "plus");
        } else {
          removeClass(x, "plus");
        }
      }
      //-ボタン有効無効
      for (let x in this.products) {
        if (this.selectedQuantitys[x] > 0) {
          if (disabledNumber > this.selectedQuantitys[x]) {
            addClass(x, "minus");
          } else {
            removeClass(x, "minus");
          }
        } else {
          addClass(x, "minus");
        }
      }
      //合計金額再計算
      for (let x in this.selectedQuantitys) {
        this.assignedQuantity += this.selectedQuantitys[x];
        if (this.products[x]) {
          if ((this.salesUnitQuantitys[x]) > 1) {
            this.fee = (this.products[x].price / this.salesUnitQuantitys[x]) * this.selectedQuantitys[x] + this.fee;
          } else {
            this.fee = this.products[x].price * this.selectedQuantitys[x] + this.fee;
          }
        }
      }
    } else {//席受け
      //未割当席数再取得
      this.unAssignedQuantity = this.seatResult.seat_name.length;
      this.nextSeat = this.seatResult.seat_name[0];
      //+ボタン有効無効
      for (let x in this.products) {
        if (this.unAssignedQuantity < this.salesUnitQuantitys[x]) {
          addClass(x, "plus");
        } else {
          removeClass(x, "plus");
        }
      }
      //-ボタン有効無効
      for (let x in this.products) {
        if (this.selectedSeatResults[x]) {
          if (disabledNumber > this.selectedSeatResults[x].length) {
            addClass(x, "minus");
          } else {
            removeClass(x, "minus");
          }
        } else {
          addClass(x, "minus");
        }
      }
      //合計金額再計算
      for (let x in this.selectedSeatResults) {
        this.assignedQuantity += this.selectedSeatResults[x].length;
        if (this.products[x]) {
          if ((this.salesUnitQuantitys[x]) != 1) {
            this.fee = (this.products[x].price / this.salesUnitQuantitys[x]) * this.selectedSeatResults[x].length + this.fee;
          } else {
            this.fee = this.products[x].price * this.selectedSeatResults[x].length + this.fee;
          }
        }
      }
    }
    this.fee = this.separate(this.fee);
    /**
    * +ボタン有効無効
    * @param  {string}  x ボタン番号
    * @param  {string}  str プラスorマイナス
    */
    function addClass(x: string, str: string) {
      if (str == "plus") {
          $('#plus-btn' + [x]).prop("disabled", true);
          $('#plus-btn' + [x]).addClass('disabled');
      } else {
          $('#minus-btn' + [x]).prop("disabled", true);
          $('#minus-btn' + [x]).addClass('disabled');
      }
    }
    /**
    * +ボタン有効無効
    * @param  {string}  x ボタン番号
    * @param  {string}  str プラスorマイナス
    */
    function removeClass(x: string, str: string) {
      if (str == "plus") {
          $('#plus-btn' + [x]).prop("disabled", false);
          $('#plus-btn' + [x]).removeClass('disabled');

      } else {
          $('#minus-btn' + [x]).prop("disabled", false);
          $('#minus-btn' + [x]).removeClass('disabled');
      }
    }
  }

  //キャンセルボタン押下（座席開放API）
  private cancel() {
    this.seatStatus.seatRelease(this.performanceId)
      .subscribe((response: ISeatsReleaseResponse) => {
        this._logger.debug(`seat release(#${this.performanceId}) success`, response);
        this.releaseResponse = response.data.results;
        if (this.releaseResponse.status == "NG") {
          this._logger.error('seat release error', this.releaseResponse);
          this.errorModalDataService.sendToErrorModal('エラー', '座席を解放できません。');
        } else {
          this.router.navigate(["performances/" + this.performanceId]);
        }
      },
      (error) => {
        this._logger.error('seat release error', error);
      });
  }

  //購入ボタン押下（商品選択API）
  private purchase() {
    this.animationEnableService.sendToRoadFlag(true);
    $('#submit').prop("disabled", true);
    let data: any;
    data = {
      "is_quantity_only": this.isQuantityOnly,
      "selected_products": []
    }
    if (data.is_quantity_only) {//数受け商品選択APIリクエストData作成
      const RequestQuantity: number = 1;
      this.selectedQuantitys.forEach((value, key) => {
        if (value >= 1) {//商品が選択されている時のみ
          let productItemsCount: number = this.products[key].product_items.length;
          let setProductItemId: number = this.products[key].product_items[0].product_item_id;
          if (productItemsCount == 1) {//商品明細が1つの商品をセット
            data.selected_products.push({
              "seat_id": null,
              "product_item_id": setProductItemId,
              "quantity": value
            });
          } else {//商品明細が2つ以上の商品をセット
            let productItemIds: number[] = [];
            let processingCount: number[] = [];
            //商品明細idを取得する処理数を取得
            for (let x in this.selectedQuantitys) {
              if (this.selectedQuantitys[x]) {
                if (this.isInteger(this.selectedQuantitys[x] / 2) && this.salesUnitQuantitys[x] != 1) {
                  processingCount.push(this.selectedQuantitys[x] / 2);
                } else {
                  processingCount.push(this.selectedQuantitys[x]);
                }
              } else {
                processingCount.push(null);
              }
            }
            //商品明細idを選択されている上から取得
            for (let x in this.selectedQuantitys) {
              if (processingCount[x]) {
                for (let i = 0, len = processingCount[x]; i < len; i++) {
                  if (this.products[x].product_items.length != 1) {
                    for (let j = 0, len = this.products[x].product_items.length; j < len; j++) {
                      productItemIds.push(this.products[x].product_items[j].product_item_id);
                    }
                  }
                }
              }
            }
            //重複削除
            productItemIds = productItemIds.filter(function (x, i, self) {
              return self.indexOf(x) === i;
            });
            //商品明細idセット
            for (let i = 0, len = productItemIds.length; i < len; i++) {
              data.selected_products.push({
                "seat_id": null,
                "product_item_id": productItemIds[i],
                "quantity": value / productItemsCount
              });
            }
          }
        }
      });
      this.unassignedSeatCheck(this.unAssignedQuantity);
    } else {//席受け商品選択APIリクエストData作成
      const RequestQuantity: number = 1;
      let itemIndex: number = 0;
      let salesUnit: number = 1;
      let seatMap = new Map<string, string>();
      let setProductItemIds: number[] = [];
      let setSeatIds: string[] = [];

      for (let x in this.seatResult.seats) {
        seatMap.set(this.seatResult.seats[x].seat_name, this.seatResult.seats[x].seat_id);
      }

      for (let x in this.selectedSeatResults) {
        for (let y in this.selectedSeatResults[x]) {
          //商品明細id,seatIdを設定
          setProductItemIds.push(this.products[x].product_items[itemIndex].product_item_id);
          setSeatIds.push(seatMap.get(this.selectedSeatResults[x][y]));
          if (this.products[x].product_items[itemIndex].sales_unit_quantity == salesUnit) {//明細の販売単位と販売単位変数が同じ場合
            if (this.products[x].product_items.length - 1 == itemIndex) {//商品明細数 - 1　とitemIndexが同じ値の場合
              itemIndex = 0;
            } else {
              itemIndex++;
            }
            salesUnit = 1;
          } else {
            salesUnit++;
          }
        }
      }
      //商品明細id,seatIdセット
      this.seatResult.seats.forEach((value, key) => {
        data.selected_products.push({
          "seat_id": setSeatIds[key],
          "product_item_id": setProductItemIds[key],
          "quantity": RequestQuantity
        });
      });
      this.unassignedSeatCheck(this.seatResult.seat_name.length);
    }
    //商品選択API
    if (!this.modalVisible) {
      this.selectProducts.selectProduct(this.performanceId, data)
        .subscribe((response: ISelectProductResponse) => {
          this._logger.debug(`select product(#${this.performanceId}) success`, response);
          this.selectProduct = response;
          if (this.selectProduct.data.results.status == "OK") {
            //現行カートの支払いへ遷移
            this.animationEnableService.sendToRoadFlag(false);
            location.href = '/cart/payment/sales/' + this.salesSegmentId;
          } else {
            this.animationEnableService.sendToRoadFlag(false);
            $('#submit').prop("disabled", false);
            this._logger.debug('select product error', this.selectProduct.data.results.reason);
            this.errorModalDataService.sendToErrorModal('エラー', '商品を選択できません。');
          }
        },
        (error) => {
          this.animationEnableService.sendToRoadFlag(false);
          $('#submit').prop("disabled", false);
          this._logger.error('select product error', error);
        });
    }
  }
  //トップへ遷移
  private onClick() {
    location.href = `${AppConstService.PAGE_URL.TOP}`;
  }
  /**
 * 合計枚数チェック
 * @param  {number}  num 未割当枚数
 */
  unassignedSeatCheck(num: number) {
    if (num > 0) {
      this.modalVisible = true;
      this.modalMessage = '<p>未割当の座席があります。</p>';
      this.animationEnableService.sendToRoadFlag(false);
      $('#submit').prop("disabled", false);
    }
  }
  /**
  * 整数か返す
  * @param  {number}  x 判定対象
  * @return {boolean}
  */
  isInteger(x: number) {
    return Math.round(x) === x;
  }
  /**
  * 3桁区切りにし返す
  * @param  {any}  num 桁区切り対象
  * @return {any}
  */
  separate(num) {
    num = String(num);
    let len = num.length;
    if (len > 3) {
      return this.separate(num.substring(0, len - 3)) + ',' + num.substring(len - 3);
    } else {
      return num;
    }
  }

  ngAfterViewInit() {
    const that = this;
    function bodyContentsHeight() {
      var h = Math.max.apply(null, [document.body.clientHeight, document.body.scrollHeight, document.documentElement.scrollHeight, document.documentElement.clientHeight]);
      return h;
    }

    $(function () {
      var windowWidth = $(window).width();
      var windowSm = 768;
      if (windowWidth <= windowSm) {
        //横幅768px以下のとき（つまりスマホ時）に行う処理を書く
        $(function () {
          var windowH;
          var mainH;
          var minus = 112
          var mainID = 'buySeatArea'
          function heightSetting() {
            windowH = $(window).height();
            mainH = windowH - minus;
            if (that.isQuantityOnly) {
              $('#' + mainID).height(bodyContentsHeight());
            }
          }
          heightSetting();
          $(window).resize(function () {
            heightSetting();
          });
        });
      } else {
        //横幅768px超のとき（タブレット、PC）に行う処理を書く
        $(function () {
          var windowH;
          var mainH;
          var minus = 169
          var mainID = 'buySeatArea'
          function heightSetting() {
            windowH = $(window).height();
            mainH = windowH - minus;
            $('#' + mainID).height(mainH + 'px');
          }
          heightSetting();
          $(window).resize(function () {
            heightSetting();
          });
        });
      }
    });
  }
}