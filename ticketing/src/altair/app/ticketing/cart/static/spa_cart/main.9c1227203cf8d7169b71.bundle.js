webpackJsonp(["main"],{

/***/ "../../../../../src/$$_gendir lazy recursive":
/***/ (function(module, exports) {

function webpackEmptyAsyncContext(req) {
	return new Promise(function(resolve, reject) { reject(new Error("Cannot find module '" + req + "'.")); });
}
webpackEmptyAsyncContext.keys = function() { return []; };
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
module.exports = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = "../../../../../src/$$_gendir lazy recursive";

/***/ }),

/***/ "../../../../../src/app/app.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/app.component.html":
/***/ (function(module, exports) {

module.exports = "<!--共通エラーモーダル-->\n<app-api-common-error></app-api-common-error>\n<!--共通読み込み中アニメーション-->\n<app-road-animation></app-road-animation>\n<!--共通初期表示アニメーション-->\n<loading-animate></loading-animate>\n<!--ルーティング-->\n<div id=\"p2rfix\">\n    <router-outlet></router-outlet>\n</div>"

/***/ }),

/***/ "../../../../../src/app/app.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return AppComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__ = __webpack_require__("../../../../ng2-loading-animate/ng2-loading-animate.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_jquery__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};




var AppComponent = (function () {
    /**
     * constructor
     * @param {Router}                private router Router
     * @param {LoadingAnimateService} private loadingService loading animation service
     */
    function AppComponent(router, loadingService) {
        var _this = this;
        this.router = router;
        this.loadingService = loadingService;
        // ブラウザのUAを小文字で取得
        this.userAgent = window.navigator.userAgent.toLowerCase();
        // 一般的なブラウザ判定
        router.events.subscribe(function (event) {
            _this.navigationInterceptor(event);
        });
    }
    AppComponent.prototype.ngOnInit = function () {
        //nothing to do
        if (this.userAgent.indexOf('chrome') != -1) {
            var bodyStyle;
            document.getElementsByTagName('html')[0].style.height = '100%';
            document.getElementsByTagName('html')[0].style.overflowY = 'hidden';
            bodyStyle = document.getElementsByTagName('body')[0].style;
            bodyStyle.height = '100%';
            bodyStyle.overflowY = 'auto';
        }
        else if (((this.userAgent.indexOf('msie') > -1) && (this.userAgent.indexOf('opera') == -1)) || (this.userAgent.indexOf('trident/7') > -1)) {
            //IE
            __WEBPACK_IMPORTED_MODULE_3_jquery__('body').addClass('ie');
        }
    };
    // Shows and hides the loading spinner during RouterEvent changes
    AppComponent.prototype.navigationInterceptor = function (event) {
        if (event instanceof __WEBPACK_IMPORTED_MODULE_1__angular_router__["NavigationStart"]) {
            this.loadingService.setValue(true);
        }
        if (event instanceof __WEBPACK_IMPORTED_MODULE_1__angular_router__["NavigationEnd"]) {
            this.loadingService.setValue(false);
        }
        // Set loading state to false in both of the below events to hide the spinner in case a request fails
        if (event instanceof __WEBPACK_IMPORTED_MODULE_1__angular_router__["NavigationCancel"]) {
            this.loadingService.setValue(false);
        }
        if (event instanceof __WEBPACK_IMPORTED_MODULE_1__angular_router__["NavigationError"]) {
            this.loadingService.setValue(false);
        }
        if (undefined) {
            this.loadingService.setValue(false);
        }
    };
    AppComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-root',
            template: __webpack_require__("../../../../../src/app/app.component.html"),
            styles: [__webpack_require__("../../../../../src/app/app.component.css")]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__["LoadingAnimateService"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__["LoadingAnimateService"]) === 'function' && _b) || Object])
    ], AppComponent);
    return AppComponent;
    var _a, _b;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/app.component.js.map

/***/ }),

/***/ "../../../../../src/app/app.constants.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return ApiConst; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return AppConstService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};

/************************************************************************************
 *
 * 定数クラス
 *
 ***********************************************************************************/
/**
 * @class API関連 定数管理
 */
var ApiConst = (function () {
    function ApiConst() {
    }
    // APIのパス以前のURL（スキーム, ドメイン, ベースパス）になります
    // public static API_BASE_URL = 'http://dev.altair-spa.tk/cart_api/api/v1/';
    ApiConst.API_BASE_URL = '/cart_api/api/v1/';
    // 各APIのURLになります
    ApiConst.API_URL = {
        // 公演情報検索API
        PERFORMANCES: ApiConst.API_BASE_URL + "events/{:event_id}/performances",
        // 公演情報API
        PERFORMANCE_INfO: ApiConst.API_BASE_URL + "performances/{:performance_id}",
        // 席種情報検索API
        STOCK_TYPES: ApiConst.API_BASE_URL + "performances/{:performance_id}/sales_segments/{:sales_segment_id}/stock_types",
        // 席種情報API
        STOCK_TYPE: ApiConst.API_BASE_URL + "performances/{:performance_id}/sales_segments/{:sales_segment_id}/stock_types/{:stock_type_id}",
        // 席種情報API
        STOCK_TYPES_ALL: ApiConst.API_BASE_URL + "performances/{:performance_id}/sales_segments/{:sales_segment_id}/stock_types/all",
        // 座席情報検索API
        SEATS: ApiConst.API_BASE_URL + "performances/{:performance_id}/seats",
        // 座席確保
        SEATS_RESERVE: ApiConst.API_BASE_URL + "performances/{:performance_id}/sales_segments/{:sales_segment_id}/seats/reserve",
        // 座席解放
        SEATS_RELEASE: ApiConst.API_BASE_URL + "performances/{:performance_id}/seats/release",
        // 商品選択
        SELECT_PRODUCT: ApiConst.API_BASE_URL + "performances/{:performance_id}/select_products",
    };
    //通信断時のエラー
    ApiConst.TIMEOUT = 'Timeout has occurred';
    //DNSエラー
    ApiConst.SERVERDNSERROR = 'server dns error';
    //ダウンエラー
    ApiConst.SERVERDOWNERROR = 'server down error';
    return ApiConst;
}());
var AppConstService = (function () {
    function AppConstService() {
    }
    // サイトのパス以前のURL（スキーム, ドメイン, ベースパス）になります
    AppConstService.APP_BASE_URL = 'public/';
    // アセッツルート 画像等のファイル関連設置場所になります
    AppConstService.ASSETS_ROOT = '/public/assets/';
    // 画像の設置場所になります
    AppConstService.IMG_ROOT = AppConstService.ASSETS_ROOT + "img/";
    // 各ページのURLになります
    AppConstService.PAGE_URL = {
        // トップページ
        TOP: "https://eagles.tstar.jp/",
        // 支払ページ
        PAYMENT: AppConstService.APP_BASE_URL + "payment",
        // 枚数選択
        RESERVE_BY_QUANTITY: AppConstService.APP_BASE_URL + "reserve-by-quantity",
        //商品選択
        SELECT_PRODUCT: AppConstService.APP_BASE_URL + "select-product",
    };
    AppConstService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], AppConstService);
    return AppConstService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/app.constants.js.map

/***/ }),

/***/ "../../../../../src/app/app.module.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return AppModule; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_platform_browser__ = __webpack_require__("../../../platform-browser/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__angular_forms__ = __webpack_require__("../../../forms/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__app_component__ = __webpack_require__("../../../../../src/app/app.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__reserve_by_seat_reserve_by_seat_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/reserve-by-seat.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__payment_payment_component__ = __webpack_require__("../../../../../src/app/payment/payment.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__reserve_by_quantity_reserve_by_quantity_component__ = __webpack_require__("../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__select_product_select_product_component__ = __webpack_require__("../../../../../src/app/select-product/select-product.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10__reserve_by_seat_event_info_event_info_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/event-info/event-info.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11__reserve_by_seat_filter_filter_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/filter/filter.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_12__reserve_by_seat_venue_map_venue_map_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13__reserve_by_seat_seat_list_seat_list_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/seat-list/seat-list.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_14__errors_page_not_found_page_not_found_component__ = __webpack_require__("../../../../../src/app/errors/page-not-found/page-not-found.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_15__errors_api_common_error_api_common_error_component__ = __webpack_require__("../../../../../src/app/errors/api-common-error/api-common-error.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_16__shared_components_road_animation_component__ = __webpack_require__("../../../../../src/app/shared/components/road-animation.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_17__shared_services_api_base_service__ = __webpack_require__("../../../../../src/app/shared/services/api-base.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_18__shared_services_performances_service__ = __webpack_require__("../../../../../src/app/shared/services/performances.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_19__shared_services_seat_status_service__ = __webpack_require__("../../../../../src/app/shared/services/seat-status.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_20__shared_services_stock_types_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_21__shared_services_seats_service__ = __webpack_require__("../../../../../src/app/shared/services/seats.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_22__shared_services_select_product_service__ = __webpack_require__("../../../../../src/app/shared/services/select-product.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_23__shared_services_quentity_check_service__ = __webpack_require__("../../../../../src/app/shared/services/quentity-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_24__shared_services_stock_type_data_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-type-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_25__shared_services_animation_enable_service__ = __webpack_require__("../../../../../src/app/shared/services/animation-enable.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_26__shared_services_error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_27__shared_services_count_select_service__ = __webpack_require__("../../../../../src/app/shared/services/count-select.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_28__shared_services_smartPhone_check_service__ = __webpack_require__("../../../../../src/app/shared/services/smartPhone-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_29__shared_services_performance_resolver_service__ = __webpack_require__("../../../../../src/app/shared/services/performance-resolver.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_30__shared_services_stock_types_resolver_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types-resolver.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_31_ng_inline_svg__ = __webpack_require__("../../../../ng-inline-svg/lib/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_31_ng_inline_svg___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_31_ng_inline_svg__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_32_primeng_primeng__ = __webpack_require__("../../../../primeng/primeng.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_32_primeng_primeng___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_32_primeng_primeng__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_33_ng2_loading_animate__ = __webpack_require__("../../../../ng2-loading-animate/ng2-loading-animate.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_33_ng2_loading_animate___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_33_ng2_loading_animate__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_34_ng2_nouislider__ = __webpack_require__("../../../../ng2-nouislider/src/nouislider.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_34_ng2_nouislider___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_34_ng2_nouislider__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_35_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_35_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_35_angular2_logger_core__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_36__environments_environment__ = __webpack_require__("../../../../../src/environments/environment.ts");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};





































var routes = [
    {
        path: 'performances/:performance_id',
        component: __WEBPACK_IMPORTED_MODULE_6__reserve_by_seat_reserve_by_seat_component__["a" /* ReserveBySeatComponent */],
        resolve: {
            performance: __WEBPACK_IMPORTED_MODULE_29__shared_services_performance_resolver_service__["a" /* PerformanceResolver */],
            stockTypes: __WEBPACK_IMPORTED_MODULE_30__shared_services_stock_types_resolver_service__["a" /* StockTypesResolver */]
        }
    },
    { path: 'performances/:performance_id/reserve-by-quantity/:stock_type_id', component: __WEBPACK_IMPORTED_MODULE_8__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */] },
    { path: 'performances/:performance_id/select-product', component: __WEBPACK_IMPORTED_MODULE_9__select_product_select_product_component__["a" /* SelectProductComponent */] },
    { path: 'payment/', component: __WEBPACK_IMPORTED_MODULE_7__payment_payment_component__["a" /* PaymentComponent */] },
    { path: '**', component: __WEBPACK_IMPORTED_MODULE_14__errors_page_not_found_page_not_found_component__["a" /* PageNotFoundComponent */] }
];
var AppModule = (function () {
    function AppModule(logger) {
        this.logger = logger;
        if (Object(__WEBPACK_IMPORTED_MODULE_1__angular_core__["isDevMode"])()) {
            console.info('To see debug logs enter: \'logger.level = logger.Level.DEBUG;\' in your browser console');
        }
        this.logger.level = __WEBPACK_IMPORTED_MODULE_36__environments_environment__["a" /* environment */].logger.level;
    }
    AppModule = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_1__angular_core__["NgModule"])({
            declarations: [
                __WEBPACK_IMPORTED_MODULE_5__app_component__["a" /* AppComponent */],
                __WEBPACK_IMPORTED_MODULE_10__reserve_by_seat_event_info_event_info_component__["a" /* EventinfoComponent */],
                __WEBPACK_IMPORTED_MODULE_11__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */],
                __WEBPACK_IMPORTED_MODULE_12__reserve_by_seat_venue_map_venue_map_component__["a" /* VenuemapComponent */],
                __WEBPACK_IMPORTED_MODULE_13__reserve_by_seat_seat_list_seat_list_component__["a" /* SeatlistComponent */],
                __WEBPACK_IMPORTED_MODULE_6__reserve_by_seat_reserve_by_seat_component__["a" /* ReserveBySeatComponent */],
                __WEBPACK_IMPORTED_MODULE_7__payment_payment_component__["a" /* PaymentComponent */],
                __WEBPACK_IMPORTED_MODULE_8__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */],
                __WEBPACK_IMPORTED_MODULE_9__select_product_select_product_component__["a" /* SelectProductComponent */],
                __WEBPACK_IMPORTED_MODULE_14__errors_page_not_found_page_not_found_component__["a" /* PageNotFoundComponent */],
                __WEBPACK_IMPORTED_MODULE_15__errors_api_common_error_api_common_error_component__["a" /* ApiCommonErrorComponent */],
                __WEBPACK_IMPORTED_MODULE_16__shared_components_road_animation_component__["a" /* RoadAnimationComponent */]
            ],
            imports: [
                __WEBPACK_IMPORTED_MODULE_0__angular_platform_browser__["BrowserModule"],
                __WEBPACK_IMPORTED_MODULE_2__angular_forms__["FormsModule"],
                __WEBPACK_IMPORTED_MODULE_3__angular_http__["HttpModule"],
                __WEBPACK_IMPORTED_MODULE_3__angular_http__["JsonpModule"],
                __WEBPACK_IMPORTED_MODULE_31_ng_inline_svg__["InlineSVGModule"],
                __WEBPACK_IMPORTED_MODULE_0__angular_platform_browser__["BrowserModule"], __WEBPACK_IMPORTED_MODULE_2__angular_forms__["FormsModule"], __WEBPACK_IMPORTED_MODULE_3__angular_http__["HttpModule"], __WEBPACK_IMPORTED_MODULE_32_primeng_primeng__["InputTextModule"], __WEBPACK_IMPORTED_MODULE_32_primeng_primeng__["ButtonModule"], __WEBPACK_IMPORTED_MODULE_32_primeng_primeng__["DialogModule"], __WEBPACK_IMPORTED_MODULE_32_primeng_primeng__["DropdownModule"],
                __WEBPACK_IMPORTED_MODULE_33_ng2_loading_animate__["LoadingAnimateModule"].forRoot(),
                __WEBPACK_IMPORTED_MODULE_4__angular_router__["RouterModule"].forRoot(routes),
                __WEBPACK_IMPORTED_MODULE_34_ng2_nouislider__["NouisliderModule"]
            ],
            providers: [
                __WEBPACK_IMPORTED_MODULE_35_angular2_logger_core__["Logger"],
                __WEBPACK_IMPORTED_MODULE_33_ng2_loading_animate__["LoadingAnimateService"],
                __WEBPACK_IMPORTED_MODULE_17__shared_services_api_base_service__["a" /* ApiBase */],
                __WEBPACK_IMPORTED_MODULE_19__shared_services_seat_status_service__["a" /* SeatStatusService */],
                __WEBPACK_IMPORTED_MODULE_20__shared_services_stock_types_service__["a" /* StockTypesService */],
                __WEBPACK_IMPORTED_MODULE_18__shared_services_performances_service__["a" /* PerformancesService */],
                __WEBPACK_IMPORTED_MODULE_21__shared_services_seats_service__["a" /* SeatsService */],
                __WEBPACK_IMPORTED_MODULE_29__shared_services_performance_resolver_service__["a" /* PerformanceResolver */],
                __WEBPACK_IMPORTED_MODULE_30__shared_services_stock_types_resolver_service__["a" /* StockTypesResolver */],
                __WEBPACK_IMPORTED_MODULE_22__shared_services_select_product_service__["a" /* SelectProductService */],
                __WEBPACK_IMPORTED_MODULE_23__shared_services_quentity_check_service__["a" /* QuentityCheckService */],
                __WEBPACK_IMPORTED_MODULE_24__shared_services_stock_type_data_service__["a" /* StockTypeDataService */],
                __WEBPACK_IMPORTED_MODULE_26__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */],
                __WEBPACK_IMPORTED_MODULE_25__shared_services_animation_enable_service__["a" /* AnimationEnableService */],
                __WEBPACK_IMPORTED_MODULE_27__shared_services_count_select_service__["a" /* CountSelectService */],
                __WEBPACK_IMPORTED_MODULE_28__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */]
            ],
            bootstrap: [
                __WEBPACK_IMPORTED_MODULE_5__app_component__["a" /* AppComponent */]
            ]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_35_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_35_angular2_logger_core__["Logger"]) === 'function' && _a) || Object])
    ], AppModule);
    return AppModule;
    var _a;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/app.module.js.map

/***/ }),

/***/ "../../../../../src/app/errors/api-common-error/api-common-error.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/errors/api-common-error/api-common-error.component.html":
/***/ (function(module, exports) {

module.exports = "<div *ngIf=\"errorDisplay\" id=\"modalWindowAlertBox\" class=\"modalWindowAlertBox foremost\">\n\t<div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\n\t\t<div id=\"modalWindowAlert\" class=\"modalWindowAlert\">\n\t\t\t<div class=\"modalInner\">\n\t\t\t\t<div class=\"modalAlert\">\n\t\t\t\t\t<p class=\"modalAlertTtl\"><span></span>{{errorTitle}}</p>\n\t\t\t\t\t<p>{{errorDetail}}</p>\n\t\t\t\t\t<button class=\"\" type=\"button\" (click)=\"errorDisplay=false\">OK</button>\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n</div>"

/***/ }),

/***/ "../../../../../src/app/errors/api-common-error/api-common-error.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return ApiCommonErrorComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__shared_services_error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var ApiCommonErrorComponent = (function () {
    function ApiCommonErrorComponent(errorModalDataService) {
        this.errorModalDataService = errorModalDataService;
    }
    ApiCommonErrorComponent.prototype.ngOnInit = function () {
        var _this = this;
        this.errorModalDataService.errorTitle$.subscribe(function (errorTitle) {
            _this.errorTitle = errorTitle;
            _this.errorDisplay = true;
        });
        this.errorModalDataService.errorDetail$.subscribe(function (errorDetail) {
            _this.errorDetail = errorDetail;
            _this.errorDisplay = true;
        });
    };
    ApiCommonErrorComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-api-common-error',
            template: __webpack_require__("../../../../../src/app/errors/api-common-error/api-common-error.component.html"),
            styles: [__webpack_require__("../../../../../src/app/errors/api-common-error/api-common-error.component.css")]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _a) || Object])
    ], ApiCommonErrorComponent);
    return ApiCommonErrorComponent;
    var _a;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/api-common-error.component.js.map

/***/ }),

/***/ "../../../../../src/app/errors/page-not-found/page-not-found.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/errors/page-not-found/page-not-found.component.html":
/***/ (function(module, exports) {

module.exports = "<h1>\n    Not Found\n</h1>\n<p>\n  The requested URL was not found on this server.\n</p>\n"

/***/ }),

/***/ "../../../../../src/app/errors/page-not-found/page-not-found.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return PageNotFoundComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};

var PageNotFoundComponent = (function () {
    function PageNotFoundComponent() {
    }
    PageNotFoundComponent.prototype.ngOnInit = function () {
    };
    PageNotFoundComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-page-not-found',
            template: __webpack_require__("../../../../../src/app/errors/page-not-found/page-not-found.component.html"),
            styles: [__webpack_require__("../../../../../src/app/errors/page-not-found/page-not-found.component.css")]
        }), 
        __metadata('design:paramtypes', [])
    ], PageNotFoundComponent);
    return PageNotFoundComponent;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/page-not-found.component.js.map

/***/ }),

/***/ "../../../../../src/app/payment/payment.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/payment/payment.component.html":
/***/ (function(module, exports) {

module.exports = "<p>\n  payment works!\n</p>\n"

/***/ }),

/***/ "../../../../../src/app/payment/payment.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return PaymentComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};

var PaymentComponent = (function () {
    function PaymentComponent() {
    }
    PaymentComponent.prototype.ngOnInit = function () {
    };
    PaymentComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-payment',
            template: __webpack_require__("../../../../../src/app/payment/payment.component.html"),
            styles: [__webpack_require__("../../../../../src/app/payment/payment.component.css")]
        }), 
        __metadata('design:paramtypes', [])
    ], PaymentComponent);
    return PaymentComponent;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/payment.component.js.map

/***/ }),

/***/ "../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.html":
/***/ (function(module, exports) {

module.exports = "<div id=\"modalWindowAlertBox\" class=\"modalWindowAlertBox\" *ngIf=\"display\">\n    <div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\n        <div id=\"modalWindow\" class=\"modalWindow\">\n            <div class=\"modalInner\">\n                <div class=\"closeBtnBox\"><span class=\"closeBtn\" (click)=\"closeClick()\"></span></div>\n                <div class=\"modalMap venueimg\" aria-label=\"vanueimg\" id=\"venue-quentity\" [inlineSVG]=\"mapURL\"></div>\n                <div class=\"modalImg\"><div [innerHTML]=\"description\"></div></div>\n                <p class=\"seatName2\">{{stockTypeName}}</p>\n                <div class=\"seatPriceBox\">\n                    <tr *ngFor=\"let value of selectedProducts ; let key = index\">\n                        <p class=\"seatPrice\">\n                            <span>{{value.product_name}}</span>\n                            <span>{{value.price}}円</span>\n                            <span *ngIf=\"selectedSalesUnitQuantitys[key]\">({{selectedSalesUnitQuantitys[key]}}枚単位)</span>\n                        </p>\n                    </tr>\n                </div>\n                <div class=\"modalTicketQty cf\">\n                    <div class=\"ticketQty\">\n                        <p class=\"ticketQtyTtl\">枚数</p>\n                        <button id=\"minus-btn\" class=\"iconMinus disabled\" (click)=\"minusClick()\"><span></span></button>\n                        <p id=\"ticketSheet\">{{quantity}}</p>\n                        <button id=\"plus-btn\"  class=\"iconPlus\" (click)=\"plusClick()\"><span></span></button>\n                    </div>\n                </div>\n                <div class=\"modalBtnBox\" *ngIf=\"nextButtonFlag\">\n                    <button id=\"reservebutton\" class=\"\" type=\"button\" (click)=\"seatReserveClick()\">次へ</button>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n<!--飛び席確認モーダル-->\n<div id=\"modalWindowAlertBox\" class=\"modalWindowAlertBox\" *ngIf=\"separatDetailDisplay\">\n    <div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\n        <div id=\"modalWindowAlert\" class=\"modalWindowAlert\">\n            <div class=\"modalInner\">\n                <div class=\"modalAlert\">\n                    <p class=\"modalAlertTtl\"><span></span>連席で座席を確保できません</p>\n                    <p>連席でお席をご用意することが出来ません。</p>\n                    <p>改めて席を選び直す場合は「座席・枚数を選び直す」をお選びください。</p>\n                    <button id=\"selectAgainBtn\" type=\"button\" (click)=\"separatedSelectAgain()\">座席・枚数を選び直す</button>\n                    <button id=\"nextBtn\" type=\"button\" (click)=\"separatedNext()\">次へ</button>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n<!--/飛び席確認モーダル-->\n"

/***/ }),

/***/ "../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return ReserveByQuantityComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__shared_services_performances_service__ = __webpack_require__("../../../../../src/app/shared/services/performances.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__shared_services_stock_types_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__shared_services_seat_status_service__ = __webpack_require__("../../../../../src/app/shared/services/seat-status.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__shared_services_quentity_check_service__ = __webpack_require__("../../../../../src/app/shared/services/quentity-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_type_data_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-type-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__reserve_by_seat_filter_filter_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/filter/filter.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__shared_services_seats_service__ = __webpack_require__("../../../../../src/app/shared/services/seats.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__shared_services_count_select_service__ = __webpack_require__("../../../../../src/app/shared/services/count-select.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10__shared_services_animation_enable_service__ = __webpack_require__("../../../../../src/app/shared/services/animation-enable.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11__shared_services_smartPhone_check_service__ = __webpack_require__("../../../../../src/app/shared/services/smartPhone-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_12__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_13_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_14__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_15_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_15_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_15_angular2_logger_core__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
















var ReserveByQuantityComponent = (function () {
    function ReserveByQuantityComponent(route, router, performances, stockTypes, seatStatus, seats, QuentityChecks, stockTypeDataService, errorModalDataService, countSelectService, animationEnableService, smartPhoneCheckService, _logger) {
        this.route = route;
        this.router = router;
        this.performances = performances;
        this.stockTypes = stockTypes;
        this.seatStatus = seatStatus;
        this.seats = seats;
        this.QuentityChecks = QuentityChecks;
        this.stockTypeDataService = stockTypeDataService;
        this.errorModalDataService = errorModalDataService;
        this.countSelectService = countSelectService;
        this.animationEnableService = animationEnableService;
        this.smartPhoneCheckService = smartPhoneCheckService;
        this._logger = _logger;
        // 座席選択数
        this.countSelectVenuemap = 0;
        this.display = false;
        this.output = new __WEBPACK_IMPORTED_MODULE_0__angular_core__["EventEmitter"]();
        this.confirmStockType = new __WEBPACK_IMPORTED_MODULE_0__angular_core__["EventEmitter"]();
        //チケット枚数
        this.quantity = 1; //初期値
        // 選択した座席表示用の商品販売単位配列
        this.selectedSalesUnitQuantitys = [];
        //枚数選択POST初期データ
        this.data = {
            "reserve_type": "auto",
            "auto_select_conditions": {
                "stock_type_id": 0,
                "quantity": 0
            }
        };
        //svgから取得する座席配列
        this.seatNameList = [];
        this.defaultMaxQuantity = 10;
        //ボタン表示・非表示
        this.nextButtonFlag = false;
        //座席確保飛び席モーダルフラグ
        this.separatDetailDisplay = false;
    }
    ReserveByQuantityComponent.prototype.ngOnInit = function () {
        var _this = this;
        this.nextButtonFlag = false;
        this.stockTypeDataService.toQuentityData$.subscribe(function (stockTypeId) {
            _this.selectStockTypeId = stockTypeId;
            _this.loadPerformance();
        });
        this.countSelectService.toQuentityData$.subscribe(function (countSelect) {
            _this.countSelectVenuemap = countSelect;
        });
    };
    //公演情報API呼び出し
    ReserveByQuantityComponent.prototype.loadPerformance = function () {
        var _this = this;
        var that = this;
        var timer;
        var regionId;
        this.route.params.subscribe(function (params) {
            if (params && params['performance_id']) {
                //パラメーター切り出し
                _this.performanceId = +params['performance_id'];
                //公演情報取得
                _this.performances.getPerformance(_this.performanceId)
                    .subscribe(function (response) {
                    _this._logger.debug("get performance(#" + _this.performanceId + ") success", response);
                    _this.performance = response.data.performance;
                    _this.mapURL = _this.performance.mini_venue_map_url;
                    _this.performanceOrderLimit = _this.performance.order_limit;
                    _this.eventOrderLimit = response.data.event.order_limit;
                    _this.selesSegments = _this.performance.sales_segments;
                    _this.selesSegmentId = _this.selesSegments[0].sales_segment_id;
                    //席種情報取得
                    if (_this.performanceId && _this.selesSegmentId && _this.selectStockTypeId) {
                        _this.stockTypes.getStockType(_this.performanceId, _this.selesSegmentId, _this.selectStockTypeId)
                            .subscribe(function (response) {
                            _this._logger.debug("get stockType(#" + _this.performanceId + ") success", response);
                            //レスポンスが正常に返ってくれば表示
                            _this.display = true;
                            __WEBPACK_IMPORTED_MODULE_13_jquery__('html,body').css({
                                'width': '100%',
                                'height': '100%',
                            });
                            _this.stockType = response.data.stock_types[0];
                            //席種名と商品情報取得
                            _this.stockTypeName = _this.stockType.stock_type_name;
                            _this.selectedProducts = _this.stockType.products;
                            _this.selectedSalesUnitQuantitys = _this.QuentityChecks.eraseOne(_this.stockType.products);
                            _this.description = _this.stockType.description ? _this.stockType.description : '';
                            _this.minQuantity = _this.stockType.min_quantity;
                            _this.maxQuantity = _this.stockType.max_quantity;
                            that.regions = _this.stockType.regions;
                            _this.modalTopCss();
                            //regionsがある時のみ色付けインターバル開始
                            if (that.regions.length > 0) {
                                startTimer();
                            }
                            that.nextButtonFlag = true;
                            //インターバル処理
                            function startTimer() {
                                var getMap;
                                timer = setInterval(function () {
                                    getMap = document.getElementById("venue-quentity");
                                    if (getMap && getMap.firstElementChild) {
                                        //二重色付け制限
                                        if (__WEBPACK_IMPORTED_MODULE_13_jquery__('#venue-quentity').find('.region').css({ 'fill': 'red' })) {
                                            __WEBPACK_IMPORTED_MODULE_13_jquery__('#venue-quentity').find('.region').css({
                                                'fill': 'white'
                                            });
                                        }
                                        //色付け
                                        for (var i = 0; i < that.regions.length; i++) {
                                            __WEBPACK_IMPORTED_MODULE_13_jquery__('#venue-quentity').find('#' + that.regions[i]).css({
                                                'fill': 'red'
                                            });
                                        }
                                        //インターバル処理終了
                                        clearInterval(timer);
                                    }
                                }, 100);
                            }
                        }, function (error) {
                            _this._logger.error('stockType error:' + error);
                            //レスポンスがエラーの場合は非表示
                            _this.display = false;
                            _this.scrollAddCss();
                            if (error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                                _this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
                            }
                        });
                    }
                    else {
                        _this.display = false;
                        _this.scrollAddCss();
                        _this._logger.error("パラメータに異常が発生しました。");
                        _this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
                    }
                }, function (error) {
                    _this.display = false;
                    _this.scrollAddCss();
                    _this._logger.error('performances error:' + error);
                    if (error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                        _this.errorModalDataService.sendToErrorModal('エラー', '公演情報を取得できません。');
                    }
                });
            }
            else {
                _this.display = false;
                _this.scrollAddCss();
                _this._logger.error('エラー', '公演IDを取得できません。');
                _this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
            }
        });
    };
    ReserveByQuantityComponent.prototype.scrollAddCss = function () {
        //スクロール解除
        __WEBPACK_IMPORTED_MODULE_13_jquery__('html').css({
            'height': "100%",
            'overflow-y': "hidden"
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('body').css({
            'height': "100%",
            'overflow-y': "auto"
        });
    };
    //閉じるボタン
    ReserveByQuantityComponent.prototype.closeClick = function () {
        this.display = false;
        this.output.emit(false);
        this.nextButtonFlag = false;
        this.quantity = 1;
    };
    //チケット枚数減少
    ReserveByQuantityComponent.prototype.minusClick = function () {
        if (this.QuentityChecks.minLimitCheck(this.minQuantity, this.quantity - 1)) {
            this.quantity--;
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#plus-btn').removeClass('disabled');
            if (!this.QuentityChecks.minLimitCheck(this.minQuantity, this.quantity - 1)) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__('#minus-btn').addClass('disabled');
            }
        }
        else {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#minus-btn').addClass('disabled');
        }
    };
    //チケット枚数増加
    ReserveByQuantityComponent.prototype.plusClick = function () {
        if (this.QuentityChecks.maxLimitCheck(this.maxQuantity, this.performanceOrderLimit, this.eventOrderLimit, this.quantity + 1)) {
            this.quantity++;
            __WEBPACK_IMPORTED_MODULE_13_jquery__("#minus-btn").removeClass('disabled');
            if (!this.QuentityChecks.maxLimitCheck(this.maxQuantity, this.performanceOrderLimit, this.eventOrderLimit, this.quantity + 1)) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__("#plus-btn").addClass('disabled');
            }
        }
        else {
            __WEBPACK_IMPORTED_MODULE_13_jquery__("#plus-btn").addClass('disabled');
        }
    };
    //座席確保ボタン選択
    ReserveByQuantityComponent.prototype.seatReserveClick = function () {
        var _this = this;
        var isSeparated;
        this.animationEnableService.sendToRoadFlag(true);
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", true);
        if (this.countSelectVenuemap == 0) {
            if (!this.QuentityChecks.salesUnitCheck(this.selectedProducts, this.quantity)) {
                this.dataUpdate();
                this.route.params.subscribe(function (params) {
                    if (params && params['performance_id']) {
                        //パラメーター切り出し
                        _this.performanceId = +params['performance_id'];
                        //座席確保api
                        _this.seatStatus.seatReserve(_this.performanceId, _this.selesSegmentId, _this.data).subscribe(function (response) {
                            _this._logger.debug("get seatReserve(#" + _this.performanceId + ") success", response);
                            _this.resSeatIds = response.data.results.seats;
                            _this.seatStatus.seatReserveResponse = response;
                            _this.seatPostStatus = response.data.results.status;
                            isSeparated = response.data.results.is_separated;
                            if (_this.seatPostStatus == "OK") {
                                // //座席選択の場合、座席名取得
                                _this.seatNameList = [];
                                if (!response.data.results.is_quantity_only) {
                                    for (var i = 0; i < _this.resSeatIds.length; i++) {
                                        _this.seatNameList[i] = _this.resSeatIds[i].seat_name;
                                    }
                                    _this.resResult = response.data.results;
                                    _this.resResult.seat_name = _this.seatNameList;
                                    response.data.results = _this.resResult;
                                    if (isSeparated) {
                                        _this.animationEnableService.sendToRoadFlag(false);
                                        __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
                                        _this.separatDetailDisplay = true;
                                        return;
                                    }
                                    else {
                                        _this.animationEnableService.sendToRoadFlag(false);
                                        _this.router.navigate(["performances/" + _this.performanceId + '/select-product/']);
                                    }
                                }
                                //OKの場合、商品選択へ画面遷移
                                _this.animationEnableService.sendToRoadFlag(false);
                                _this.router.navigate(["performances/" + _this.performanceId + '/select-product/']);
                            }
                            else {
                                _this.animationEnableService.sendToRoadFlag(false);
                                __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
                                _this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');
                                _this.seatUpdate(); //座席情報最新化
                            }
                        }, function (error) {
                            _this.animationEnableService.sendToRoadFlag(false);
                            __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
                            _this._logger.error('seatReserve error:' + error);
                            if (error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                                _this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');
                            }
                            _this.seatUpdate(); //座席情報最新化
                        });
                    }
                    else {
                        _this.animationEnableService.sendToRoadFlag(false);
                        __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
                        _this._logger.error("エラー:公演IDを取得できません");
                        _this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
                    }
                });
            }
            else {
                this.animationEnableService.sendToRoadFlag(false);
                __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
                this.errorModalDataService.sendToErrorModal('エラー', this.QuentityChecks.salesUnitCheck(this.selectedProducts, this.quantity) + '席単位でご選択ください。');
            }
        }
        else {
            this.animationEnableService.sendToRoadFlag(false);
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
            this.confirmStockType.emit(true);
        }
    };
    //data更新
    ReserveByQuantityComponent.prototype.dataUpdate = function () {
        this.data = {
            "reserve_type": "auto",
            "auto_select_conditions": {
                "stock_type_id": this.selectStockTypeId,
                "quantity": this.quantity
            }
        };
    };
    //NGorERRORの場合、座席情報検索apiを呼び、空席情報を更新する処理
    ReserveByQuantityComponent.prototype.seatUpdate = function () {
        this.filterComponent.search();
    };
    //飛び席モーダル「選び直す」ボタン
    ReserveByQuantityComponent.prototype.separatedSelectAgain = function () {
        var _this = this;
        var releaseResponse;
        //座席開放API
        this.seatStatus.seatRelease(this.performanceId)
            .subscribe(function (response) {
            _this._logger.debug("seat release(#" + _this.performanceId + ") success", response);
            releaseResponse = response.data.results;
            if (releaseResponse.status == "NG") {
                _this._logger.debug("seat release error", response);
                _this.errorModalDataService.sendToErrorModal('エラー', '座席を解放できません。');
            }
        }, function (error) {
            _this._logger.debug("seat release error", error);
            if (error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_14__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                _this.errorModalDataService.sendToErrorModal('エラー', '座席を解放できません。');
            }
        });
        //モーダル非表示
        this.separatDetailDisplay = false;
    };
    //飛び席モーダル「次へ」ボタン
    ReserveByQuantityComponent.prototype.separatedNext = function () {
        this.animationEnableService.sendToRoadFlag(false);
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#reservebutton').prop("disabled", false);
        this.router.navigate(['performances/' + this.performanceId + '/select-product/']);
    };
    //SP、検索エリアがアクティブ時のモーダルのトップ調整
    ReserveByQuantityComponent.prototype.modalTopCss = function () {
        if (this.smartPhoneCheckService.isSmartPhone()) {
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__(".choiceAreaAcdBox").css('display') == "block") {
                setTimeout(function () {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__("#modalWindowAlertBox").css({
                        'top': "-220px",
                    });
                }, 100);
            }
            else {
                setTimeout(function () {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__("#modalWindowAlertBox").css({
                        'top': "-37px",
                    });
                }, 100);
            }
        }
    };
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', (typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_7__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_7__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */]) === 'function' && _a) || Object)
    ], ReserveByQuantityComponent.prototype, "filterComponent", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', Boolean)
    ], ReserveByQuantityComponent.prototype, "display", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Output"])(), 
        __metadata('design:type', Object)
    ], ReserveByQuantityComponent.prototype, "output", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Output"])(), 
        __metadata('design:type', Object)
    ], ReserveByQuantityComponent.prototype, "confirmStockType", void 0);
    ReserveByQuantityComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-reserve-by-quantity',
            template: __webpack_require__("../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.html"),
            styles: [__webpack_require__("../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.css")]
        }),
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["NgModule"])({
            imports: [],
            declarations: [
                __WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]
            ],
            bootstrap: [__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]]
        }), 
        __metadata('design:paramtypes', [(typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_12__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_12__angular_router__["ActivatedRoute"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_12__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_12__angular_router__["Router"]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_1__shared_services_performances_service__["a" /* PerformancesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__shared_services_performances_service__["a" /* PerformancesService */]) === 'function' && _d) || Object, (typeof (_e = typeof __WEBPACK_IMPORTED_MODULE_2__shared_services_stock_types_service__["a" /* StockTypesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2__shared_services_stock_types_service__["a" /* StockTypesService */]) === 'function' && _e) || Object, (typeof (_f = typeof __WEBPACK_IMPORTED_MODULE_3__shared_services_seat_status_service__["a" /* SeatStatusService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__shared_services_seat_status_service__["a" /* SeatStatusService */]) === 'function' && _f) || Object, (typeof (_g = typeof __WEBPACK_IMPORTED_MODULE_8__shared_services_seats_service__["a" /* SeatsService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_8__shared_services_seats_service__["a" /* SeatsService */]) === 'function' && _g) || Object, (typeof (_h = typeof __WEBPACK_IMPORTED_MODULE_4__shared_services_quentity_check_service__["a" /* QuentityCheckService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__shared_services_quentity_check_service__["a" /* QuentityCheckService */]) === 'function' && _h) || Object, (typeof (_j = typeof __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_type_data_service__["a" /* StockTypeDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_type_data_service__["a" /* StockTypeDataService */]) === 'function' && _j) || Object, (typeof (_k = typeof __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _k) || Object, (typeof (_l = typeof __WEBPACK_IMPORTED_MODULE_9__shared_services_count_select_service__["a" /* CountSelectService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_9__shared_services_count_select_service__["a" /* CountSelectService */]) === 'function' && _l) || Object, (typeof (_m = typeof __WEBPACK_IMPORTED_MODULE_10__shared_services_animation_enable_service__["a" /* AnimationEnableService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_10__shared_services_animation_enable_service__["a" /* AnimationEnableService */]) === 'function' && _m) || Object, (typeof (_o = typeof __WEBPACK_IMPORTED_MODULE_11__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_11__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */]) === 'function' && _o) || Object, (typeof (_p = typeof __WEBPACK_IMPORTED_MODULE_15_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_15_angular2_logger_core__["Logger"]) === 'function' && _p) || Object])
    ], ReserveByQuantityComponent);
    return ReserveByQuantityComponent;
    var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/reserve-by-quantity.component.js.map

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/event-info/event-info.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/event-info/event-info.component.html":
/***/ (function(module, exports) {

module.exports = "<section class=\"headArea\">\n  <div class=\"inner\">\n    <p><span>{{performance.performance_name}}</span><span class=\"place\">{{performance.venue_name}}</span>\n    <span>{{year}}年{{month}}月{{day}}日 {{startOnTime}}～</span>\n    </p>\n    <button type=\"button\" class=\"haBtn02 pc\" (click)= \"onClick()\"><span class=\"iconSearch\"></span><span>他の試合へ</span></button>\n  </div>\n</section>\n"

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/event-info/event-info.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return EventinfoComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};



var EventinfoComponent = (function () {
    /**
     * コンストラクタ
     */
    function EventinfoComponent(route, router, AppConstService) {
        this.route = route;
        this.router = router;
        this.AppConstService = AppConstService;
    }
    /**
     * 初期化処理
     */
    EventinfoComponent.prototype.ngOnInit = function () {
        var response = this.route.snapshot.data['performance'];
        this.performance = response.data.performance;
        var startOn = new Date(this.performance.start_on + '+09:00');
        this.startOnTime = startOn.getHours() + '時';
        if (startOn.getMinutes() != 0) {
            this.startOnTime += startOn.getMinutes() + '分';
        }
        this.year = startOn.getFullYear();
        this.month = startOn.getMonth() + 1;
        this.day = startOn.getDate();
    };
    EventinfoComponent.prototype.onClick = function () {
        location.href = "" + __WEBPACK_IMPORTED_MODULE_2__app_constants__["b" /* AppConstService */].PAGE_URL.TOP;
    };
    EventinfoComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            providers: [__WEBPACK_IMPORTED_MODULE_2__app_constants__["b" /* AppConstService */]],
            selector: 'app-event-info',
            template: __webpack_require__("../../../../../src/app/reserve-by-seat/event-info/event-info.component.html"),
            styles: [__webpack_require__("../../../../../src/app/reserve-by-seat/event-info/event-info.component.css")]
        }),
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["NgModule"])({
            imports: [],
            declarations: [
                __WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]
            ],
            bootstrap: [__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_2__app_constants__["b" /* AppConstService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2__app_constants__["b" /* AppConstService */]) === 'function' && _c) || Object])
    ], EventinfoComponent);
    return EventinfoComponent;
    var _a, _b, _c;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/event-info.component.js.map

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/filter/filter.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/filter/filter.component.html":
/***/ (function(module, exports) {

module.exports = "<section class=\"choiceArea\">\n  <div class=\"inner\">\n  <div class=\"choiceAreaMenuBtn acdBt sp cf\"><span></span>絞り込み検索</div>\n    <div class=\"choiceAreaAcdBox\">\n      <div id=\"ticketPrice\" class=\"ticketPrice\">\n        <label class=\"priceTtl\">価格</label>\n        <div class=\"ticketPriceInner\">\n          <div class=\"ticketPriceBerBox\">\n            <div class=\"ticketPriceBer\">\n              <nouislider id=\"slider\" [connect]=\"true\" [min]=\"min\" [max]=\"max\" [tooltips]=\"[ true, true ]\" [step]=\"stepValue\" [ngModel]=\"seatPrices\" (change)=\"onChangeSlider(seatPrices)\" [disabled]=\"sliderBool\"></nouislider>\n            </div>\n          </div>\n          <button *ngIf=\"setPriceInitFlag\" class=\"minPrice\" type=\"button\">&yen;&nbsp;<span>{{seatPrices[0]}}</span></button>\n          <button *ngIf=\"setPriceInitFlag\" class=\"maxPrice\" type=\"button\">&yen;&nbsp;<span>{{seatPrices[1]}}</span></button>\n        </div>\n      </div>\n\n      <div id=\"seatSearch\" class=\"seatSearch cf\">\n        <div class=\"seatSearchFormBox\">\n          <form id=\"seatSearchForm\" name=\"seatSearchForm\" ngNoForm>\n            <label class=\"searchbox\">席種</label><input id=\"input\" type=\"text\" maxlength='50' size=\"14\" class=\"form-control\" placeholder=\"席種名で検索\" [(ngModel)]=\"seatName\" pInputText />\n            <input type=\"checkbox\" value=\"指定席\" id=\"ssCheck01\" (ngModelChange)=\"onChangeReserved(reserved)\" [(ngModel)]=\"reserved\" checked><label class=\"checkbox\" for=\"ssCheck01\">指定<span class=\"pc\">席</span></label>\n            <input type=\"checkbox\" value=\"自由席\" id=\"ssCheck02\" (ngModelChange)=\"onChangeUnreserved(unreserved)\" [(ngModel)]=\"unreserved\" checked><label class=\"checkbox\" for=\"ssCheck02\">自由<span class=\"pc\">席</span></label>\n          </form>\n        </div>\n        <div class=\"seatSearchButtonbox\">\n          <button pButton type=\"button\" id=\"search-btn\" form=\"seatSearchForm\" (click)=\"searchClick()\" label=\"検索\"></button>\n          <button pButton type=\"button\" id=\"clear-btn\" form=\"seatSearchForm\" (click)=\"clearClick()\" label=\"検索条件をクリア\"></button>\n        </div>\n      </div>\n    </div>\n  </div>\n</section>"

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/filter/filter.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return FilterComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_primeng_primeng__ = __webpack_require__("../../../../primeng/primeng.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_primeng_primeng___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_primeng_primeng__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__shared_services_seats_service__ = __webpack_require__("../../../../../src/app/shared/services/seats.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__shared_services_stock_types_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_type_data_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-type-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__shared_services_animation_enable_service__ = __webpack_require__("../../../../../src/app/shared/services/animation-enable.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_8_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10_ng2_nouislider__ = __webpack_require__("../../../../ng2-nouislider/src/nouislider.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10_ng2_nouislider___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_10_ng2_nouislider__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_11_angular2_logger_core__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};












var FilterComponent = (function () {
    function FilterComponent(seats, route, stockTypeService, errorModalDataService, animationEnableService, stockTypeDataService, _logger) {
        this.seats = seats;
        this.route = route;
        this.stockTypeService = stockTypeService;
        this.errorModalDataService = errorModalDataService;
        this.animationEnableService = animationEnableService;
        this.stockTypeDataService = stockTypeDataService;
        this._logger = _logger;
        //金額初期値
        this.min = 0;
        this.max = 50000;
        this.stepValue = 100; //区切り
        this.setPriceInitNumber = 0;
        this.setPriceInitFlag = false;
        //金額範囲
        this.seatPrices = [0, 50000];
        //席種名
        this.seatName = "";
        //席種チェックボックス（指定席、自由席）
        this.unreserved = true; //自由席
        this.reserved = true; //指定席
        this.seatValues = [this.unreserved, this.reserved];
        //検索中フラグ
        this.searching = false;
        //スライダーの有効・無効
        this.sliderBool = false;
        //スライダー値取得フラグ
        this.getSliderValue = false;
        //自由席regionId配列
        this.unreservedRegionIds = [];
        //指定席regionId配列
        this.reservedRegionIds = [];
        //検索有効無効
        this.isSearch = false;
        this.searched$ = new __WEBPACK_IMPORTED_MODULE_0__angular_core__["EventEmitter"]();
    }
    FilterComponent.prototype.ngOnInit = function () {
        var _this = this;
        //公演情報
        var performanceRes = this.route.snapshot.data['performance'];
        this.performance = performanceRes.data.performance;
        this.performanceId = this.performance.performance_id;
        this.salesSegmentId = this.performance.sales_segments[0].sales_segment_id;
        //席種情報検索
        var stockTypesRes = this.route.snapshot.data['stockTypes'];
        this.stockTypes = stockTypesRes.data.stock_types;
        //初期金額セット＋検索処理
        this.setPriceInit();
        this.stockTypeDataService.toIsSearchFlag$.subscribe(function (flag) {
            _this.isSearch = flag;
        });
        //席種名検索時Enterキー無効化
        __WEBPACK_IMPORTED_MODULE_8_jquery__(function () {
            __WEBPACK_IMPORTED_MODULE_8_jquery__("input").keydown(function (e) {
                if ((e.which && e.which === 13) || (e.keyCode && e.keyCode === 13)) {
                    return false;
                }
                else {
                    return true;
                }
            });
        });
    };
    //Slider初期表示
    FilterComponent.prototype.setPriceInit = function () {
        var _this = this;
        var that = this;
        var selesSegmentId = this.performance.sales_segments[0].sales_segment_id;
        var stockTypeIds = [];
        var products = [];
        var resions = [];
        var allPrices = [];
        var prices = [];
        var minPrice = 0;
        var maxPrice = 0;
        this.stockTypeService.getStockTypesAll(this.performanceId, selesSegmentId)
            .subscribe(function (response) {
            _this._logger.debug("get StockTypesAll(#" + _this.performanceId + ") success", response);
            var stockTypes = response.data.stock_types;
            if (_this.stockTypes.length > 0) {
                for (var i = 0, len = stockTypes.length; i < len; i++) {
                    var productPrice = 0;
                    var resions_1 = stockTypes[i].regions;
                    if (stockTypes[i].products.length) {
                        productPrice = +stockTypes[i].products[0].price;
                    }
                    else {
                        continue;
                    }
                    if (resions_1.length > 0) {
                        for (var l = 0, urlen = resions_1.length; l < urlen; l++) {
                            if (stockTypes[i].is_quantity_only) {
                                _this.unreservedRegionIds.push(resions_1[l]); //自由席のregionIdを取得
                            }
                            else {
                                _this.reservedRegionIds.push(resions_1[l]); //指定席のregionIdを取得
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
                _this.max = maxPrice;
                _this.min = (minPrice == maxPrice) ? 0 : minPrice;
                _this.seatPrices = [minPrice, maxPrice];
                _this.setPriceInitFlag = true;
                //初期表示処理
                _this.valueGetTime();
                _this.searchs(_this.seatPrices[0], _this.seatPrices[1], _this.seatName, _this.seatValues[0], _this.seatValues[1]);
            }
            else {
                _this.max = 100;
                _this.min = 0;
                setTimeout(function () {
                    that.seatPrices = [0, 100];
                    that.setPriceInitFlag = true;
                }, 100);
                _this.valueGetTime();
                _this.search();
            }
        }, function (error) {
            _this._logger.error('[FilterComponent]getStockType error', error);
            if (error != "" + __WEBPACK_IMPORTED_MODULE_9__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_9__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_9__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                _this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
            }
        });
        //初期表示処理
        if (this.stockTypes.length > 1) {
            var sliderStartTimer_1 = setInterval(function () {
                if (that.getSliderValue) {
                    //スライダーを動かしたときの処理
                    __WEBPACK_IMPORTED_MODULE_8_jquery__('.noUi-handle-lower')
                        .mousedown(function () {
                        if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-handle-upper .noUi-active").length == 0) {
                            that.moveLowerSlier();
                        }
                    })
                        .bind('touchstart', function () {
                        if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-handle-upper .noUi-active").length == 0) {
                            that.moveLowerSlier();
                        }
                    });
                    __WEBPACK_IMPORTED_MODULE_8_jquery__('.noUi-handle-upper')
                        .mousedown(function () {
                        if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-handle-lower .noUi-active").length == 0) {
                            that.moveUpperSlider();
                        }
                    })
                        .bind('touchstart', function () {
                        if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-handle-lower .noUi-active").length == 0) {
                            that.moveUpperSlider();
                        }
                    });
                    clearInterval(sliderStartTimer_1);
                }
            }, 100);
        }
        else if (this.stockTypes.length == 1) {
            this.seatPrices = [0, this.max];
        }
        else {
            this.seatPrices = [0, 0];
        }
    };
    //スライダー値取得タイマー
    FilterComponent.prototype.valueGetTime = function () {
        var valueGetTimer;
        var that = this;
        valueGetTimer = setInterval(function () {
            if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-tooltip").length > 0) {
                that.getSliderValue = true;
                clearInterval(valueGetTimer);
            }
        }, 100);
    };
    //左レンジ変更処理
    FilterComponent.prototype.moveLowerSlier = function () {
        var valueTimer;
        var that = this;
        valueTimer = setInterval(function () {
            var tooltipElements = document.getElementsByClassName("noUi-tooltip");
            that.seatPrices[0] = that.lowerRounding(+tooltipElements[0].innerHTML);
            //スライダーを離したときの処理
            __WEBPACK_IMPORTED_MODULE_8_jquery__('.noUi-handle-lower')
                .mouseup(function () {
                clearInterval(valueTimer);
            })
                .bind('touchend', function () {
                clearInterval(valueTimer);
            });
            if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-active").length == 0) {
                clearInterval(valueTimer);
            }
        }, 100);
    };
    //右レンジ変更処理
    FilterComponent.prototype.moveUpperSlider = function () {
        var valueTimer;
        var that = this;
        valueTimer = setInterval(function () {
            var tooltipElements = document.getElementsByClassName("noUi-tooltip");
            that.seatPrices[1] = that.upperRounding(+tooltipElements[1].innerHTML);
            //スライダーを離したときの処理
            __WEBPACK_IMPORTED_MODULE_8_jquery__('.noUi-handle-upper')
                .mouseup(function () {
                clearInterval(valueTimer);
            })
                .bind('touchend', function () {
                clearInterval(valueTimer);
            });
            if (__WEBPACK_IMPORTED_MODULE_8_jquery__(".noUi-active").length == 0) {
                clearInterval(valueTimer);
            }
        }, 100);
    };
    //左レンジ値四捨五入処理
    FilterComponent.prototype.lowerRounding = function (minNum) {
        var minCalNum;
        var connectElements = document.getElementsByClassName("noUi-connect");
        if (String(minNum).length >= 3) {
            minCalNum = minNum / 100;
            minCalNum = Math.round(minCalNum) * 100;
            if (connectElements[0].outerHTML.indexOf("left: 0%") > -1) {
                return this.min;
            }
            else if (connectElements[0].outerHTML.indexOf("left: 100%") > -1) {
                return this.max;
            }
            return minCalNum;
        }
        else {
            return minNum;
        }
    };
    //右レンジ値四捨五入処理
    FilterComponent.prototype.upperRounding = function (maxNum) {
        var maxCalNum;
        var connectElements = document.getElementsByClassName("noUi-connect");
        if (String(maxNum).length >= 3) {
            maxCalNum = maxNum / 100;
            maxCalNum = Math.round(maxCalNum) * 100;
            if (connectElements[0].outerHTML.indexOf("right: 0%") > -1) {
                return this.max;
            }
            else if (connectElements[0].outerHTML.indexOf("right: 100%") > -1) {
                return this.min;
            }
            return maxCalNum;
        }
        else {
            if (connectElements[0].outerHTML.indexOf("right: 100%") > -1) {
                return this.min;
            }
            return maxNum;
        }
    };
    FilterComponent.prototype.searchClick = function () {
        if (!this.searching) {
            this.getIsSearchFlag();
            if (!this.searching && !this.isSearch) {
                this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
            }
        }
    };
    //各項目を初期化
    FilterComponent.prototype.clearClick = function () {
        this.getIsSearchFlag();
        if (!this.searching && !this.isSearch) {
            this.seatPrices = [this.min, this.max];
            this.seatName = "";
            this.unreserved = true;
            this.reserved = true;
            this.seatValues = [true, true];
            this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
        }
    };
    FilterComponent.prototype.getIsSearchFlag = function () {
        var _this = this;
        this.stockTypeDataService.toIsSearchFlag$.subscribe(function (flag) {
            _this.isSearch = flag;
        });
        if (this.isSearch) {
            this.errorModalDataService.sendToErrorModal('エラー', '座席確保状態では絞込み検索をご利用いただけません');
        }
    };
    //スライダー値変更
    FilterComponent.prototype.onChangeSlider = function (e) {
        if (document.getElementsByClassName("noUi-tooltip")) {
            var tooltipelements = document.getElementsByClassName("noUi-tooltip");
            this.seatPrices[0] = this.lowerRounding(+tooltipelements["0"].innerHTML);
            this.seatPrices[1] = this.upperRounding(+tooltipelements["1"].innerHTML);
        }
    };
    //自由席チェック変更
    FilterComponent.prototype.onChangeUnreserved = function (unreserved) {
        if (unreserved) {
            this.seatValues[0] = false;
        }
        else {
            this.seatValues[0] = true;
        }
    };
    //指定席チェック変更
    FilterComponent.prototype.onChangeReserved = function (reserved) {
        if (reserved) {
            this.seatValues[1] = false;
        }
        else {
            this.seatValues[1] = true;
        }
    };
    //座席選択時処理
    FilterComponent.prototype.selectSeatSearch = function (name) {
        this.seatPrices = [this.min, this.max];
        this.unreserved = true;
        this.reserved = true;
        this.seatValues = [true, true];
        this.seatName = name;
        if (!this.searching) {
            this.searchs(this.seatPrices[0], this.seatPrices[1], this.seatName, this.seatValues[0], this.seatValues[1]);
        }
    };
    //検索パラメータ取得処理
    FilterComponent.prototype.getSearchParams = function () {
        var params = {
            fields: "",
            min_price: this.seatPrices[0],
            max_price: this.seatPrices[1],
            stock_type_name: this.seatName,
        };
        return params;
    };
    //検索処理
    FilterComponent.prototype.search = function () {
        var _this = this;
        this._logger.debug("seat search start");
        this.searching = true;
        __WEBPACK_IMPORTED_MODULE_8_jquery__('.reserve').prop("disabled", true);
        this.animationEnableService.sendToRoadFlag(true);
        var find = this.seats.findSeatsByPerformanceId(this.performance.performance_id, this.getSearchParams())
            .map(function (response) {
            for (var i = 0; i < response.data.stock_types.length; i++) {
                response.data.stock_types[i] = Object.assign(response.data.stock_types[i], _this.stockTypes.find(function (obj) { return obj.stock_type_id == response.data.stock_types[i].stock_type_id; }));
            }
            return response;
        });
        find.subscribe(function (response) {
            _this._logger.debug("seat search completed", response);
            __WEBPACK_IMPORTED_MODULE_8_jquery__('.reserve').prop("disabled", false);
            _this.searching = false;
            _this.animationEnableService.sendToRoadFlag(false);
            _this.sliderBool = false;
            _this.searched$.emit(response);
        }, function (error) {
            _this.searching = false;
            __WEBPACK_IMPORTED_MODULE_8_jquery__('.reserve').prop("disabled", false);
            _this.animationEnableService.sendToRoadFlag(false);
            _this._logger.error("seat search error", error);
            if (error != "" + __WEBPACK_IMPORTED_MODULE_9__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_9__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_9__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                _this.errorModalDataService.sendToErrorModal('エラー', '座席情報検索を取得できません。');
            }
        });
        return find;
    };
    //検索項目変更ディレイ（連打防止）
    FilterComponent.prototype.searchs = function (min, max, name, unreserved, reserved) {
        var _this = this;
        setTimeout(function () {
            if (min == _this.seatPrices[0] && max == _this.seatPrices[1] &&
                name == _this.seatName && unreserved == _this.seatValues[0] && reserved == _this.seatValues[1]) {
                _this.search();
            }
        }, 500);
    };
    FilterComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-filter',
            template: __webpack_require__("../../../../../src/app/reserve-by-seat/filter/filter.component.html"),
            styles: [__webpack_require__("../../../../../src/app/reserve-by-seat/filter/filter.component.css")],
            providers: [],
        }),
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["NgModule"])({
            imports: [
                __WEBPACK_IMPORTED_MODULE_2_primeng_primeng__["InputTextModule"],
                __WEBPACK_IMPORTED_MODULE_10_ng2_nouislider__["NouisliderModule"]
            ],
            declarations: [
                __WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]
            ],
            bootstrap: [__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]]
        }),
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_3__shared_services_seats_service__["a" /* SeatsService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__shared_services_seats_service__["a" /* SeatsService */]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__shared_services_stock_types_service__["a" /* StockTypesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__shared_services_stock_types_service__["a" /* StockTypesService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _d) || Object, (typeof (_e = typeof __WEBPACK_IMPORTED_MODULE_7__shared_services_animation_enable_service__["a" /* AnimationEnableService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_7__shared_services_animation_enable_service__["a" /* AnimationEnableService */]) === 'function' && _e) || Object, (typeof (_f = typeof __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_type_data_service__["a" /* StockTypeDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_type_data_service__["a" /* StockTypeDataService */]) === 'function' && _f) || Object, (typeof (_g = typeof __WEBPACK_IMPORTED_MODULE_11_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_11_angular2_logger_core__["Logger"]) === 'function' && _g) || Object])
    ], FilterComponent);
    return FilterComponent;
    var _a, _b, _c, _d, _e, _f, _g;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/filter.component.js.map

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/reserve-by-seat.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/reserve-by-seat.component.html":
/***/ (function(module, exports) {

module.exports = "<header>\n  <div class=\"inner\">\n    <h1 class=\"title\"><a href=\"/\"><img src=\"https://tstar.s3.amazonaws.com/extauth/static/eagles/images/logo.png\" alt=\"イーグルスチケット\"></a></h1>\n    <form id=\"logout\" ngNoForm action=\"/cart/logout\" target=\"_self\" method=\"POST\">\n      <button id=\"logout\" type=\"submit\">ログアウト</button>\n    </form>\n  </div>\n</header>\n\n\n<div class=\"login-page\">\n  <div class=\"contents\">\n  \n  \n<!--****************************************************************-->\n  \n\n    <!--  event-info   -->\n      <app-event-info></app-event-info>\n    <!--  /event-info   -->\n\n    <!--  filter   -->\n      <app-filter #filter></app-filter>\n    <!--  /filter   -->\n      \n      <section class=\"mapArea\">\n        <!--  venue-map   -->\n          <app-venue-map #venuemap [filterComponent]=\"filter\" [mapAreaLeftH]=\"mapAreaLeftH\"></app-venue-map>\n        <!--  /venue-map   -->\n      </section>\n\n\n<!--****************************************************************-->\n\n\n    </div>\n</div>\n<!-- .contents -->\n\n<!--SiteCatalyst-->\n\n\n<!--<footer>\n  <div class=\"page-top-box\">\n    <a href=\"#\" class=\"sp page-top\" id=\"pageTop\">\n      <span class=\"arrow top\"></span>\n    </a>\n  </div>\n\n  <p class=\"copyright\">\n    <small>&copy; TicketStar, Inc.</small>\n  </p>\n</footer>-->"

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/reserve-by-seat.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return ReserveBySeatComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__ = __webpack_require__("../../../../ng2-loading-animate/ng2-loading-animate.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_jquery__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};




var ReserveBySeatComponent = (function () {
    function ReserveBySeatComponent(route, loadingService) {
        this.route = route;
        this.loadingService = loadingService;
        // マップの高さ
        this.mapAreaLeftH = 0;
    }
    ReserveBySeatComponent.prototype.ngOnInit = function () {
        //ローディング表示
        this.loadingService.setValue(true);
        var response = this.route.snapshot.data['performance'];
        this.performance = response.data.performance;
        this.pageTitle = this.performance.performance_name;
        var that = this;
        //ここからmainHeight.js
        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
            var mainH;
            var windowH;
            var windowWidth = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).width();
            var windowSm = 768;
            if (windowWidth <= windowSm) {
                //横幅768px以下のとき（つまりスマホ時）に行う処理を書く
                __WEBPACK_IMPORTED_MODULE_3_jquery__(document).ready(function () {
                    __WEBPACK_IMPORTED_MODULE_3_jquery__('.acdTp').click(function () {
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(this).prev().slideToggle(300);
                    }).prev().hide();
                });
                //filterのtoggle
                __WEBPACK_IMPORTED_MODULE_3_jquery__(document).ready(function () {
                    __WEBPACK_IMPORTED_MODULE_3_jquery__('.acdBt').click(function () {
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(this).next().slideToggle(300);
                    }).next().hide();
                });
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    if (__WEBPACK_IMPORTED_MODULE_3_jquery__('#choiceSeatArea').length) {
                        //seat-listが存在した場合
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                            //var minus = 230
                            var minus = 280;
                            var mainID = 'mapAreaLeft';
                            function heightSetting() {
                                windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                                mainH = windowH - minus;
                                that.mapAreaLeftH = mainH;
                                __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                            }
                            heightSetting();
                            __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                                heightSetting();
                            });
                        });
                    }
                });
                // $(function(){
                //   if($('#buySeatArea').length){
                //       //select-productが存在した場合
                //       $(function(){
                //         var minus = 149
                //         var mainID = 'mapAreaLeft'
                //         function heightSetting(){
                //           windowH = $(window).height();
                //           mainH = windowH - minus;
                //           $('#'+mainID).height(mainH+'px');
                //         }
                //         heightSetting();
                //         $(window).resize(function() {
                //           heightSetting();
                //         });
                //       });
                //       $(function(){
                //         var minus = 114
                //         var mainID = 'buySeatArea'
                //         function heightSetting(){
                //           windowH = $(window).height();
                //           mainH = windowH - minus;
                //           $('#'+mainID).height(mainH+'px');
                //         }
                //         heightSetting();
                //         $(window).resize(function() {
                //           heightSetting();
                //         });
                //       });
                //       /////////////////////
                //   }
                // });
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    if (__WEBPACK_IMPORTED_MODULE_3_jquery__('#buyChoiceSeatArea').length) {
                        //venue-mapの選択した座席のリストが存在した場合
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                            var minus = 209;
                            var mainID = 'mapAreaLeft';
                            function heightSetting() {
                                windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                                mainH = windowH - minus;
                                that.mapAreaLeftH = mainH;
                                __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                            }
                            heightSetting();
                            __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                                heightSetting();
                            });
                        });
                    }
                });
                //	$(function(){
                //		var minus = 112
                //		var mainID = 'buyChoiceSeatArea'
                //		function heightSetting(){
                //			windowH = $(window).height();
                //			mainH = windowH - minus;
                //
                //			$('#'+mainID).height(mainH+'px');
                //		}
                //		heightSetting();
                //		$(window).resize(function() {
                //			heightSetting();
                //		});
                //	});
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    if (__WEBPACK_IMPORTED_MODULE_3_jquery__('#modalWindow').length) {
                        //venue-mapの席種詳細モーダルが存在した場合
                        //reserve-by-quantityが存在した場合
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                            var minus = 149;
                            var mainID = 'mapAreaLeft';
                            function heightSetting() {
                                windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                                mainH = windowH - minus;
                                that.mapAreaLeftH = mainH;
                                __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                            }
                            heightSetting();
                            __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                                heightSetting();
                            });
                        });
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                            var minus = 114;
                            var mainID = 'modalWindow';
                            function heightSetting() {
                                windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                                mainH = windowH - minus;
                                __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                            }
                            heightSetting();
                            __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                                heightSetting();
                            });
                        });
                    }
                });
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    var minus = 114;
                    var mainID = 'modalWindowAlertBoxInner';
                    function heightSetting() {
                        windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                        mainH = windowH - minus;
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                    }
                    heightSetting();
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                        heightSetting();
                    });
                });
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    if (!(__WEBPACK_IMPORTED_MODULE_3_jquery__('#choiceSeatArea, #buySeatArea, #buyChoiceSeatArea').length)) {
                        //ここに「＃sample」が存在しなかった場合の処理を記述
                        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                            var minus = 149;
                            var mainID = 'mapAreaLeft';
                            function heightSetting() {
                                windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                                mainH = windowH - minus;
                                that.mapAreaLeftH = mainH;
                                __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                            }
                            heightSetting();
                            __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                                heightSetting();
                            });
                        });
                    }
                });
            }
            else {
                //横幅768px超のとき（タブレット、PC）に行う処理を書く
                /***********************************************************/
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    if (!(__WEBPACK_IMPORTED_MODULE_3_jquery__('#choiceSeatArea, #buySeatArea, #buyChoiceSeatArea').length)) {
                        //ここに「＃sample」が存在しなかった場合の処理を記述
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#mapAreaLeft').addClass('noSide');
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#mapBtnBox').addClass('mapBtnBoxR');
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#mapNaviBox').addClass('mapNaviBoxR');
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#mapAreaRight').addClass('dNone');
                    }
                });
                /***********************************************************/
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    //var minus = 220
                    var minus = 240;
                    var mainID = 'mapAreaLeft';
                    function heightSetting() {
                        windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                        mainH = windowH - minus;
                        that.mapAreaLeftH = mainH;
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                    }
                    heightSetting();
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                        heightSetting();
                    });
                });
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    var minus = 220;
                    var mainID = 'mapAreaRight';
                    function heightSetting() {
                        windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                        mainH = windowH - minus;
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                    }
                    heightSetting();
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                        heightSetting();
                    });
                });
                __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
                    var minus = 169;
                    var mainID = 'buySeatArea';
                    function heightSetting() {
                        windowH = __WEBPACK_IMPORTED_MODULE_3_jquery__(window).height();
                        mainH = windowH - minus;
                        __WEBPACK_IMPORTED_MODULE_3_jquery__('#' + mainID).height(mainH + 'px');
                    }
                    heightSetting();
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(window).resize(function () {
                        heightSetting();
                    });
                });
            }
        });
        /*/////////////////////PC・SP両方/////////////////////////*/
        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
            //venue-mapの選択した座席リスト、select-productのtoggle
            __WEBPACK_IMPORTED_MODULE_3_jquery__("#mapAreaRight").on("click", ".selectBoxBtn", function () {
                __WEBPACK_IMPORTED_MODULE_3_jquery__(this).prev().slideToggle(300);
                // activeが存在する場合
                if (__WEBPACK_IMPORTED_MODULE_3_jquery__(this).children(".closeBtnBox").hasClass('active')) {
                    // activeを削除
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(this).children(".closeBtnBox").removeClass('active');
                }
                else {
                    // activeを追加
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(this).children(".closeBtnBox").addClass('active');
                }
            });
        });
        //【新】
        // var price = 0;
        // $('#ticketQtyForm .iconPlus').click(function(){
        //   $({count: price}).animate({count: price+1}, {
        //     duration: 0,
        //     progress: function() {
        //         $('#ticketQtyForm #ticketSheet').text(Math.ceil(this.count));
        //     }
        //   });
        //   price+=1;
        // });
        // $('#ticketQtyForm .iconMinus').click(function(){
        //   $({count: price}).animate({count: price-1}, {
        //     duration: 0,
        //     progress: function() {
        //         $('#ticketQtyForm #ticketSheet').text(Math.ceil(this.count));
        //     }
        //   });
        //   price-=1;
        // });
        //【旧】
        //	$(function(){
        //		var cnt = 1;
        //		function countUp(){
        //			cnt++;
        //			document.getElementById("ticketSheet").innerHTML=cnt;
        //		}
        //		function countDown(){
        //			cnt--;
        //			document.getElementById("ticketSheet").innerHTML=cnt;
        //		}
        //		window.onload = function(){
        //			document.getElementById("ticketSheet").innerHTML=cnt;
        //			document.ticketQtyForm.p_btn.onclick=countUp;
        //			document.ticketQtyForm.m_btn.onclick=countDown;
        //		};
        //	});
        //seat-listのボタンのtoggle
        __WEBPACK_IMPORTED_MODULE_3_jquery__(function () {
            __WEBPACK_IMPORTED_MODULE_3_jquery__(".acd dd").css("display", "none");
            __WEBPACK_IMPORTED_MODULE_3_jquery__("#mapAreaRight").on("click", ".acd dt", function () {
                __WEBPACK_IMPORTED_MODULE_3_jquery__(this).next("dd").slideToggle();
                __WEBPACK_IMPORTED_MODULE_3_jquery__(this).next("dd").parent().siblings().find("dd").slideUp();
                __WEBPACK_IMPORTED_MODULE_3_jquery__(this).toggleClass("open");
                __WEBPACK_IMPORTED_MODULE_3_jquery__(this).parent().siblings().find("dt").removeClass("open");
            });
        });
        //リサイズでリロード
        // $(function(){
        //   var timer;
        //   $(window).resize(function() {
        //   if (timer !== false) {
        //   clearTimeout(timer);
        //   }
        //   timer = setTimeout(function() {
        //   location.reload();
        //   }, 200);
        //   });
        // });
        __WEBPACK_IMPORTED_MODULE_3_jquery__(document).ready(function () {
            __WEBPACK_IMPORTED_MODULE_3_jquery__(".methodExplanation").hide();
            // show the info that is already clicked
            var clicked_item = __WEBPACK_IMPORTED_MODULE_3_jquery__("input[id^='radio']").filter(':checked');
            __WEBPACK_IMPORTED_MODULE_3_jquery__(clicked_item).parent().next().show();
            __WEBPACK_IMPORTED_MODULE_3_jquery__("dt.settlement-list").on('click', function (e) {
                e.preventDefault();
                var clicked_radio = __WEBPACK_IMPORTED_MODULE_3_jquery__(this).find("input[id^='radio']");
                var index = __WEBPACK_IMPORTED_MODULE_3_jquery__("input[id^='radio']").index(clicked_radio);
                var vis_item = __WEBPACK_IMPORTED_MODULE_3_jquery__(".methodExplanation:visible");
                // uncheck the radio and close the info block when it is clicked again
                if (__WEBPACK_IMPORTED_MODULE_3_jquery__(clicked_radio).is(':checked') && __WEBPACK_IMPORTED_MODULE_3_jquery__(this).next().is(':visible')) {
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(clicked_radio).prop('checked', false);
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(this).next().slideUp();
                }
                else {
                    var do_shift = false;
                    var shift = 0;
                    // decide whether the position setting needs to include the height of previous info block
                    if (__WEBPACK_IMPORTED_MODULE_3_jquery__(vis_item).length === 1) {
                        var vis_index = __WEBPACK_IMPORTED_MODULE_3_jquery__(".methodExplanation").index(__WEBPACK_IMPORTED_MODULE_3_jquery__(vis_item));
                        // if the index of visible item is less than that of the clicked item.
                        do_shift = vis_index < index;
                    }
                    // set the position to be shifted.
                    if (do_shift) {
                        var margin = +__WEBPACK_IMPORTED_MODULE_3_jquery__(vis_item).css('margin-top').replace("px", "");
                        margin += +__WEBPACK_IMPORTED_MODULE_3_jquery__(vis_item).css('margin-bottom').replace("px", "");
                        shift = __WEBPACK_IMPORTED_MODULE_3_jquery__(vis_item).height() + margin;
                    }
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(".methodExplanation").slideUp();
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(this).next().slideDown();
                    __WEBPACK_IMPORTED_MODULE_3_jquery__(clicked_radio).prop('checked', true);
                    // shift the position to show the info properly
                    __WEBPACK_IMPORTED_MODULE_3_jquery__('html, body').animate({
                        scrollTop: __WEBPACK_IMPORTED_MODULE_3_jquery__(this).offset().top - shift
                    });
                }
            });
        });
        //////////////////////////////////////////////////////////ここから上mainHeight.js
    };
    ReserveBySeatComponent.prototype.ngAfterViewInit = function () {
        //ローディング非表示
        this.loadingService.setValue(false);
    };
    ReserveBySeatComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-reserve-by-seat',
            template: __webpack_require__("../../../../../src/app/reserve-by-seat/reserve-by-seat.component.html"),
            styles: [__webpack_require__("../../../../../src/app/reserve-by-seat/reserve-by-seat.component.css")]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__["LoadingAnimateService"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2_ng2_loading_animate__["LoadingAnimateService"]) === 'function' && _b) || Object])
    ], ReserveBySeatComponent);
    return ReserveBySeatComponent;
    var _a, _b;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/reserve-by-seat.component.js.map

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/seat-list/seat-list.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/seat-list/seat-list.component.html":
/***/ (function(module, exports) {

module.exports = "<div id=\"choiceSeatArea\" class=\"choiceSeatArea\" *ngIf=\"seatListDisply\">\r\n    <p class=\"choiceSeatTtl\">席種を選択</p>\r\n    <dl class=\"acd\">\r\n        <div *ngIf=\"searchResultFlag\">条件に一致するチケットがありませんでした。</div>\r\n        <div *ngFor=\"let stockType of makeStockTypes\">\r\n            <dt><span class=\"{{stockStatus(stockType.stock_status)}}\"><span></span></span><div class=\"listText\">{{stockType.stock_type_name}}</div></dt>\r\n                <dd style=\"display:none\">\r\n                    <div *ngIf=\"stockType.is_quantity_only\" class=\"buy\"><button class=\"\" type=\"button\" (click)=\"onAutoClick(stockType.stock_type_id)\">この席種を購入</button></div>\r\n                    <div *ngIf=\"!stockType.is_quantity_only\"><button class=\"\" type=\"button\" (click)=\"onSelectClick(stockType.stock_type_name)\">座席を選んで購入</button><button class=\"\" type=\"button\" (click)=\"onAutoClick(stockType.stock_type_id)\">おまかせで購入</button></div>\r\n                </dd>\r\n        </div>\r\n    </dl>\r\n</div>"

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/seat-list/seat-list.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return SeatlistComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__reserve_by_seat_filter_filter_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/filter/filter.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__reserve_by_quantity_reserve_by_quantity_component__ = __webpack_require__("../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__reserve_by_seat_venue_map_venue_map_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__shared_services_stock_type_data_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-type-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6_jquery__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};







var SeatlistComponent = (function () {
    function SeatlistComponent(route, reserveByQuantity, stockTypeDataService, Venuemap) {
        this.route = route;
        this.reserveByQuantity = reserveByQuantity;
        this.stockTypeDataService = stockTypeDataService;
        this.Venuemap = Venuemap;
        this.mapHome = new __WEBPACK_IMPORTED_MODULE_0__angular_core__["EventEmitter"]();
        this.confirmStockType = new __WEBPACK_IMPORTED_MODULE_0__angular_core__["EventEmitter"]();
        this.stockTypeIdFromList = new __WEBPACK_IMPORTED_MODULE_0__angular_core__["EventEmitter"]();
        //seatList表示・非表示フラグ
        this.seatListDisply = true;
        //検索結果フラグ
        this.searchResultFlag = false;
    }
    //公演情報・席種情報取得
    SeatlistComponent.prototype.ngOnInit = function () {
        var _this = this;
        this.stockTypeDataService.toSeatListFlag$.subscribe(function (flag) {
            _this.seatListDisply = flag;
        });
        var that = this;
        var performanceRes = this.route.snapshot.data['performance'];
        this.stockTypesRes = this.route.snapshot.data['stockTypes'];
        this.stockTypes = this.stockTypesRes.data.stock_types;
        this.performance = performanceRes.data.performance;
        this.filterComponent.searched$.subscribe(function (response) {
            that.searchResultFlag = false;
            var divideStockTypes = _this.divideList(response.data.stock_types);
            _this.makeStockTypes = _this.sortList(divideStockTypes, that.stockTypes);
            //検索結果フラグ
            if (_this.makeStockTypes.length == 0) {
                that.searchResultFlag = true;
            }
        });
    };
    //自由席と指定席を内部構造でより分ける
    SeatlistComponent.prototype.divideList = function (response) {
        var _this = this;
        var divideStockTypes;
        divideStockTypes = [];
        response.forEach(function (value, key) {
            if (value.is_quantity_only) {
                if (_this.filterComponent.unreserved) {
                    divideStockTypes.push(value);
                }
            }
            else {
                if (_this.filterComponent.reserved) {
                    divideStockTypes.push(value);
                }
            }
        });
        return divideStockTypes;
    };
    //席種情報検索のレスポンスと同じ順番に変更
    SeatlistComponent.prototype.sortList = function (divideStockTypes, stockTypes) {
        var sortStockTypes;
        sortStockTypes = [];
        for (var i = 0, len = stockTypes.length; i < len; i++) {
            for (var l = 0, dlen = divideStockTypes.length; l < dlen; l++)
                if (stockTypes[i].stock_type_id == divideStockTypes[l].stock_type_id) {
                    sortStockTypes.push(divideStockTypes[l]);
                }
        }
        return sortStockTypes;
    };
    //statusに合わせたクラス名を返す
    SeatlistComponent.prototype.stockStatus = function (status) {
        switch (status) {
            case '◎': return 'circleW';
            case '△': return 'triangle';
            case '×': return 'close';
            default: return 'unknown';
        }
    };
    //おまかせで購入を選択
    SeatlistComponent.prototype.onAutoClick = function (stockTypeId) {
        __WEBPACK_IMPORTED_MODULE_6_jquery__('html').css({
            'height': "",
            'overflow-y': "hidden"
        });
        __WEBPACK_IMPORTED_MODULE_6_jquery__('body').css({
            'height': "",
            'overflow-y': "auto"
        });
        if (this.countSelect == 0) {
            this.stockTypeDataService.sendToQuentity(stockTypeId);
            this.stockTypeId = stockTypeId;
        }
        else {
            this.confirmStockType.emit(true);
            this.stockTypeIdFromList.emit(stockTypeId);
        }
    };
    //座席を選んで購入を選択
    SeatlistComponent.prototype.onSelectClick = function (stockTypeName) {
        this.filterComponent.selectSeatSearch(stockTypeName);
        this.mapHome.emit();
    };
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', (typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */]) === 'function' && _a) || Object)
    ], SeatlistComponent.prototype, "filterComponent", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', Number)
    ], SeatlistComponent.prototype, "countSelect", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_2__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */]) === 'function' && _b) || Object)
    ], SeatlistComponent.prototype, "reserveByQuantityComponent", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Output"])(), 
        __metadata('design:type', Object)
    ], SeatlistComponent.prototype, "mapHome", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Output"])(), 
        __metadata('design:type', Object)
    ], SeatlistComponent.prototype, "confirmStockType", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Output"])(), 
        __metadata('design:type', Object)
    ], SeatlistComponent.prototype, "stockTypeIdFromList", void 0);
    SeatlistComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            providers: [__WEBPACK_IMPORTED_MODULE_1__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */], __WEBPACK_IMPORTED_MODULE_2__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */], __WEBPACK_IMPORTED_MODULE_3__reserve_by_seat_venue_map_venue_map_component__["a" /* VenuemapComponent */]],
            selector: 'app-seat-list',
            template: __webpack_require__("../../../../../src/app/reserve-by-seat/seat-list/seat-list.component.html"),
            styles: [__webpack_require__("../../../../../src/app/reserve-by-seat/seat-list/seat-list.component.css")]
        }), 
        __metadata('design:paramtypes', [(typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_5__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5__angular_router__["ActivatedRoute"]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_2__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */]) === 'function' && _d) || Object, (typeof (_e = typeof __WEBPACK_IMPORTED_MODULE_4__shared_services_stock_type_data_service__["a" /* StockTypeDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__shared_services_stock_type_data_service__["a" /* StockTypeDataService */]) === 'function' && _e) || Object, (typeof (_f = typeof __WEBPACK_IMPORTED_MODULE_3__reserve_by_seat_venue_map_venue_map_component__["a" /* VenuemapComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__reserve_by_seat_venue_map_venue_map_component__["a" /* VenuemapComponent */]) === 'function' && _f) || Object])
    ], SeatlistComponent);
    return SeatlistComponent;
    var _a, _b, _c, _d, _e, _f;
}());
;
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/seat-list.component.js.map

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.html":
/***/ (function(module, exports) {

module.exports = "<div id=\"mapAreaLeft\">\r\n    <!--  venue-map   -->\r\n    <div id=\"mapImgBox\" [inlineSVG]=\"venueURL\" alt=\"\"></div>\r\n    <div class=\"mapBtnBox\">\r\n        <button id=\"mapBtnHome\" class=\"mapBtnHome\" type=\"button\"><span></span></button>\r\n        <div class=\"mapZoomBtnBox\">\r\n            <button id=\"mapBtnPlus\" class=\"mapBtnPlus\" type=\"button\"><span></span></button>\r\n            <button id=\"mapBtnMinus\" class=\"mapBtnMinus\" type=\"button\"><span></span></button>\r\n        </div>\r\n    </div>\r\n\r\n    <div class=\"mapNaviBox\" *ngIf=\"wholemapFlag\">\r\n        <div id=\"mapImgBoxS\" [inlineSVG]=\"wholemapURL\" alt=\"\" style=\"height:auto;\"></div>\r\n    </div>\r\n    <!--  /venue-map   -->\r\n</div>\r\n    <div id=\"colorNavi\" [inlineSVG]=\"colorNavi\" alt=\"\"></div>\r\n<!--エラーモーダル-->\r\n<div id=\"modalWindowAlertBox\" class=\"modalWindowAlertBox\" *ngIf=\"confirmStockType\">\r\n    <div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\r\n        <div id=\"modalWindowAlert\" class=\"modalWindowAlert\">\r\n            <div class=\"modalInner\">\r\n                <div class=\"modalAlert\">\r\n                    <p class=\"modalAlertTtl\"><span></span>確認</p>\r\n                    <p>{{confirmationMassage}}</p>\r\n                        <button id=\"cancelbtn\" type=\"button\" (click)=\"removeConfirmation()\">いいえ</button>\r\n                        <button id=\"okbtn\" type=\"button\" (click)=\"removeSeatList()\">はい</button>\r\n                </div>\r\n            </div>\r\n        </div>\r\n    </div>\r\n</div>\r\n<!--/エラーモーダル-->\r\n\r\n<!--横画面エラーモーダル-->\r\n<div id=\"modalWindowErrorBox\" class=\"modalWindowAlertBox noScroll\" *ngIf=\"sideProhibition\">\r\n    <div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\r\n        <div id=\"modalWindowAlert\" class=\"modalWindowAlert\">\r\n            <div class=\"modalInner\">\r\n              <div class=\"modalAlert\">\r\n                    <p class=\"modalAlertTtl\"><span></span>お願い</p>\r\n                    <p class=\"modalAlertText\">縦向きでご使用ください</p>\r\n                </div>\r\n            </div>\r\n        </div>\r\n    </div>\r\n</div>\r\n<!--/横画面エラーモーダル-->\r\n\r\n<!--席種詳細モーダル-->\r\n<div id=\"modalWindowStockTypeAlertBox\" class=\"modalWindowAlertBox\" *ngIf=\"displayDetail\">\r\n    <div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\r\n        <div id=\"modalWindow\" class=\"modalWindow\">\r\n            <div class=\"modalInner\">\r\n                <div class=\"closeBtnBox\" (click)=\"removeModalWindow()\"><span class=\"closeBtn\"></span></div>\r\n                <p class=\"seatName\">{{selectedStockTypeName}}</p>\r\n                <div [innerHTML]=\"selectedDescription\"></div>\r\n                <div class=\"seatPriceBox\" *ngFor=\"let value of selectedProducts\">\r\n                    <p class=\"seatPrice\"><span>{{value.product_name}}</span><span>￥{{value.price}}</span></p>\r\n                </div>\r\n                <div class=\"modalBtnBox\">\r\n                    <button class=\"\" type=\"button\" (click)=\"removeDialog()\">キャンセル</button><button class=\"\" type=\"button\" (click)=\"addSeatList()\">OK</button>\r\n                </div>\r\n            </div>\r\n        </div>\r\n    </div>\r\n</div>\r\n<!--/席種詳細モーダル-->\r\n\r\n<!--枚数選択モーダル-->\r\n    <app-reserve-by-quantity #quantity [filterComponent]=\"filterComponent\" [display]=\"display\" (output)=\"display = $event\" (confirmStockType)=\"confirmStockType = $event\"></app-reserve-by-quantity>\r\n<!--/枚数選択モーダル-->\r\n<div id=\"mapAreaRight\">\r\n\r\n    <!--  seat-list   -->\r\n    <app-seat-list [reserveByQuantityComponent]=\"quantity\" [filterComponent]=\"filterComponent\" [countSelect]=\"countSelect\" (confirmStockType)=\"confirmStockType = $event\" (mapHome)=\"mapHome()\" (stockTypeIdFromList)=\"stockTypeIdFromList = $event\"></app-seat-list>\r\n    <!--  /seat-list   -->\r\n\r\n    <!--購入確認-->\r\n    <div id=\"buyChoiceSeatArea\" *ngIf=\"ticketDetail\">\r\n        <p class=\"buyChoiceSeatTtl pc\"><span>購入確認</span></p>\r\n        <div class=\"buyChoiceSeatBox\">\r\n            <div class=\"seatNumberBox\">\r\n            <div class=\"seatNumber\" *ngFor=\"let value of selectedSeatNameList\" (click)=\"showDialog(value)\">\r\n                <div class=\"closeBtnBox\"><span class=\"closeBtn\" (click)=\"removeSeatListFromBtn(value, $event)\"></span></div>\r\n                <p>{{value}}</p>\r\n            </div>\r\n            </div>\r\n            <div class=\"selectBoxBtn cf\">\r\n            <div class=\"closeBtnBox {{active}}\"><span class=\"closeBtn\"></span></div>\r\n            <p><span>{{stockTypeName}}</span>&nbsp;<span>{{countSelect}}枚</span></p>\r\n            </div>\r\n        </div>\r\n        <div class=\"buttonBox\">\r\n            <button class=\"clear\" type=\"button\" name=\"\" value=\"選択中の座席をクリア\" form=\"buySeatForm\" (click)=\"seatClearClick()\">選択中の座席をクリア</button>\r\n            <button class=\"reserve\" type=\"button\" name=\"\" value=\"次へ\" form=\"buySeatForm\" (click)=\"seatReserveClick()\">次へ</button>\r\n        </div>\r\n    </div>\r\n    <!--/購入確認-->\r\n</div>"

/***/ }),

/***/ "../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return VenuemapComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__reserve_by_seat_filter_filter_component__ = __webpack_require__("../../../../../src/app/reserve-by-seat/filter/filter.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__ = __webpack_require__("../../../../../src/app/reserve-by-quantity/reserve-by-quantity.component.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__shared_services_performances_service__ = __webpack_require__("../../../../../src/app/shared/services/performances.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__shared_services_seat_status_service__ = __webpack_require__("../../../../../src/app/shared/services/seat-status.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__shared_services_stock_types_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__shared_services_quentity_check_service__ = __webpack_require__("../../../../../src/app/shared/services/quentity-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__shared_services_stock_type_data_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-type-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__shared_services_error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10__shared_services_animation_enable_service__ = __webpack_require__("../../../../../src/app/shared/services/animation-enable.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11__shared_services_count_select_service__ = __webpack_require__("../../../../../src/app/shared/services/count-select.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_12__shared_services_smartPhone_check_service__ = __webpack_require__("../../../../../src/app/shared/services/smartPhone-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_13_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_14_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_14_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_14_angular2_logger_core__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_15__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};














// hammer
__webpack_require__("../../../../jquery-hammerjs/jquery.hammer.js");


var SEAT_COLOR_AVAILABLE = 'rgb(0, 128, 255)';
var SEAT_COLOR_SELECTED = 'rgb(236, 13, 80)';
var SEAT_COLOR_NA = 'rgb(128, 128, 128)';
var REGION_COLOR_NA = 'rgb(128, 128, 128)';
var REGION_COLOR_FEW_SEATS = 'rgb(76, 195, 255)';
var REGION_COLOR_MANY_SEATS = 'rgb(0, 0, 255)';
var STOCK_STATUS_MANY = "◎";
var STOCK_STATUS_FEW = "△";
var SCALE_SEAT = 1.0; // 表示倍率2倍個席表示
var SCALE_MAX = 5.0; // 表示倍率の最大値
var WINDOW_SM = 768; // スマホか否かの判定に用いる
var SIDE_HEIGHT = 200; //横画面時エラーを出す最大値
var MAX_QUANTITY_DEFAULT = 10; // デフォルトの選択可能枚数
var VenuemapComponent = (function () {
    function VenuemapComponent(el, route, performances, seatStatus, stockTypes, QuentityChecks, router, reserveByQuantity, stockTypeDataService, errorModalDataService, animationEnableService, countSelectService, smartPhoneCheckService, _logger) {
        this.el = el;
        this.route = route;
        this.performances = performances;
        this.seatStatus = seatStatus;
        this.stockTypes = stockTypes;
        this.QuentityChecks = QuentityChecks;
        this.router = router;
        this.reserveByQuantity = reserveByQuantity;
        this.stockTypeDataService = stockTypeDataService;
        this.errorModalDataService = errorModalDataService;
        this.animationEnableService = animationEnableService;
        this.countSelectService = countSelectService;
        this.smartPhoneCheckService = smartPhoneCheckService;
        this._logger = _logger;
        this.display = false;
        // 説明
        this.description = '';
        // 選択した座席の説明
        this.selectedDescription = '';
        // 会場図グリッドサイズ
        this.venueGridSize = 100;
        // 詳細表示フラグ
        this.displayDetail = false;
        // 選択した座席情報フラグ
        this.ticketDetail = false;
        // ミニマップの表示フラグ
        this.wholemapFlag = false;
        // 同一席種かどうかのフラグ
        this.sameStockType = true;
        // 選択した座席リストの+-を切り替えるクラス
        this.active = 'active';
        // カート破棄のダイアログを表示するフラグ
        this.confirmStockType = false;
        // 選択した座席のid
        this.selectedSeatId = null;
        // 選択した座席とそれに紐づくid
        this.selectedGroupIds = [];
        // 選択した座席の座席名
        this.selectedSeatName = null;
        // 選択した座席の座席名
        this.selectedSeatGroupNames = [];
        // 選択した座席の席種id
        this.selectedStockTypeId = null;
        // 選択した席種の最大購入数
        this.selectedStockTypeMaxQuantity = null;
        // 選択した席種の最小購入数
        this.selectedStockTypeMinQuantity = null;
        // 選択した座席リスト
        this.selectedSeatList = [];
        // 選択した座席の座席名リスト
        this.selectedSeatNameList = [];
        // 選択した回数
        this.countSelect = 0;
        // カート破棄確認メッセージ
        this.confirmationMassage = 'こちらは選択中の座席の席種とは異なりますが、選択中の座席をキャンセルしてこちらの座席を選択しますか？';
        // 1つ前に選択した座席id
        this.prevSeatId = null;
        // 1つ前に選択した席種
        this.prevStockType = null;
        // 選択したブロックのid
        this.selectedRegionId = null;
        // 数受けの席種Id
        this.quantityStockTypeIds = [];
        // 席種Id+regionIds
        this.stockTypeRegionIds = {};
        // 座席選択POST初期データ
        this.data = {
            'reserve_type': 'seat_choise',
            'selected_seats': []
        };
        // 全体の拡大縮小率
        this.scaleTotal = 1.0;
        // regionId（数受けの席のregion Id）
        this.regionIds = [];
        // viewBoxの初期値を格納
        this.originalViewBox = null;
        // ドラッグ（スワイプ）フラグ
        this.panFlag = false;
        // touchとclickを同時に発生させないため
        this.touchFlag = false;
        // pinch時のフラグ
        this.pinchFlag = false;
        // pinchスケール
        this.pinchScale = 1;
        // 表示領域のaspect比に対応するviewBox
        this.displayViewBox = null;
        // 座席Element情報
        this.seat_elements = {};
        // 表示中のグリッド
        this.active_grid = [];
        //横画面表示エラーモーダルフラグ
        this.sideProhibition = false;
        //選択単位フラグ 1席ずつ:true/2席以上ずつ:false
        this.isGroupedSeats = true;
        //最終座席情報検索呼び出しチェック状態
        this.reservedFlag = true;
        this.unreservedFlag = true;
        this.element = this.el.nativeElement;
    }
    VenuemapComponent.prototype.ngOnInit = function () {
        var _this = this;
        var that = this;
        var drawingRegionTimer;
        var drawingSeatTimer;
        var regionIds = Array();
        this.animationEnableService.sendToRoadFlag(true);
        // 公演情報
        var performanceRes = this.route.snapshot.data['performance'];
        this.event = performanceRes.data.event;
        this.performance = performanceRes.data.performance;
        this.performanceId = this.performance.performance_id;
        this.venueURL = this.performance.venue_map_url;
        this.colorNavi = "https://s3-ap-northeast-1.amazonaws.com/tstar/cart_api/color_sample.svg";
        this.wholemapURL = this.performance.mini_venue_map_url;
        this.salesSegments = this.performance.sales_segments;
        var selesSegmentId = this.salesSegments[0].sales_segment_id;
        // 席種情報検索
        var response = this.route.snapshot.data['stockTypes'];
        this._logger.debug("get stock types success", response);
        this.stockType = response.data.stock_types;
        this.stockTypeRes = response.data.stock_types;
        this.stockTypes.getStockTypesAll(this.performanceId, selesSegmentId)
            .subscribe(function (response) {
            _this._logger.debug("get StockTypesAll(#" + _this.performanceId + ") success", response);
            var stockTypes = response.data.stock_types;
            for (var i = 0, len = stockTypes.length; i < len; i++) {
                if (stockTypes[i].is_quantity_only) {
                    var regions = stockTypes[i].regions;
                    var stockTypeId = stockTypes[i].stock_type_id;
                    if (regions.length > 0) {
                        that.stockTypeRegionIds[stockTypeId] = regions;
                        Array.prototype.push.apply(_this.regionIds, regions);
                    }
                }
            }
            (function (error) {
                _this._logger.error('[VenueMapComponent]getStockType error', error);
                if (error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                    _this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
                }
            });
        });
        this.filterComponent.searched$.subscribe(function (response) {
            that.seatGroups = response.data.seat_groups;
            that.regions = response.data.regions;
            that.seats = response.data.seats;
            _this.reservedFlag = _this.filterComponent.reserved;
            _this.unreservedFlag = _this.filterComponent.unreserved;
            var drawingRegions = [];
            var drawingRegionIds = [];
            // フィルタで指定席がONの場合の色付け対象region設定
            if (_this.reservedFlag) {
                for (var i = 0, len = that.regions.length; i < len; i++) {
                    for (var j = 0, fLen = _this.filterComponent.reservedRegionIds.length; j < fLen; j++) {
                        if (that.regions[i].region_id == _this.filterComponent.reservedRegionIds[j]) {
                            var seatRegion = { 'region_id': '', 'stock_status': '' };
                            seatRegion.region_id = that.regions[i].region_id;
                            seatRegion.stock_status = that.regions[i].stock_status;
                            drawingRegions.push(seatRegion);
                        }
                    }
                }
            }
            // フィルタで自由席がONの場合の色付け対象region設定
            if (_this.unreservedFlag) {
                for (var i = 0, len = that.regions.length; i < len; i++) {
                    for (var j = 0, fLen = _this.filterComponent.unreservedRegionIds.length; j < fLen; j++) {
                        if (that.regions[i].region_id == _this.filterComponent.unreservedRegionIds[j]) {
                            var seatRegion = { 'region_id': '', 'stock_status': '' };
                            seatRegion.region_id = that.regions[i].region_id;
                            seatRegion.stock_status = that.regions[i].stock_status;
                            drawingRegions.push(seatRegion);
                        }
                    }
                }
            }
            // regionの色付け開始
            startDrawingRegionTimer(drawingRegions);
            function startDrawingRegionTimer(regions) {
                drawingRegionTimer = setInterval(function () {
                    if (that.svgMap) {
                        clearInterval(drawingRegionTimer);
                        __WEBPACK_IMPORTED_MODULE_13_jquery__(that.svgMap).find('.region').css({ 'fill': REGION_COLOR_NA });
                        __WEBPACK_IMPORTED_MODULE_13_jquery__(that.svgMap).find('.coloring_region').css({ 'fill': REGION_COLOR_NA });
                        for (var i = 0, len = regions.length; i < len; i++) {
                            if (regions[i].stock_status == '△') {
                                __WEBPACK_IMPORTED_MODULE_13_jquery__(that.svgMap).find('#' + regions[i].region_id).css({ 'fill': REGION_COLOR_FEW_SEATS });
                                __WEBPACK_IMPORTED_MODULE_13_jquery__(that.svgMap).find('#' + regions[i].region_id).find('.coloring_region').css({ 'fill': REGION_COLOR_FEW_SEATS });
                            }
                            else if (regions[i].stock_status == '◎') {
                                __WEBPACK_IMPORTED_MODULE_13_jquery__(that.svgMap).find('#' + regions[i].region_id).css({ 'fill': REGION_COLOR_MANY_SEATS });
                                __WEBPACK_IMPORTED_MODULE_13_jquery__(that.svgMap).find('#' + regions[i].region_id).find('.coloring_region').css({ 'fill': REGION_COLOR_MANY_SEATS });
                            }
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
        // SVGのロード完了チェック+各領域のheight取得
        var svgLoadCompleteTimer = setInterval(function () {
            that.originalViewBox = that.getPresentViewBox();
            // 元のviewBoxが取得でき，かつreserve-by-seat.componentの高さ設定値が取得できたら
            if ((that.originalViewBox) && (that.mapAreaLeftH != 0)) {
                clearInterval(svgLoadCompleteTimer);
                that.seatAreaHeight = __WEBPACK_IMPORTED_MODULE_13_jquery__("#mapImgBox").height();
                that.svgMap = document.getElementById('mapImgBox').firstElementChild;
                that.saveSeatData();
                that.mapHome();
            }
        }, 200);
    };
    VenuemapComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        var FastClick = __webpack_require__("../../../../fastclick/lib/fastclick.js");
        FastClick.attach(document.body);
        // ホームボタン
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapBtnHome').on('mousedown touchstart', function (event) {
            if (_this.originalViewBox && _this.seats) {
                _this.touchFlag = true;
                event.preventDefault();
            }
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapBtnHome').on('mouseup touchend', function (event) {
            if (_this.originalViewBox && _this.seats) {
                if (_this.touchFlag)
                    _this.mapHome();
                _this.touchFlag = false;
                event.preventDefault();
            }
        });
        // 拡大ボタン
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapBtnPlus').on('mousedown touchstart', function (event) {
            if (_this.originalViewBox && _this.seats) {
                _this.touchFlag = true;
                event.preventDefault();
            }
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapBtnPlus').on('mouseup touchend', function (event) {
            if (_this.originalViewBox && _this.seats) {
                if (_this.touchFlag)
                    _this.enlargeMap();
                _this.touchFlag = false;
                event.preventDefault();
            }
        });
        // 縮小ボタン
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapBtnMinus').on('mousedown touchstart', function (event) {
            if (_this.originalViewBox && _this.seats) {
                _this.touchFlag = true;
                event.preventDefault();
            }
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapBtnMinus').on('mouseup touchend', function (event) {
            if (_this.originalViewBox && _this.seats) {
                if (_this.touchFlag)
                    _this.shrinkMap();
                _this.touchFlag = false;
                event.preventDefault();
            }
        });
        // ブロック・座席のタップ
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').on('mousedown touchstart', function (event) {
            if (_this.originalViewBox && _this.seats) {
                _this.touchFlag = true;
                event.preventDefault();
            }
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').on('mouseup touchend', function (event) {
            if (_this.originalViewBox && _this.seats) {
                if (_this.touchFlag) {
                    if (__WEBPACK_IMPORTED_MODULE_13_jquery__(event.target).hasClass('region') || __WEBPACK_IMPORTED_MODULE_13_jquery__(event.target).parents().hasClass('region')) {
                        _this.tapRegion(event);
                    }
                    else if (__WEBPACK_IMPORTED_MODULE_13_jquery__(event.target).hasClass('seat')) {
                        _this.tapSeat(event);
                    }
                }
                _this.touchFlag = false;
                event.preventDefault();
            }
        });
        var gestureObj = new Hammer(__WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox')[0]);
        gestureObj.get('pan').set({ enable: true, threshold: 0, direction: Hammer.DIRECTION_ALL });
        gestureObj.get('pinch').set({ enable: true });
        // パン操作
        gestureObj.on('panstart panmove panend', function (event) {
            if (_this.originalViewBox && _this.seats) {
                var venueObj = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox');
                var x = void 0, y = void 0, viewBoxVals = void 0;
                var offsetX = venueObj.offset().left;
                var offsetY = venueObj.offset().top;
                var x_pos = event.center.x - offsetX;
                var y_pos = event.center.y - offsetY;
                switch (event.type) {
                    case 'panstart':
                        _this.originalX = event.deltaX;
                        _this.originalY = event.deltaY;
                        _this.panFlag = true;
                        break;
                    case 'panmove':
                        if (_this.panFlag) {
                            x = event.deltaX - _this.originalX;
                            y = event.deltaY - _this.originalY;
                            viewBoxVals = _this.getDragViewBox(-x, -y);
                            venueObj.children().attr('viewBox', viewBoxVals.join(' ')); // set the viewBox
                            _this.originalX = event.deltaX;
                            _this.originalY = event.deltaY;
                            if (x_pos < 0 || x_pos > _this.D_Width) {
                                _this.panFlag = false;
                            }
                            if (y_pos < 0 || y_pos > _this.D_Height) {
                                _this.panFlag = false;
                            }
                        }
                        _this.touchFlag = false;
                        break;
                    case 'panend':
                        _this.panFlag = false;
                        _this.setActiveGrid();
                        break;
                }
            }
        });
        // ピンチ操作
        gestureObj.on('pinchstart pinchmove pinchend', function (event) {
            if (_this.originalViewBox && _this.seats) {
                var viewBoxVals = void 0;
                var venueObj = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox');
                var offsetX = venueObj.offset().left;
                var offsetY = venueObj.offset().top;
                var x = event.center.x - offsetX;
                var y = event.center.y - offsetY;
                var scale = void 0;
                switch (event.type) {
                    case 'pinchstart':
                        _this.pinchFlag = true;
                        _this.pinchScale = event.scale;
                        break;
                    case 'pinchmove':
                        if (_this.pinchFlag) {
                            scale = (event.scale - _this.pinchScale) + 1;
                            viewBoxVals = _this.getZoomViewBox(x, y, 1 / scale);
                            _this.scaleTotal = _this.getPresentScale(viewBoxVals);
                            if (_this.scaleTotal > SCALE_MAX) {
                                scale = _this.scaleTotal / SCALE_MAX * (1 / scale);
                                _this.scaleTotal = SCALE_MAX;
                                viewBoxVals = _this.getZoomViewBox(x, y, scale);
                            }
                            else {
                                if (_this.scaleTotal < _this.SCALE_MIN) {
                                    _this.mapHome();
                                    return;
                                }
                            }
                            venueObj.children().attr('viewBox', viewBoxVals.join(' '));
                            if (_this.scaleTotal >= SCALE_SEAT && !(_this.wholemapFlag)) {
                                if ((__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() <= WINDOW_SM) || (_this.countSelect != 0)) {
                                    _this.stockTypeDataService.sendToSeatListFlag(false);
                                    _this.seatSelectDisplay(false);
                                }
                                _this.wholemapFlag = true;
                                _this.onoffRegion(_this.regionIds);
                            }
                            else {
                                if (_this.scaleTotal < SCALE_SEAT) {
                                    _this.onoffRegion(_this.regionIds);
                                    if (_this.countSelect == 0) {
                                        _this.stockTypeDataService.sendToSeatListFlag(true);
                                        _this.seatSelectDisplay(true);
                                    }
                                    _this.wholemapFlag = false;
                                }
                            }
                        }
                        _this.pinchScale = event.scale;
                        _this.touchFlag = false;
                        break;
                    case 'pinchend':
                        _this.pinchFlag = false;
                        _this.pinchScale = 1;
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
        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').bind('mousewheel DOMMouseScroll', function (e) {
            if (_this.originalViewBox && _this.seats) {
                var viewBoxVals = void 0;
                var offsetX = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').offset().left;
                var offsetY = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').offset().top;
                var x = e.pageX - offsetX;
                var y = e.pageY - offsetY;
                var scale = void 0;
                var d = extractDelta(e);
                var venueObj = __WEBPACK_IMPORTED_MODULE_13_jquery__(document).find('#mapImgBox');
                if (d > 0) {
                    scale = 0.8;
                    viewBoxVals = _this.getZoomViewBox(x, y, scale);
                    _this.scaleTotal = _this.getPresentScale(viewBoxVals);
                    if (_this.scaleTotal > SCALE_MAX) {
                        if (_this.scaleTotal == SCALE_MAX) {
                            return;
                        }
                        else {
                            scale = _this.scaleTotal / SCALE_MAX * scale;
                            _this.scaleTotal = SCALE_MAX;
                            viewBoxVals = _this.getZoomViewBox(x, y, scale);
                        }
                    }
                    venueObj.children().attr('viewBox', viewBoxVals.join(' '));
                    if (_this.scaleTotal >= SCALE_SEAT && !(_this.wholemapFlag)) {
                        if ((__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() <= WINDOW_SM) || (_this.countSelect != 0)) {
                            _this.stockTypeDataService.sendToSeatListFlag(false);
                            _this.seatSelectDisplay(false);
                        }
                        _this.wholemapFlag = true;
                        _this.onoffRegion(_this.regionIds);
                    }
                }
                else {
                    scale = 1.2;
                    viewBoxVals = _this.getZoomViewBox(x, y, scale);
                    _this.scaleTotal = _this.getPresentScale(viewBoxVals);
                    if (_this.scaleTotal < _this.SCALE_MIN) {
                        _this.mapHome();
                        return;
                    }
                    venueObj.children().attr('viewBox', viewBoxVals.join(' '));
                    if (_this.scaleTotal < SCALE_SEAT) {
                        _this.onoffRegion(_this.regionIds);
                        if (_this.countSelect == 0) {
                            _this.stockTypeDataService.sendToSeatListFlag(true);
                            _this.seatSelectDisplay(true);
                        }
                        _this.wholemapFlag = false;
                    }
                }
                e.stopPropagation();
                e.preventDefault();
            }
            e.stopPropagation();
            e.preventDefault();
        });
        // リサイズ処理
        var getHightTimer = null;
        var resizeTimer = null;
        var orientation = window.orientation;
        var that = this;
        //初期表示時横の場合
        getHightTimer = setInterval(function () {
            that.seatAreaHeight = __WEBPACK_IMPORTED_MODULE_13_jquery__("#mapImgBox").height();
            if (that.seatAreaHeight > 0) {
                that.sideError();
                clearTimeout(getHightTimer);
            }
            else if (that.seatAreaHeight == 0 && orientation == 90 || orientation == -90 && _this.smartPhoneCheckService.isSmartPhone()) {
                that.sideError();
                clearTimeout(getHightTimer);
            }
        }, 100);
        __WEBPACK_IMPORTED_MODULE_13_jquery__(window).resize(function () {
            if (resizeTimer !== false) {
                clearTimeout(resizeTimer);
            }
            resizeTimer = setTimeout(function () {
                _this.seatAreaHeight = __WEBPACK_IMPORTED_MODULE_13_jquery__("#mapImgBox").height();
                _this.sideError();
                if (that.originalViewBox && that.mapAreaLeftH != 0) {
                    _this.mapHome();
                }
            }, 100);
        });
    };
    VenuemapComponent.prototype.sideError = function () {
        var orientation = window.orientation;
        if (this.seatAreaHeight < SIDE_HEIGHT && orientation == 90 || orientation == -90) {
            this.sideProhibition = true;
            this.resizeCssTrue();
        }
        else {
            this.resizeCssFalse();
        }
    };
    VenuemapComponent.prototype.resizeCssTrue = function () {
        __WEBPACK_IMPORTED_MODULE_13_jquery__('html').css({
            'height': "",
            'overflow-y': ""
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('.choiceArea').css({
            'display': 'none'
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('html,body').css({
            'width': '100%',
            'height': '100%',
            'overflow-y': 'hidden'
        });
    };
    VenuemapComponent.prototype.resizeCssFalse = function () {
        this.sideProhibition = false;
        //スクロール解除
        __WEBPACK_IMPORTED_MODULE_13_jquery__('html').css({
            'height': "100%",
            'overflow-y': "hidden"
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('body').css({
            'height': "100%",
            'overflow-y': "auto"
        });
        __WEBPACK_IMPORTED_MODULE_13_jquery__('.choiceArea').css({
            'display': 'block'
        });
    };
    // ブロックのタップ操作
    VenuemapComponent.prototype.tapRegion = function (e) {
        var selectedRegionId = null;
        if (e.target.id && __WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).hasClass('region')) {
            selectedRegionId = e.target.id;
        }
        else if (__WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).parents().hasClass('region')) {
            selectedRegionId = __WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).parents('.region')[0].id;
        }
        else {
            return;
        }
        if (stockStatusCheck(selectedRegionId, this.regions)) {
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](selectedRegionId, this.regionIds) != -1) {
                // regionIdsを回し、選んだregionIdと同じなら遷移
                for (var x in this.stockTypeRegionIds) {
                    for (var i = 0, len = this.stockTypeRegionIds[x][i].length; i < len; i++) {
                        if (this.stockTypeRegionIds[x][i] === selectedRegionId) {
                            __WEBPACK_IMPORTED_MODULE_13_jquery__('html,body').css({
                                'height': "",
                                'overflow-y': ""
                            });
                            this.stockTypeDataService.sendToQuentity(+x);
                        }
                    }
                }
                this.countSelectService.sendToQuentity(this.countSelect);
            }
            else {
                var scale = this.scaleTotal / SCALE_SEAT; // 1辺の長さの拡大率
                this.scaleTotal = SCALE_SEAT;
                var x_pos = getPositionX(e);
                var y_pos = getPositionY(e);
                var viewBoxVals = this.getZoomViewBox(x_pos, y_pos, scale);
                __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').children().attr('viewBox', viewBoxVals.join(' '));
                if ((__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() <= WINDOW_SM) || (this.countSelect != 0)) {
                    this.stockTypeDataService.sendToSeatListFlag(false);
                    this.seatSelectDisplay(false);
                }
                this.wholemapFlag = true;
                this.onoffRegion(this.regionIds);
            }
        }
        function stockStatusCheck(selectedRegionId, regions) {
            var result = false;
            for (var i = 0, len = regions.length; i < len; i++) {
                if (selectedRegionId == regions[i].region_id) {
                    if (regions[i].stock_status == STOCK_STATUS_MANY || regions[i].stock_status == STOCK_STATUS_FEW) {
                        result = true;
                    }
                }
            }
            return result;
        }
        function getPositionX(e) {
            var offsetX = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').offset().left;
            if (e.type == 'touchend') {
                return e.changedTouches[0].pageX - offsetX;
            }
            else {
                return e.pageX - offsetX;
            }
        }
        function getPositionY(e) {
            var offsetY = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').offset().top;
            if (e.type == 'touchend') {
                return e.changedTouches[0].pageY - offsetY;
            }
            else {
                return e.pageY - offsetY;
            }
        }
    };
    // 座席のタップ操作
    VenuemapComponent.prototype.tapSeat = function (e) {
        //初期化
        this.selectedSeatId = e.target.id;
        this.selectedGroupIds = [];
        this.selectedSeatGroupNames = [];
        this.selectedStockTypeMaxQuantity = null;
        //席種id取得
        for (var i = 0; i < this.seats.length; i++) {
            if (this.seats[i].seat_l0_id == this.selectedSeatId) {
                this.selectedStockTypeId = this.seats[i].stock_type_id;
                break;
            }
        }
        //1席ずつか2席以上ずつか判定
        this.isGroupedSeats = true;
        for (var i = 0, len = this.seatGroups.length; i < len; i++) {
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.seatGroups[i].seat_l0_ids) != -1) {
                this.isGroupedSeats = false;
                this.selectedGroupIds = this.seatGroups[i].seat_l0_ids;
                break;
            }
        }
        //席種に紐づく最大購入数取得＋無い場合1.公演2.イベントの順でセット
        for (var i = 0, len = this.stockType.length; i < len; i++) {
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
        }
        else {
            this.tapMultipleSeats(e);
        }
    };
    VenuemapComponent.prototype.tapOneSeats = function (e) {
        if (this.changeRgb(__WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).css('fill')) == SEAT_COLOR_AVAILABLE) {
            if (this.QuentityChecks.maxLimitCheck(this.selectedStockTypeMaxQuantity, this.performance.order_limit, this.event.order_limit, this.selectedSeatList.length + 1)) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).css({ 'fill': SEAT_COLOR_SELECTED });
                this.selectedSeatName = __WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).children('title').text();
                this.selectTimes();
            }
            else {
                this.errorModalDataService.sendToErrorModal('エラー', this.selectedStockTypeMaxQuantity + '席以下でご選択ください。');
            }
        }
        else if (this.changeRgb(__WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).css('fill')) == SEAT_COLOR_SELECTED) {
            var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.selectedSeatList);
            if (findNum != -1) {
                for (var i = 0; i < this.countSelect; i++) {
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
                for (var i = 0; i < this.seats.length; i++) {
                    if (this.selectedSeatId == this.seats[i].seat_l0_id) {
                        __WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).css({ 'fill': SEAT_COLOR_AVAILABLE });
                        break;
                    }
                }
            }
            this.displayDetail = false;
        }
    };
    VenuemapComponent.prototype.tapMultipleSeats = function (e) {
        if (this.changeRgb(__WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).css('fill')) == SEAT_COLOR_AVAILABLE) {
            if (this.selectedStockTypeId == this.prevStockType) {
                if (this.QuentityChecks.maxLimitCheck(this.selectedStockTypeMaxQuantity, this.performance.order_limit, this.event.order_limit, this.selectedSeatList.length + this.selectedGroupIds.length)) {
                    for (var i = 0, len = this.selectedGroupIds.length; i < len; i++) {
                        __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).find('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_SELECTED });
                        this.selectedSeatGroupNames.push(__WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).find('#' + this.selectedGroupIds[i]).children('title').text());
                    }
                    this.selectTimes();
                }
                else {
                    this.errorModalDataService.sendToErrorModal('エラー', this.selectedStockTypeMaxQuantity + '席以下でご選択ください。');
                }
            }
            else {
                for (var i = 0, len = this.selectedGroupIds.length; i < len; i++) {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).find('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_SELECTED });
                    this.selectedSeatGroupNames.push(__WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).find('#' + this.selectedGroupIds[i]).children('title').text());
                }
                this.selectTimes();
            }
        }
        else if (this.changeRgb(__WEBPACK_IMPORTED_MODULE_13_jquery__(e.target).css('fill')) == SEAT_COLOR_SELECTED) {
            var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedGroupIds[0], this.selectedSeatList);
            if (findNum != -1) {
                this.selectedSeatList.splice(findNum, this.selectedGroupIds.length);
                this.selectedSeatNameList.splice(findNum, this.selectedGroupIds.length);
                this.countSelect = this.selectedSeatList.length;
            }
            this.selectedCancel();
            if (this.reservedFlag) {
                for (var i = 0; i < this.seats.length; i++) {
                    if (this.selectedSeatId == this.seats[i].seat_l0_id) {
                        for (var j = 0, len = this.selectedGroupIds.length; j < len; j++) {
                            __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedGroupIds[j]).css({ 'fill': SEAT_COLOR_AVAILABLE });
                        }
                    }
                }
            }
            this.displayDetail = false;
        }
    };
    VenuemapComponent.prototype.selectTimes = function () {
        if (this.countSelect == 0) {
            // 1席目の座席選択
            this.stockTypeId = this.selectedStockTypeId;
            this.getStockTypeInforamtion();
            __WEBPACK_IMPORTED_MODULE_13_jquery__('.seatNumberBox').slideDown(300);
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() <= WINDOW_SM) {
                this.active = '';
            }
            this.sameStockType = true;
        }
        else {
            if (this.selectedStockTypeId != this.prevStockType) {
                // 席種の異なる座席選択
                this.stockTypeId = this.selectedStockTypeId;
                this.getStockTypeInforamtion();
                this.sameStockType = false;
            }
            else {
                // 2席目の座席選択，同一席種
                this.displayDetail = false;
                this.sameStockType = true;
                this.addSeatList();
            }
        }
    };
    VenuemapComponent.prototype.selectedCancel = function () {
        if (this.countSelect == 0) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('.seatNumberBox').slideUp(300);
            __WEBPACK_IMPORTED_MODULE_13_jquery__('.buyChoiceSeatBox .selectBoxBtn .closeBtnBox').removeClass('active');
            this.ticketDetail = false;
            this.countSelect = 0;
            this.sameStockType = true;
            this.stockTypeId = null;
            this.stockTypeName = '';
            this.filterComponent.selectSeatSearch(this.stockTypeName);
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() > WINDOW_SM) {
                this.stockTypeDataService.sendToSeatListFlag(true);
                this.seatSelectDisplay(true);
            }
        }
    };
    // ボタンによる拡大
    VenuemapComponent.prototype.enlargeMap = function () {
        if (this.originalViewBox && this.seats) {
            var viewBoxVals = this.getPresentViewBox();
            var venueObj = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox');
            var x = this.D_Width / 2; // 中心x
            var y = this.D_Height / 2; // 中心y
            var scale = 0.5; // 1辺の長さの拡大率
            viewBoxVals = this.getZoomViewBox(x, y, scale);
            this.scaleTotal = this.getPresentScale(viewBoxVals);
            if (this.scaleTotal > SCALE_MAX) {
                if (this.scaleTotal == SCALE_MAX) {
                    return;
                }
                else {
                    scale = this.scaleTotal / SCALE_MAX * scale;
                    this.scaleTotal = SCALE_MAX;
                    viewBoxVals = this.getZoomViewBox(x, y, scale);
                }
            }
            venueObj.children().attr('viewBox', viewBoxVals.join(' ')); // viewBoxを設定する
            if (this.scaleTotal >= SCALE_SEAT && !(this.wholemapFlag)) {
                if ((__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() <= WINDOW_SM) || (this.countSelect != 0)) {
                    this.stockTypeDataService.sendToSeatListFlag(false);
                    this.seatSelectDisplay(false);
                }
                this.wholemapFlag = true;
                this.onoffRegion(this.regionIds);
            }
        }
    };
    // ボタンによる縮小
    VenuemapComponent.prototype.shrinkMap = function () {
        if (this.originalViewBox && this.seats) {
            var viewBoxVals = this.getPresentViewBox();
            var venueObj = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox');
            var x = this.D_Width / 2; // 中心x
            var y = this.D_Height / 2; // 中心y
            var scale = 2.0; // 1辺の長さの拡大率
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
    };
    // 初期状態
    VenuemapComponent.prototype.mapHome = function () {
        var _this = this;
        if (this.countSelect == 0) {
            this.stockTypeDataService.sendToSeatListFlag(true);
            this.seatSelectDisplay(true);
        }
        var resizeTimer = setTimeout(function () {
            _this.D_Width = __WEBPACK_IMPORTED_MODULE_13_jquery__(_this.svgMap).innerWidth(); // 表示窓のwidth
            _this.D_Height = __WEBPACK_IMPORTED_MODULE_13_jquery__(_this.svgMap).innerHeight(); // 表示窓のheight
            _this.DA = _this.D_Width / _this.D_Height;
            _this.scaleTotal = _this.getPresentScale(_this.originalViewBox);
            _this.SCALE_MIN = _this.scaleTotal;
            _this.wholemapFlag = false;
            // svgのoriginalViweBoxと表示領域のアスペクト比を合わせる
            _this.displayViewBox = _this.originalViewBox.concat();
            _this.TA = parseFloat(_this.originalViewBox[2]) / parseFloat(_this.originalViewBox[3]);
            if (_this.DA >= _this.TA) {
                _this.displayViewBox[2] = String(_this.D_Width * parseFloat(_this.displayViewBox[3]) / _this.D_Height);
                _this.displayViewBox[0] = String(parseFloat(_this.displayViewBox[0]) - (parseFloat(_this.displayViewBox[2]) - parseFloat(_this.originalViewBox[2])) / 2);
            }
            else {
                _this.displayViewBox[3] = String(_this.D_Height * parseFloat(_this.displayViewBox[2]) / _this.D_Width);
                _this.displayViewBox[1] = String(parseFloat(_this.displayViewBox[1]) - (parseFloat(_this.displayViewBox[3]) - parseFloat(_this.originalViewBox[3])) / 2);
            }
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').children().attr('viewBox', _this.displayViewBox.join(' ')); // viewBoxを初期値に設定
            _this.onoffRegion(_this.regionIds);
        }, 0);
    };
    // 現在のviewBoxの値を取得
    VenuemapComponent.prototype.getPresentViewBox = function () {
        var viewBox = __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapImgBox').children().attr('viewBox');
        return (viewBox) ? viewBox.split(' ') : null;
    };
    //座席選択時の画面拡大縮小
    VenuemapComponent.prototype.seatSelectDisplay = function (flag) {
        var _this = this;
        var windowHeight = __WEBPACK_IMPORTED_MODULE_13_jquery__(window).height();
        var allHead = __WEBPACK_IMPORTED_MODULE_13_jquery__('header').height();
        +__WEBPACK_IMPORTED_MODULE_13_jquery__('.headArea').height();
        +__WEBPACK_IMPORTED_MODULE_13_jquery__('.choiceArea').height();
        ;
        var orientation = window.orientation;
        if (flag) {
            if (this.smartPhoneCheckService.isSmartPhone()) {
                if (orientation == 0 || orientation == 180) {
                    if (this.seatAreaHeight) {
                        __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapAreaLeft').css({
                            'height': this.seatAreaHeight,
                        });
                        var resizeTimer = setTimeout(function () {
                            _this.setAspectRatio();
                        }, 0);
                    }
                }
            }
        }
        else {
            if (this.smartPhoneCheckService.isSmartPhone()) {
                if (orientation == 0 || orientation == 180) {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__('#mapAreaLeft').css({
                        'height': windowHeight - allHead,
                    });
                    var resizeTimer = setTimeout(function () {
                        _this.setAspectRatio();
                    }, 0);
                }
            }
        }
    };
    //現在のアスペクト比を合わせる
    VenuemapComponent.prototype.setAspectRatio = function () {
        this.D_Width = __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).innerWidth(); // 表示窓のwidth
        this.D_Height = __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).innerHeight(); // 表示窓のheight
        this.DA = this.D_Width / this.D_Height;
        // svgのoriginalViweBoxと表示領域のアスペクト比を合わせる
        this.displayViewBox = this.originalViewBox.concat();
        this.TA = parseFloat(this.originalViewBox[2]) / parseFloat(this.originalViewBox[3]);
        if (this.DA >= this.TA) {
            this.displayViewBox[2] = String(this.D_Width * parseFloat(this.displayViewBox[3]) / this.D_Height);
            this.displayViewBox[0] = String(parseFloat(this.displayViewBox[0]) - (parseFloat(this.displayViewBox[2]) - parseFloat(this.originalViewBox[2])) / 2);
        }
        else {
            this.displayViewBox[3] = String(this.D_Height * parseFloat(this.displayViewBox[2]) / this.D_Width);
            this.displayViewBox[1] = String(parseFloat(this.displayViewBox[1]) - (parseFloat(this.displayViewBox[3]) - parseFloat(this.originalViewBox[3])) / 2);
        }
        this.onoffRegion(this.regionIds);
    };
    // 現在の画像width/表示窓widthの比
    VenuemapComponent.prototype.getPresentRatioW = function (viewBoxValues) {
        var ratioW = parseFloat(viewBoxValues[2]) / this.D_Width; // 拡大前の 画像width/表示窓width
        return ratioW;
    };
    // 現在の画像height/表示窓heightの比
    VenuemapComponent.prototype.getPresentRatioH = function (viewBoxValues) {
        var ratioH = parseFloat(viewBoxValues[3]) / this.D_Height; // 拡大前の 画像height/表示窓height
        return ratioH;
    };
    // 現在の表示倍率を求める
    VenuemapComponent.prototype.getPresentScale = function (viewBoxValues) {
        this.TA = parseFloat(viewBoxValues[2]) / parseFloat(viewBoxValues[3]);
        if (this.DA >= this.TA) {
            return (this.D_Height / parseFloat(viewBoxValues[3]));
        }
        else {
            return (this.D_Width / parseFloat(viewBoxValues[2]));
        }
    };
    // 拡大・縮小後ののviewBoxの値を取得
    VenuemapComponent.prototype.getZoomViewBox = function (x, y, scale) {
        var viewBoxValues = this.getPresentViewBox();
        var viewBoxVals = [];
        var ratioW = this.getPresentRatioW(viewBoxValues); // 拡大前の 画像width/表示窓width
        var ratioH = this.getPresentRatioH(viewBoxValues); // 拡大前の 画像height/表示窓height
        viewBoxVals[2] = scale * parseFloat(viewBoxValues[2]); // 拡大後のwidth
        viewBoxVals[3] = scale * parseFloat(viewBoxValues[3]); // 拡大後のheight
        // 拡大前と後でダブルクリックした点が表示窓上の同じ点になるようにviewBoxの始点を求める
        // （拡大前）－（拡大後）の差が拡大後の始点x, y　
        viewBoxVals[0] = (x * ratioW + parseFloat(viewBoxValues[0])) - (viewBoxVals[2] / this.D_Width * x);
        viewBoxVals[1] = (y * ratioH + parseFloat(viewBoxValues[1])) - (viewBoxVals[3] / this.D_Height * y);
        return viewBoxVals;
    };
    // ドラッグ処理のviewBoxの値を取得
    VenuemapComponent.prototype.getDragViewBox = function (x, y) {
        var viewBoxValues = this.getPresentViewBox();
        var viewBoxVals = [];
        var scale = this.getPresentScale(viewBoxValues);
        viewBoxVals[0] = parseFloat(viewBoxValues[0]); // Convert string 'numeric' values to actual numeric values.
        viewBoxVals[1] = parseFloat(viewBoxValues[1]);
        viewBoxVals[2] = parseFloat(viewBoxValues[2]);
        viewBoxVals[3] = parseFloat(viewBoxValues[3]);
        viewBoxVals[0] += (x / scale);
        if (viewBoxVals[0] < parseFloat(this.displayViewBox[0])) {
            viewBoxVals[0] = parseFloat(this.displayViewBox[0]);
        }
        else {
            if ((viewBoxVals[0] + viewBoxVals[2]) > (parseFloat(this.displayViewBox[0]) + parseFloat(this.displayViewBox[2]))) {
                viewBoxVals[0] -= (viewBoxVals[0] + viewBoxVals[2]) - (parseFloat(this.displayViewBox[0]) + parseFloat(this.displayViewBox[2]));
            }
        }
        viewBoxVals[1] += (y / scale);
        if (viewBoxVals[1] < parseFloat(this.displayViewBox[1])) {
            viewBoxVals[1] = parseFloat(this.displayViewBox[1]);
        }
        else {
            if ((viewBoxVals[1] + viewBoxVals[3]) > (parseFloat(this.displayViewBox[1]) + parseFloat(this.displayViewBox[3]))) {
                viewBoxVals[1] -= (viewBoxVals[1] + viewBoxVals[3]) - (parseFloat(this.displayViewBox[1]) + parseFloat(this.displayViewBox[3]));
            }
        }
        return viewBoxVals;
    };
    // 個席表示/非表示処理
    VenuemapComponent.prototype.onoffRegion = function (regionIds) {
        var region;
        var flag;
        if (this.scaleTotal < SCALE_SEAT) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__(".region").each(function () {
                region = __WEBPACK_IMPORTED_MODULE_13_jquery__(this).attr('id');
                flag = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](region, regionIds);
                if (flag == -1) {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__(this).css({ 'display': 'inline' });
                }
            });
        }
        else {
            __WEBPACK_IMPORTED_MODULE_13_jquery__(".region").each(function () {
                region = __WEBPACK_IMPORTED_MODULE_13_jquery__(this).attr('id');
                flag = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](region, regionIds);
                if (flag == -1) {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__(this).css({ 'display': 'none' });
                }
            });
        }
        this.setActiveGrid();
    };
    // SVGの座席データを[連席ID, Element]として保持してDOMツリーから削除
    VenuemapComponent.prototype.saveSeatData = function () {
        var els = document.querySelectorAll('.seat');
        for (var i = 0; i < els.length; i++) {
            var grid_class = els[i].className.baseVal;
            grid_class = grid_class.substr(grid_class.indexOf('grid'), 13);
            var parent_id = __WEBPACK_IMPORTED_MODULE_13_jquery__(els[i].parentNode).attr('id');
            if (!(grid_class in this.seat_elements)) {
                this.seat_elements[grid_class] = [];
            }
            els[i].style.display = 'inline';
            (this.seat_elements[grid_class]).push([parent_id, els[i]]);
        }
        __WEBPACK_IMPORTED_MODULE_13_jquery__('.seat').remove();
    };
    // 現在の描画サイズに合わせて表示するグリッドを決定し、座席データを動的に追加・削除
    VenuemapComponent.prototype.setActiveGrid = function () {
        if (this.scaleTotal >= SCALE_SEAT) {
            var viewBox = this.getPresentViewBox();
            var grid_x_from = Math.floor(viewBox[0] / this.venueGridSize) - 1;
            var grid_y_from = Math.floor(viewBox[1] / this.venueGridSize) - 1;
            var grid_x_to = Math.floor((Number(viewBox[0]) + Number(viewBox[2])) / this.venueGridSize) + 1;
            var grid_y_to = Math.floor((Number(viewBox[1]) + Number(viewBox[3])) / this.venueGridSize) + 1;
            var $svg = __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap);
            var next_active_grid = [];
            var isRedrawSeats = false;
            for (var x = grid_x_from; x <= grid_x_to; x++) {
                for (var y = grid_y_from; y <= grid_y_to; y++) {
                    var grid_class = 'grid_';
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
            for (var i = 0; i < this.active_grid.length; i++) {
                if (!(next_active_grid.indexOf(this.active_grid[i]) >= 0)) {
                    var els = this.seat_elements[this.active_grid[i]];
                    for (var idx = 0; idx < els.length; idx++) {
                        document.getElementById(els[idx][0]).textContent = null;
                    }
                    this.active_grid.splice(i, 1);
                }
            }
            // 非表示から表示へ
            for (var i in next_active_grid) {
                if (!(next_active_grid[i] in this.active_grid)) {
                    var els = this.seat_elements[next_active_grid[i]];
                    for (var idx = 0; idx < els.length; idx++) {
                        document.getElementById(els[idx][0]).appendChild(els[idx][1]);
                        this.active_grid.push(next_active_grid[i]);
                        isRedrawSeats = true;
                    }
                }
            }
            if (isRedrawSeats)
                this.drawingSeats();
        }
        else {
            for (var i = 0; i < this.active_grid.length; i++) {
                var els = this.seat_elements[this.active_grid[i]];
                for (var idx = 0; idx < els.length; idx++) {
                    document.getElementById(els[idx][0]).textContent = null;
                }
            }
            this.active_grid = [];
        }
    };
    // 座席要素の色付け
    VenuemapComponent.prototype.drawingSeats = function () {
        if (!(this.seats))
            return;
        __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).find('.seat').css({ 'fill': SEAT_COLOR_NA });
        // フィルタで指定席がONの場合のみ空席の色付け
        if (this.reservedFlag) {
            // 空席の色付け
            for (var i = 0, len = this.seats.length; i < len; i++) {
                if (this.seats[i].is_available) {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.seats[i].seat_l0_id).css({ 'fill': SEAT_COLOR_AVAILABLE });
                }
            }
        }
        // 座席が選択されていた場合の色付け
        for (var i = 0; i < this.selectedSeatList.length; i++) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_SELECTED });
        }
    };
    // 詳細情報の表示
    VenuemapComponent.prototype.showDialog = function (value) {
        this.displayDetail = true;
        this.modalTopCss();
        // 押下したボタンの座席名
        this.selectedSeatName = value;
        var flag = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatName, this.selectedSeatNameList);
        this.selectedSeatId = this.selectedSeatList[flag];
        this.selectedStockTypeName = this.stockTypeName;
        this.selectedDescription = this.description;
        // 押下したボタンの座席idの席種
        for (var i = 0; i < this.countSelect; i++) {
            if (this.selectedSeatId == this.seats[i].seat_l0_id) {
                this.selectedStockTypeId = this.seats[i].stock_type_id;
                break;
            }
        }
    };
    // ダイアログの消去
    VenuemapComponent.prototype.removeDialog = function () {
        if (this.isGroupedSeats) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatId).css({ 'fill': SEAT_COLOR_NA });
            if (this.reservedFlag) {
                for (var i = 0; i < this.seats.length; i++) {
                    if (this.selectedSeatId == this.seats[i].seat_l0_id) {
                        __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.seats[i].seat_l0_id).css({ 'fill': SEAT_COLOR_AVAILABLE });
                        break;
                    }
                }
            }
            var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.selectedSeatList);
            if (findNum != -1) {
                this.selectedSeatList.splice(findNum, 1);
                this.selectedSeatNameList.splice(findNum, 1);
                this.countSelect--;
            }
        }
        else {
            for (var i = 0, len = this.selectedGroupIds.length; i < len; i++) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_NA });
            }
            if (this.reservedFlag) {
                for (var i = 0, len = this.selectedGroupIds.length; i < len; i++) {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedGroupIds[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
                }
            }
            var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedGroupIds[0], this.selectedSeatList);
            if (findNum != -1) {
                this.selectedSeatList.splice(findNum, this.selectedGroupIds.length);
                this.selectedSeatNameList.splice(findNum, this.selectedGroupIds.length);
                this.countSelect = this.selectedSeatList.length;
            }
        }
        this.displayDetail = false;
        if (this.countSelect == 0) {
            this.ticketDetail = false;
            if ((__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() > WINDOW_SM) || (this.scaleTotal < SCALE_SEAT)) {
                this.seatSelectDisplay(false);
            }
        }
    };
    // リストへの追加
    VenuemapComponent.prototype.addSeatList = function () {
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
                var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.selectedSeatList);
                if (findNum == -1) {
                    this.selectedSeatList[this.countSelect] = this.selectedSeatId;
                    this.selectedSeatNameList[this.countSelect] = this.selectedSeatName;
                    this.countSelect++;
                    this.prevSeatId = this.selectedSeatId;
                    this.prevStockType = this.selectedStockTypeId;
                }
            }
            else {
                var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.selectedSeatList);
                if (findNum == -1) {
                    Array.prototype.push.apply(this.selectedSeatList, this.selectedGroupIds);
                    Array.prototype.push.apply(this.selectedSeatNameList, this.selectedSeatGroupNames);
                    this.countSelect = this.selectedSeatList.length;
                    this.prevSeatId = this.selectedSeatId;
                    this.prevStockType = this.selectedStockTypeId;
                }
            }
        }
        else {
            this.confirmStockType = true;
        }
    };
    // リストから削除（席種の異なる座席を選択した場合）
    VenuemapComponent.prototype.removeSeatList = function () {
        this.stockTypeName = this.selectedStockTypeName;
        this.description = this.selectedDescription;
        for (var i = 0; i <= this.countSelect; i++) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_NA });
            if (this.isGroupedSeats) {
                for (var j = 0; j < this.seats.length; j++) {
                    if (this.selectedSeatList[i] == this.seats[j].seat_l0_id) {
                        __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
                        break;
                    }
                }
            }
            else {
                for (var j = 0; j < this.seats.length; j++) {
                    if (this.selectedSeatList[i] == this.seats[j].seat_l0_id) {
                        __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
                    }
                }
            }
        }
        this.selectedSeatList.length = 0;
        this.selectedSeatNameList.length = 0;
        this.countSelect = 0;
        if (!this.sameStockType) {
            if (this.isGroupedSeats) {
                this.selectedSeatList[this.countSelect] = this.selectedSeatId;
                this.selectedSeatNameList[this.countSelect] = this.selectedSeatName;
                this.countSelect++;
            }
            else {
                Array.prototype.push.apply(this.selectedSeatList, this.selectedGroupIds);
                Array.prototype.push.apply(this.selectedSeatNameList, this.selectedSeatGroupNames);
                this.countSelect = this.selectedSeatList.length;
            }
            this.confirmStockType = false;
            this.prevSeatId = this.selectedSeatId;
            this.prevStockType = this.selectedStockTypeId;
            this.sameStockType = true;
            this.filterComponent.selectSeatSearch(this.stockTypeName);
        }
        else {
            if (this.stockTypeIdFromList) {
                this.stockTypeDataService.sendToQuentity(this.stockTypeIdFromList);
            }
            else {
                this.display = false;
                this.countSelectService.sendToQuentity(this.countSelect);
                this.quantity.seatReserveClick();
            }
            this.confirmStockType = false;
            this.ticketDetail = false;
            this.stockTypeDataService.sendToIsSearchFlag(false);
        }
    };
    // 座席ボタンのｘ印から除去
    VenuemapComponent.prototype.removeSeatListFromBtn = function (value, event) {
        var rmSeatIds = [];
        // 押下したボタンの座席名
        event.stopPropagation();
        this.selectedSeatName = value;
        for (var i = 0; i < this.countSelect; i++) {
            if (this.selectedSeatName == this.selectedSeatNameList[i]) {
                this.selectedSeatId = this.selectedSeatList[i];
                break;
            }
        }
        // 押下したボタンの座席idの席種
        for (var i = 0; i < this.countSelect; i++) {
            if (this.selectedSeatId == this.seats[i].seat_l0_id) {
                this.selectedStockTypeId = this.seats[i].stock_type_id;
                break;
            }
        }
        if (this.isGroupedSeats) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatId).css({ 'fill': SEAT_COLOR_AVAILABLE });
            var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.selectedSeatList);
            if (findNum != -1) {
                this.selectedSeatList.splice(findNum, 1);
                this.selectedSeatNameList.splice(findNum, 1);
                this.countSelect--;
            }
        }
        else {
            for (var i = 0, len = this.seatGroups.length; i < len; i++) {
                if (__WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.seatGroups[i].seat_l0_ids) != -1) {
                    rmSeatIds = this.seatGroups[i].seat_l0_ids;
                }
            }
            for (var i = 0, len = rmSeatIds.length; i < len; i++) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__(this.svgMap).find('#' + rmSeatIds[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
            }
            var findNum = __WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](rmSeatIds[0], this.selectedSeatList);
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
            if ((__WEBPACK_IMPORTED_MODULE_13_jquery__(window).width() > WINDOW_SM) || (this.scaleTotal < SCALE_SEAT)) {
                this.stockTypeDataService.sendToSeatListFlag(true);
                this.seatSelectDisplay(true);
            }
        }
        this.displayDetail = false;
    };
    // カート破棄のダイアログの非表示
    VenuemapComponent.prototype.removeConfirmation = function () {
        this.confirmStockType = false;
        this.display = false;
    };
    // 席種情報取得
    VenuemapComponent.prototype.getStockTypeInforamtion = function () {
        var _this = this;
        if (this.performanceId && this.salesSegments[0].sales_segment_id && this.stockTypeId) {
            this.stockTypes.getStockType(this.performanceId, this.salesSegments[0].sales_segment_id, this.stockTypeId)
                .subscribe(function (response) {
                _this._logger.debug("get stockType(#" + _this.performanceId + ") success", response);
                var stockType = response.data.stock_types[0];
                _this.selectedStockTypeName = stockType.stock_type_name;
                _this.selectedProducts = stockType.products;
                _this.selectedDescription = stockType.description ? stockType.description : '';
                _this.displayDetail = true;
                _this.modalTopCss();
            }, function (error) {
                _this.removeDialog();
                _this._logger.error('stockType error', error);
                if (error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                    _this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
                }
            });
        }
        else {
            this.removeDialog();
            this._logger.error("パラメータに異常が発生しました。");
            this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
        }
    };
    //選択中の座席クリア
    VenuemapComponent.prototype.seatClearClick = function () {
        //色クリア
        for (var i = 0; i <= this.countSelect; i++) {
            __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatList[i]).css({ 'fill': SEAT_COLOR_NA });
        }
        //選択クリア
        this.selectedSeatList = [];
        this.selectedSeatNameList = [];
        this.countSelect = 0;
        this.stockTypeDataService.sendToIsSearchFlag(false);
        this.ticketDetail = false;
        this.mapHome();
        this.filterComponent.clearClick();
    };
    // 座席確保ボタン選択
    VenuemapComponent.prototype.seatReserveClick = function () {
        var _this = this;
        this.animationEnableService.sendToRoadFlag(true);
        __WEBPACK_IMPORTED_MODULE_13_jquery__('.reserve').prop("disabled", true);
        this.selectedStockTypeMinQuantity = null;
        var quantity = this.selectedSeatList.length;
        for (var i = 0, len = this.stockType.length; i < len; i++) {
            if (this.selectedStockTypeId == this.stockType[i].stock_type_id) {
                this.selectedStockTypeMinQuantity = this.stockType[i].min_quantity;
                break;
            }
        }
        if (this.QuentityChecks.minLimitCheck(this.selectedStockTypeMinQuantity, quantity)) {
            if (!this.QuentityChecks.salesUnitCheck(this.selectedProducts, quantity)) {
                // 選択した座席を設定
                this.dataUpdate();
                this.seatStatus.seatReserve(this.performanceId, this.salesSegments[0].sales_segment_id, this.data).subscribe(function (response) {
                    _this._logger.debug("get seatReserve(#" + _this.performanceId + ") success", response);
                    _this.resResult = response.data.results;
                    _this.resResult.seat_name = _this.selectedSeatNameList;
                    response.data.results = _this.resResult;
                    _this.seatStatus.seatReserveResponse = response;
                    _this.seatPostStatus = response.data.results.status;
                    if (_this.seatPostStatus == 'NG') {
                        _this.animationEnableService.sendToRoadFlag(false);
                        __WEBPACK_IMPORTED_MODULE_13_jquery__('.reserve').prop("disabled", false);
                        _this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');
                        _this.seatUpdate(); // 座席情報最新化
                    }
                    else {
                        _this.animationEnableService.sendToRoadFlag(false);
                        _this.router.navigate(['performances/' + _this.performanceId + '/select-product/']);
                    }
                }, function (error) {
                    _this.animationEnableService.sendToRoadFlag(false);
                    __WEBPACK_IMPORTED_MODULE_13_jquery__('.reserve').prop("disabled", false);
                    _this._logger.error('seatReserve error', error);
                    if (error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_15__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                        _this.errorModalDataService.sendToErrorModal('エラー', '座席の確保に失敗しました。');
                    }
                    _this.seatUpdate(); //座席情報最新化
                });
            }
            else {
                this.animationEnableService.sendToRoadFlag(false);
                __WEBPACK_IMPORTED_MODULE_13_jquery__('.reserve').prop("disabled", false);
                this.errorModalDataService.sendToErrorModal('エラー', this.QuentityChecks.salesUnitCheck(this.selectedProducts, quantity) + '席単位でご選択ください。');
            }
        }
        else {
            this.animationEnableService.sendToRoadFlag(false);
            __WEBPACK_IMPORTED_MODULE_13_jquery__('.reserve').prop("disabled", false);
            if (quantity) {
                this.errorModalDataService.sendToErrorModal('エラー', this.selectedStockTypeMinQuantity + '席以上でご選択ください。');
            }
            else {
                this.errorModalDataService.sendToErrorModal('エラー', 1 + '席以上でご選択ください。');
            }
        }
    };
    // 選択した座席をポストするためのデータに格納
    VenuemapComponent.prototype.dataUpdate = function () {
        this.data = {
            'reserve_type': 'seat_choise',
            'selected_seats': this.selectedSeatList
        };
    };
    // 座席情報検索更新
    VenuemapComponent.prototype.seatUpdate = function () {
        // NGorERRORの場合、座席情報検索apiを呼び、空席情報を更新する処理
        this.filterComponent.search();
    };
    // モーダルウィンドウを閉じる
    VenuemapComponent.prototype.removeModalWindow = function () {
        if (this.isGroupedSeats) {
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.selectedSeatList) == -1) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + this.selectedSeatId).css({ 'fill': SEAT_COLOR_AVAILABLE });
            }
        }
        else {
            var rmSeatIds = [];
            for (var i = 0, len = this.seatGroups.length; i < len; i++) {
                if (__WEBPACK_IMPORTED_MODULE_13_jquery__["inArray"](this.selectedSeatId, this.seatGroups[i].seat_l0_ids) != -1) {
                    rmSeatIds = this.seatGroups[i].seat_l0_ids;
                }
            }
            for (var i = 0, len = rmSeatIds.length; i < len; i++) {
                __WEBPACK_IMPORTED_MODULE_13_jquery__('#' + rmSeatIds[i]).css({ 'fill': SEAT_COLOR_AVAILABLE });
            }
        }
        this.displayDetail = false;
    };
    // ミニマップ用四角
    VenuemapComponent.prototype.ngAfterViewChecked = function () {
        if (this.wholemapFlag) {
            var svg = document.getElementById('mapImgBoxS').firstElementChild;
            if (svg) {
                var viewRect = document.getElementById('minimap-rect');
                if (viewRect) {
                    this.moveRect(viewRect);
                }
                else {
                    this.makeRect(svg);
                }
            }
        }
    };
    VenuemapComponent.prototype.makeRect = function (svg) {
        var viewBox = this.getPresentViewBox();
        var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', viewBox[0]);
        rect.setAttribute('y', viewBox[1]);
        rect.setAttribute('width', viewBox[2]);
        rect.setAttribute('height', viewBox[3]);
        rect.setAttribute('style', 'fill:##c63f44;opacity:0.8;');
        rect.setAttribute('id', 'minimap-rect');
        svg.appendChild(rect);
    };
    VenuemapComponent.prototype.moveRect = function (viewRect) {
        var viewBox = this.getPresentViewBox();
        viewRect.setAttribute('x', viewBox[0]);
        viewRect.setAttribute('y', viewBox[1]);
        viewRect.setAttribute('width', viewBox[2]);
        viewRect.setAttribute('height', viewBox[3]);
    };
    //cssが16進数か判定する
    VenuemapComponent.prototype.changeRgb = function (value) {
        var text = value.substr(0, 3);
        if (text != "rgb") {
            var red = parseInt(value.substring(1, 3), 16);
            var green = parseInt(value.substring(3, 5), 16);
            var blue = parseInt(value.substring(5, 7), 16);
            return "rgb(" + red + ", " + green + ", " + blue + ")";
        }
        return value;
    };
    //SP、検索エリアがアクティブ時のモーダルのトップ調整
    VenuemapComponent.prototype.modalTopCss = function () {
        if (this.smartPhoneCheckService.isSmartPhone()) {
            if (__WEBPACK_IMPORTED_MODULE_13_jquery__(".choiceAreaAcdBox").css('display') == "block") {
                setTimeout(function () {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__("#modalWindowAlertBox").css({
                        'top': "-250px",
                    });
                }, 100);
            }
            else {
                setTimeout(function () {
                    __WEBPACK_IMPORTED_MODULE_13_jquery__("#modalWindowAlertBox").css({
                        'top': "-37px",
                    });
                }, 100);
            }
        }
    };
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', (typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_2__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_2__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */]) === 'function' && _a) || Object)
    ], VenuemapComponent.prototype, "filterComponent", void 0);
    __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Input"])(), 
        __metadata('design:type', Number)
    ], VenuemapComponent.prototype, "mapAreaLeftH", void 0);
    __decorate([
        // reserve-by-seat.component.tsからのマップ領域の高さ設定値
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["ViewChild"])(__WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */]), 
        __metadata('design:type', (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */]) === 'function' && _b) || Object)
    ], VenuemapComponent.prototype, "quantity", void 0);
    VenuemapComponent = __decorate([
        // デフォルトの選択可能枚数
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            providers: [__WEBPACK_IMPORTED_MODULE_2__reserve_by_seat_filter_filter_component__["a" /* FilterComponent */], __WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */]],
            selector: 'app-venue-map',
            template: __webpack_require__("../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.html"),
            styles: [__webpack_require__("../../../../../src/app/reserve-by-seat/venue-map/venue-map.component.css")],
        }), 
        __metadata('design:paramtypes', [(typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_0__angular_core__["ElementRef"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_0__angular_core__["ElementRef"]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"]) === 'function' && _d) || Object, (typeof (_e = typeof __WEBPACK_IMPORTED_MODULE_4__shared_services_performances_service__["a" /* PerformancesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__shared_services_performances_service__["a" /* PerformancesService */]) === 'function' && _e) || Object, (typeof (_f = typeof __WEBPACK_IMPORTED_MODULE_5__shared_services_seat_status_service__["a" /* SeatStatusService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5__shared_services_seat_status_service__["a" /* SeatStatusService */]) === 'function' && _f) || Object, (typeof (_g = typeof __WEBPACK_IMPORTED_MODULE_6__shared_services_stock_types_service__["a" /* StockTypesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_6__shared_services_stock_types_service__["a" /* StockTypesService */]) === 'function' && _g) || Object, (typeof (_h = typeof __WEBPACK_IMPORTED_MODULE_7__shared_services_quentity_check_service__["a" /* QuentityCheckService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_7__shared_services_quentity_check_service__["a" /* QuentityCheckService */]) === 'function' && _h) || Object, (typeof (_j = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"]) === 'function' && _j) || Object, (typeof (_k = typeof __WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__reserve_by_quantity_reserve_by_quantity_component__["a" /* ReserveByQuantityComponent */]) === 'function' && _k) || Object, (typeof (_l = typeof __WEBPACK_IMPORTED_MODULE_8__shared_services_stock_type_data_service__["a" /* StockTypeDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_8__shared_services_stock_type_data_service__["a" /* StockTypeDataService */]) === 'function' && _l) || Object, (typeof (_m = typeof __WEBPACK_IMPORTED_MODULE_9__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_9__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _m) || Object, (typeof (_o = typeof __WEBPACK_IMPORTED_MODULE_10__shared_services_animation_enable_service__["a" /* AnimationEnableService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_10__shared_services_animation_enable_service__["a" /* AnimationEnableService */]) === 'function' && _o) || Object, (typeof (_p = typeof __WEBPACK_IMPORTED_MODULE_11__shared_services_count_select_service__["a" /* CountSelectService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_11__shared_services_count_select_service__["a" /* CountSelectService */]) === 'function' && _p) || Object, (typeof (_q = typeof __WEBPACK_IMPORTED_MODULE_12__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_12__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */]) === 'function' && _q) || Object, (typeof (_r = typeof __WEBPACK_IMPORTED_MODULE_14_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_14_angular2_logger_core__["Logger"]) === 'function' && _r) || Object])
    ], VenuemapComponent);
    return VenuemapComponent;
    var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p, _q, _r;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/venue-map.component.js.map

/***/ }),

/***/ "../../../../../src/app/select-product/select-product.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/select-product/select-product.component.html":
/***/ (function(module, exports) {

module.exports = "<header>\n  <div class=\"inner\">\n    <h1 class=\"title\"><a href=\"/\"><img src=\"https://tstar.s3.amazonaws.com/extauth/static/eagles/images/logo.png\" alt=\"イーグルスチケット\"></a></h1>\n    <form id=\"logout\" ngNoForm action=\"/cart/logout\" target=\"_self\" method=\"POST\">\n      <button id=\"logout\" type=\"submit\">ログアウト</button>\n    </form>\n  </div>\n</header>\n\n<div class=\"login-page\">\n  <div class=\"contents\">\n\n    <section class=\"headArea\">\n      <div class=\"inner\">\n        <p *ngIf=\"performance\"><span>{{performance.performance_name}}</span><span>{{performance.venue_name}}</span>\n        <span>{{year}}年{{month}}月{{day}}日 {{startOnTime}}～</span>\n        </p>\n        <button type=\"button\" class=\"haBtn02 pc\" (click)= \"onClick()\"><span class=\"iconSearch\"></span><span>他の試合へ</span></button>\n      </div>\n    </section>\n\n\t\t\t<section class=\"mapArea\">\n        <!--席受け-->\n        <div id=\"buySeatArea\" *ngIf=\"!response?.data.results.is_quantity_only\">\n          <p class=\"buySeatTtl\"><span>購入確認</span></p>\n          <div id=\"textArea\">\n            <p class=\"buySeatText\"><span>未割り当ての座席を＋－ボタンを操作して商品に割り当ててください。</span></p>\n            <p class=\"buySeatText\"><span>※黄色の座席が選択中の座席です</span></p>\n            <p class=\"buySeatQuantity\"><span class=\"assignedQuantity\">{{assignedQuantity}}</span>席選択済み、残り<span class=\"unassignedQuantity\">{{unAssignedQuantity}}</span>席。</p>\n          </div>\n          <div id=\"allocationArea\">\n            <p class=\"buySeatText\"><span>◆未割り当ての座席</span></p>\n            <p class=\"nextSeatText\"><span>　次の座席</span></p>\n            <p class=\"nextSeat\"*ngIf=\"nextSeat\" >{{nextSeat}}</p>\n            <p class=\"remnantSeatText\"><span>　残りの座席</span></p>\n            <div class=\"allocationSeats\" *ngFor=\"let value of seatResult?.seat_name | slice:1 ; let key = index\">\n              <p class=\"allocationSeat\">{{value}}</p>\n            </div>\n          </div>\n          <div id=\"productArea\">\n            <p class=\"buySeatText\"><span>◆商品</span></p>\n            <div class=\"productBox\" *ngFor=\"let value of products ; let key = index\">\n              <div class=\"cf\">\n                <div class=\"productNameGroup\">\n                  <p class=\"productName\"><span>{{value.product_name}}</span></p>\n                  <p class=\"productPrice\"><span>(￥{{separate(value.price)}})</span></p>\n                </div>\n                <div class=\"IconGroup\">\n                  <div class=\"IconIn\">\n                    <button class=\"iconMinus\" id=\"minus-btn{{key}}\" (click)=\"minusClick(key)\"><span></span></button>\n                      <p *ngIf=\"!selectedSeatResults[key] && !salesUnitQuantitysV[key]\" id=\"ticketSheet01\">0</p>\n                      <p *ngIf=\"selectedSeatResults[key] && !salesUnitQuantitysV[key]\" id=\"ticketSheet01\">{{selectedSeatResults[key].length}}</p>\n                      <p *ngIf=\"!selectedSeatResults[key] && salesUnitQuantitysV[key]\" id=\"ticketSheet01\">0(0席)</p>\n                      <p *ngIf=\"selectedSeatResults[key] && salesUnitQuantitysV[key]\" id=\"ticketSheet01\">{{selectedSeatResults[key].length / salesUnitQuantitysV[key]}}({{selectedSeatResults[key].length}}席)</p>\n                    <button class=\"iconPlus\" id=\"plus-btn{{key}}\" (click)=\"plusClick(key)\"><span></span></button>\n                  </div>\n                </div>\n                <div class=\"allocationSeatGroup\">\n                  <div class=\"allocationSeats\" *ngFor=\"let value of selectedSeatResults[key] ; let skey = index\">\n                    <p class=\"allocationSeat\"><span>{{value}}</span></p>\n                  </div>\n                </div>\n              </div>\n            </div>\n          </div>\n          <div id=\"priceArea\">\n            <p class=\"buySeatText\"><span class=\"priceText\">合計金額：￥{{fee}}</span><span class=\"variousText\">+ 各種手数料</span></p>\n          </div>\n          <div id=\"productSelectBtn\">\n              <button type=\"reset\" id=\"reset\" name=\"\" value=\"キャンセル\" form=\"buySeatForm\" (click)=\"cancel()\">キャンセル</button>\n              <button type=\"submit\" id=\"submit\" name=\"\" value=\"次へ\" form=\"buySeatForm\" (click)=\"purchase()\">次へ</button>\n          </div>\n        </div>\n        <!--/席受け-->\n\n        <!--数受け-->\n        <div id=\"buySeatArea\" *ngIf=\"response?.data.results.is_quantity_only\">\n          <p class=\"buySeatTtl\"><span>購入確認</span></p>\n          <div id=\"textArea\">\n            <p class=\"buySeatQuantity\"><span class=\"assignedQuantity\">{{assignedQuantity}}</span>席選択済み、残り<span class=\"unassignedQuantity\">{{unAssignedQuantity}}</span>席。</p>\n          </div>\n          <div id=\"productArea\">\n            <p class=\"buySeatText\"><span>◆商品</span></p>\n            <div class=\"productBox\" *ngFor=\"let value of products ; let key = index\">\n              <div class=\"cf\">\n                <div class=\"productNameGroup\">\n                  <p class=\"productName\"><span>{{value.product_name}}</span></p>\n                  <p class=\"productPrice\"><span>(￥{{separate(value.price)}})</span></p>\n                </div>\n                <div class=\"IconGroup\">\n                  <div class=\"IconIn\">\n                    <button class=\"iconMinus\" id=\"minus-btn{{key}}\" (click)=\"minusClick(key)\"><span></span></button>\n                      <p *ngIf=\"!selectedQuantitys[key] && !salesUnitQuantitysV[key]\" id=\"ticketSheet01\">0</p>\n                      <p *ngIf=\"selectedQuantitys[key] && !salesUnitQuantitysV[key]\" id=\"ticketSheet01\">{{selectedQuantitys[key]}}</p>\n                      <p *ngIf=\"!selectedQuantitys[key] && salesUnitQuantitysV[key]\" id=\"ticketSheet01\">0(0席)</p>\n                      <p *ngIf=\"selectedQuantitys[key] && salesUnitQuantitysV[key]\" id=\"ticketSheet01\">{{selectedQuantitys[key] / salesUnitQuantitysV[key]}}({{selectedQuantitys[key]}}席)</p>\n                    <button class=\"iconPlus\" id=\"plus-btn{{key}}\" (click)=\"plusClick(key)\"><span></span></button>\n                  </div>\n                </div>\n              </div>\n            </div>\n          </div>\n          <div id=\"priceArea\">\n             <p class=\"buySeatText\"><span class=\"priceText\">合計金額：￥{{fee}}</span><span class=\"variousText\">+ 各種手数料</span></p>\n          </div>\n          <div id=\"productSelectBtn\">\n              <button type=\"reset\" name=\"\" value=\"キャンセル\" form=\"buySeatForm\" (click)=\"cancel()\">キャンセル</button>\n              <button type=\"submit\" name=\"\" value=\"次へ\" form=\"buySeatForm\" (click)=\"purchase()\">次へ</button>\n          </div>\n        </div>\n        <!--/数受け-->\n\n        <!--エラーモーダル-->\n        <div *ngIf=\"modalVisible\" id=\"modalWindowAlertBox\" class=\"modalWindowAlertBox\">\n            <div id=\"modalWindowAlertBoxInner\" class=\"modalWindowAlertBoxInner\">\n                <div id=\"modalWindowAlert\" class=\"modalWindowAlert\">\n                    <div class=\"modalInner\">\n                        <div class=\"modalAlert\">\n                            <p class=\"modalAlertTtl\"><span></span>{{modalTitle}}</p>\n                            <p [innerHTML]=\"modalMessage\"></p>\n                            <button *ngIf=\"!timeoutFlag\" class=\"\" type=\"button\" (click)=\"modalVisible=false;\">OK</button>\n                            <button *ngIf=\"timeoutFlag\" routerLink=\"/performances/{{performanceId}}\" class=\"\" type=\"button\" (click)=\"modalVisible=false;\">OK</button>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </div>\n        <!--/エラーモーダル-->\n      </section>\n\n  </div>\n</div>\n"

/***/ }),

/***/ "../../../../../src/app/select-product/select-product.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return SelectProductComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_primeng_primeng__ = __webpack_require__("../../../../primeng/primeng.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_primeng_primeng___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_primeng_primeng__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__shared_services_seat_status_service__ = __webpack_require__("../../../../../src/app/shared/services/seat-status.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__shared_services_performances_service__ = __webpack_require__("../../../../../src/app/shared/services/performances.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_types_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_7__shared_services_select_product_service__ = __webpack_require__("../../../../../src/app/shared/services/select-product.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_8__shared_services_smartPhone_check_service__ = __webpack_require__("../../../../../src/app/shared/services/smartPhone-check.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_9__shared_services_animation_enable_service__ = __webpack_require__("../../../../../src/app/shared/services/animation-enable.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10_jquery__ = __webpack_require__("../../../../jquery/dist/jquery.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_10_jquery___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_10_jquery__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11_rxjs_Rx__ = __webpack_require__("../../../../rxjs/Rx.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_11_rxjs_Rx___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_11_rxjs_Rx__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_12__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_13_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_13_angular2_logger_core__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};














var SelectProductComponent = (function () {
    function SelectProductComponent(seatStatus, route, router, performances, stockTypes, selectProducts, errorModalDataService, smartPhoneCheckService, animationEnableService, _logger) {
        this.seatStatus = seatStatus;
        this.route = route;
        this.router = router;
        this.performances = performances;
        this.stockTypes = stockTypes;
        this.selectProducts = selectProducts;
        this.errorModalDataService = errorModalDataService;
        this.smartPhoneCheckService = smartPhoneCheckService;
        this.animationEnableService = animationEnableService;
        this._logger = _logger;
        //確保座席商品　席受け,数受け
        this.products = [];
        //販売単位(HTML表示用)　席受け,数受け
        this.salesUnitQuantitysV = [];
        //販売単位(TS処理用)　席受け,数受け
        this.salesUnitQuantitys = [];
        //未割当枚数　席受け,数受け
        this.unAssignedQuantity = 0;
        //割当済枚数　席受け,数受け
        this.assignedQuantity = 0;
        //合計金額　席受け,数受け
        this.fee = 0;
        //割当済座席名配列　席受け
        this.selectedSeatResults = {};
        //次の座席名
        this.nextSeat = null;
        //割当済座席枚数配列　数受け
        this.selectedQuantitys = [];
        //モーダル
        this.modalVisible = false;
        this.modalMessage = '';
        this.modalTitle = '選択エラー';
        this.timeoutFlag = false;
        this.response = this.seatStatus.seatReserveResponse;
    }
    SelectProductComponent.prototype.ngOnInit = function () {
        var _this = this;
        var that = this;
        this.timer = __WEBPACK_IMPORTED_MODULE_11_rxjs_Rx__["Observable"].timer(900000);
        this.timer = this.timer.subscribe(function () {
            that.cancel();
            that.timeout();
        });
        if (!this.response) {
            this.route.params.subscribe(function (params) {
                if (params && params['performance_id']) {
                    _this.performanceId = +params['performance_id'];
                    _this.router.navigate(["performances/" + _this.performanceId]);
                }
                else {
                    _this._logger.error("エラー:公演IDを取得できません");
                    _this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
                }
            });
        }
        else {
            this.seatResult = this.response.data.results;
            this.stockTypeId = this.response.data.results.stock_type_id;
            this.isQuantityOnly = this.response.data.results.is_quantity_only;
            this.loadPerformance();
        }
    };
    SelectProductComponent.prototype.ngOnDestroy = function () {
        this.timer.unsubscribe();
    };
    SelectProductComponent.prototype.timeout = function () {
        this.timeoutFlag = true;
        this.modalVisible = true;
        this.modalTitle = 'タイムアウトエラー';
        this.modalMessage = '座席確保から15分経過しました。もう一度最初からやり直してください。';
    };
    SelectProductComponent.prototype.loadPerformance = function () {
        var _this = this;
        this.route.params.subscribe(function (params) {
            if (params && params['performance_id']) {
                //パラメーター切り出し
                _this.performanceId = +params['performance_id'];
                //公演情報取得
                _this.performances.getPerformance(_this.performanceId)
                    .subscribe(function (response) {
                    _this._logger.debug("get performance(#" + _this.performanceId + ") success", response);
                    _this.performance = response.data.performance;
                    var startOn = new Date(_this.performance.start_on + '+09:00');
                    _this.startOnTime = startOn.getHours() + '時';
                    if (startOn.getMinutes() != 0) {
                        _this.startOnTime += startOn.getMinutes() + '分';
                    }
                    _this.year = startOn.getFullYear();
                    _this.month = startOn.getMonth() + 1;
                    _this.day = startOn.getDate();
                    _this.salesSegmentId = response.data.sales_segments[0].sales_segment_id;
                    _this.pageTitle = _this.performance.performance_name;
                    _this.loadStockType();
                }, function (error) {
                    _this._logger.error('performances error', error);
                    if (error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                        _this.errorModalDataService.sendToErrorModal('エラー', '公演情報を取得できません。');
                    }
                });
            }
            else {
                _this._logger.error("エラー:公演IDを取得できません");
                _this.errorModalDataService.sendToErrorModal('エラー', '公演IDを取得できません。');
            }
        });
    };
    SelectProductComponent.prototype.loadStockType = function () {
        var _this = this;
        if (this.performanceId && this.salesSegmentId && this.stockTypeId) {
            this.stockTypes.getStockType(this.performanceId, this.salesSegmentId, this.stockTypeId)
                .subscribe(function (response) {
                _this._logger.debug("get stockType(#" + _this.performanceId + ") success", response);
                _this.stockType = response.data.stock_types[0];
                _this.initialSetting();
            }, function (error) {
                _this._logger.error('stockType error', error);
                if (error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                    _this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
                }
            });
        }
        else {
            this._logger.error("パラメータに異常が発生しました。");
            this.errorModalDataService.sendToErrorModal('エラー', '席種情報を取得できません。');
        }
    };
    //初期設定
    SelectProductComponent.prototype.initialSetting = function () {
        var _this = this;
        var that = this;
        //商品一覧,販売単位取得
        this.stockType.products.forEach(function (value, key) {
            var sumQuantity = 0;
            _this.products.push(value);
            for (var i = 0, len = _this.products[key].product_items.length; i < len; i++) {
                sumQuantity += _this.products[key].product_items[i].sales_unit_quantity;
            }
            _this.salesUnitQuantitys.push(sumQuantity);
        });
        //販売単位表示用配列（1 == null）
        for (var i = 0, len = this.salesUnitQuantitys.length; i < len; i++) {
            if (this.salesUnitQuantitys[i] == 1) {
                this.salesUnitQuantitysV[i] = null;
            }
            else {
                this.salesUnitQuantitysV[i] = this.salesUnitQuantitys[i];
            }
        }
        if (this.isQuantityOnly) {
            var productCount = this.products.length;
            if (productCount == 1) {
                this.unAssignedQuantity = this.seatResult.quantity;
                if (this.salesUnitQuantitys[0] == 1) {
                    this.selectedQuantitys[0] = this.unAssignedQuantity;
                    this.unAssignedQuantity = 0;
                }
                else {
                    var divisionResult = Math.floor(this.unAssignedQuantity / this.salesUnitQuantitys[0]);
                    var setFirstProduct = divisionResult * this.salesUnitQuantitys[0];
                    this.selectedQuantitys[0] = setFirstProduct;
                    this.unAssignedQuantity -= setFirstProduct;
                }
            }
            else {
                this.unAssignedQuantity = this.seatResult.quantity;
            }
        }
        else {
            var productCount = this.products.length;
            if (productCount == 1) {
                if (this.salesUnitQuantitys[0] == 1) {
                    for (var i = 0, len = this.seatResult.seat_name.length; i < len; i++) {
                        if (this.selectedSeatResults[i] == null) {
                            this.selectedSeatResults[i] = [];
                        }
                        this.selectedSeatResults[0].push(this.seatResult.seat_name[0]);
                        this.seatResult.seat_name.shift();
                    }
                }
                else {
                    var divisionResult = Math.floor(this.seatResult.seat_name.length / this.salesUnitQuantitys[0]);
                    var setFirstProduct = divisionResult * this.salesUnitQuantitys[0];
                    for (var i = 0, len = setFirstProduct; i < len; i++) {
                        if (this.selectedSeatResults[i] == null) {
                            this.selectedSeatResults[i] = [];
                        }
                        this.selectedSeatResults[0].push(this.seatResult.seat_name[0]);
                        this.seatResult.seat_name.shift();
                    }
                }
            }
        }
        setTimeout(function () {
            that.recalculation();
        }, 0);
    };
    //-押下
    SelectProductComponent.prototype.minusClick = function (key) {
        if (this.isQuantityOnly) {
            for (var i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
                this.selectedQuantitys[key] -= 1;
                this.unAssignedQuantity++;
            }
        }
        else {
            if (this.selectedSeatResults[key] == null) {
                this.selectedSeatResults[key] = [];
            }
            if (this.salesUnitQuantitys[key] == 1) {
                for (var i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
                    var rmSeatName = this.selectedSeatResults[key][this.selectedSeatResults[key].length - 1];
                    this.selectedSeatResults[key].pop();
                    this.seatResult.seat_name.push(rmSeatName);
                }
            }
            else {
                var rmSeatNames = [];
                for (var i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
                    var rmSeatName = this.selectedSeatResults[key][this.selectedSeatResults[key].length - 1];
                    rmSeatNames.push(this.selectedSeatResults[key][this.selectedSeatResults[key].length - 1]);
                    this.selectedSeatResults[key].pop();
                }
                rmSeatNames.reverse();
                Array.prototype.push.apply(this.seatResult.seat_name, rmSeatNames);
            }
        }
        this.recalculation();
    };
    //+押下
    SelectProductComponent.prototype.plusClick = function (key) {
        if (this.isQuantityOnly) {
            if (!this.selectedQuantitys[key]) {
                this.selectedQuantitys[key] = 0;
            }
            for (var i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
                this.selectedQuantitys[key] += 1;
                this.unAssignedQuantity--;
            }
        }
        else {
            if (this.selectedSeatResults[key] == null) {
                this.selectedSeatResults[key] = [];
            }
            for (var i = 0, len = this.salesUnitQuantitys[key]; i < len; i++) {
                this.selectedSeatResults[key].push(this.seatResult.seat_name[0]);
                this.seatResult.seat_name.shift();
            }
        }
        this.recalculation();
    };
    //残席数・合計金額・選択済み座席数・±ボタン有効無効
    SelectProductComponent.prototype.recalculation = function () {
        var disabledNumber = 1;
        this.assignedQuantity = 0;
        this.fee = 0;
        if (this.isQuantityOnly) {
            //+ボタン有効無効
            for (var x in this.products) {
                if (this.unAssignedQuantity < this.salesUnitQuantitys[x]) {
                    addClass(x, "plus");
                }
                else {
                    removeClass(x, "plus");
                }
            }
            //-ボタン有効無効
            for (var x in this.products) {
                if (this.selectedQuantitys[x] > 0) {
                    if (disabledNumber > this.selectedQuantitys[x]) {
                        addClass(x, "minus");
                    }
                    else {
                        removeClass(x, "minus");
                    }
                }
                else {
                    addClass(x, "minus");
                }
            }
            //合計金額再計算
            for (var x in this.selectedQuantitys) {
                this.assignedQuantity += this.selectedQuantitys[x];
                if (this.products[x]) {
                    if ((this.salesUnitQuantitys[x]) > 1) {
                        this.fee = (this.products[x].price / this.salesUnitQuantitys[x]) * this.selectedQuantitys[x] + this.fee;
                    }
                    else {
                        this.fee = this.products[x].price * this.selectedQuantitys[x] + this.fee;
                    }
                }
            }
        }
        else {
            //未割当席数再取得
            this.unAssignedQuantity = this.seatResult.seat_name.length;
            this.nextSeat = this.seatResult.seat_name[0];
            //+ボタン有効無効
            for (var x in this.products) {
                if (this.unAssignedQuantity < this.salesUnitQuantitys[x]) {
                    addClass(x, "plus");
                }
                else {
                    removeClass(x, "plus");
                }
            }
            //-ボタン有効無効
            for (var x in this.products) {
                if (this.selectedSeatResults[x]) {
                    if (disabledNumber > this.selectedSeatResults[x].length) {
                        addClass(x, "minus");
                    }
                    else {
                        removeClass(x, "minus");
                    }
                }
                else {
                    addClass(x, "minus");
                }
            }
            //合計金額再計算
            for (var x in this.selectedSeatResults) {
                this.assignedQuantity += this.selectedSeatResults[x].length;
                if (this.products[x]) {
                    if ((this.salesUnitQuantitys[x]) != 1) {
                        this.fee = (this.products[x].price / this.salesUnitQuantitys[x]) * this.selectedSeatResults[x].length + this.fee;
                    }
                    else {
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
        function addClass(x, str) {
            if (str == "plus") {
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#plus-btn' + [x]).prop("disabled", true);
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#plus-btn' + [x]).addClass('disabled');
            }
            else {
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#minus-btn' + [x]).prop("disabled", true);
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#minus-btn' + [x]).addClass('disabled');
            }
        }
        /**
        * +ボタン有効無効
        * @param  {string}  x ボタン番号
        * @param  {string}  str プラスorマイナス
        */
        function removeClass(x, str) {
            if (str == "plus") {
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#plus-btn' + [x]).prop("disabled", false);
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#plus-btn' + [x]).removeClass('disabled');
            }
            else {
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#minus-btn' + [x]).prop("disabled", false);
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#minus-btn' + [x]).removeClass('disabled');
            }
        }
    };
    //キャンセルボタン押下（座席開放API）
    SelectProductComponent.prototype.cancel = function () {
        var _this = this;
        this.seatStatus.seatRelease(this.performanceId)
            .subscribe(function (response) {
            _this._logger.debug("seat release(#" + _this.performanceId + ") success", response);
            _this.releaseResponse = response.data.results;
            if (_this.releaseResponse.status == "NG") {
                _this._logger.error('seat release error', _this.releaseResponse);
                _this.errorModalDataService.sendToErrorModal('エラー', '座席を解放できません。');
            }
        }, function (error) {
            _this._logger.error('seat release error', error);
            if (error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                _this.errorModalDataService.sendToErrorModal('エラー', '座席を解放できません。');
            }
        });
        this.router.navigate(["performances/" + this.performanceId]);
    };
    //購入ボタン押下（商品選択API）
    SelectProductComponent.prototype.purchase = function () {
        var _this = this;
        this.animationEnableService.sendToRoadFlag(true);
        __WEBPACK_IMPORTED_MODULE_10_jquery__('#submit').prop("disabled", true);
        var data;
        data = {
            "is_quantity_only": this.isQuantityOnly,
            "selected_products": []
        };
        if (data.is_quantity_only) {
            var RequestQuantity = 1;
            this.selectedQuantitys.forEach(function (value, key) {
                if (value >= 1) {
                    var productItemsCount = _this.products[key].product_items.length;
                    var setProductItemId = _this.products[key].product_items[0].product_item_id;
                    if (productItemsCount == 1) {
                        data.selected_products.push({
                            "seat_id": null,
                            "product_item_id": setProductItemId,
                            "quantity": value
                        });
                    }
                    else {
                        var productItemIds = [];
                        var processingCount = [];
                        //商品明細idを取得する処理数を取得
                        for (var x in _this.selectedQuantitys) {
                            if (_this.selectedQuantitys[x]) {
                                if (_this.isInteger(_this.selectedQuantitys[x] / 2) && _this.salesUnitQuantitys[x] != 1) {
                                    processingCount.push(_this.selectedQuantitys[x] / 2);
                                }
                                else {
                                    processingCount.push(_this.selectedQuantitys[x]);
                                }
                            }
                            else {
                                processingCount.push(null);
                            }
                        }
                        //商品明細idを選択されている上から取得
                        for (var x in _this.selectedQuantitys) {
                            if (processingCount[x]) {
                                for (var i = 0, len = processingCount[x]; i < len; i++) {
                                    if (_this.products[x].product_items.length != 1) {
                                        for (var j = 0, len_1 = _this.products[x].product_items.length; j < len_1; j++) {
                                            productItemIds.push(_this.products[x].product_items[j].product_item_id);
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
                        for (var i = 0, len = productItemIds.length; i < len; i++) {
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
        }
        else {
            var RequestQuantity_1 = 1;
            var itemIndex = 0;
            var salesUnit = 1;
            var seatMap = new Map();
            var setProductItemIds_1 = [];
            var setSeatIds_1 = [];
            for (var x in this.seatResult.seats) {
                seatMap.set(this.seatResult.seats[x].seat_name, this.seatResult.seats[x].seat_id);
            }
            for (var x in this.selectedSeatResults) {
                for (var y in this.selectedSeatResults[x]) {
                    //商品明細id,seatIdを設定
                    setProductItemIds_1.push(this.products[x].product_items[itemIndex].product_item_id);
                    setSeatIds_1.push(seatMap.get(this.selectedSeatResults[x][y]));
                    if (this.products[x].product_items[itemIndex].sales_unit_quantity == salesUnit) {
                        if (this.products[x].product_items.length - 1 == itemIndex) {
                            itemIndex = 0;
                        }
                        else {
                            itemIndex++;
                        }
                        salesUnit = 1;
                    }
                    else {
                        salesUnit++;
                    }
                }
            }
            //商品明細id,seatIdセット
            this.seatResult.seats.forEach(function (value, key) {
                data.selected_products.push({
                    "seat_id": setSeatIds_1[key],
                    "product_item_id": setProductItemIds_1[key],
                    "quantity": RequestQuantity_1
                });
            });
            this.unassignedSeatCheck(this.seatResult.seat_name.length);
        }
        //商品選択API
        if (!this.modalVisible) {
            this.selectProducts.selectProduct(this.performanceId, data)
                .subscribe(function (response) {
                _this._logger.debug("select product(#" + _this.performanceId + ") success", response);
                _this.selectProduct = response;
                if (_this.selectProduct.data.results.status == "OK") {
                    //現行カートの支払いへ遷移
                    _this.animationEnableService.sendToRoadFlag(false);
                    location.href = '/cart/payment/sales/' + _this.salesSegmentId;
                }
                else {
                    _this.animationEnableService.sendToRoadFlag(false);
                    __WEBPACK_IMPORTED_MODULE_10_jquery__('#submit').prop("disabled", false);
                    _this._logger.debug('select product error', _this.selectProduct.data.results.reason);
                    _this.errorModalDataService.sendToErrorModal('エラー', '商品を選択できません。');
                }
            }, function (error) {
                _this.animationEnableService.sendToRoadFlag(false);
                __WEBPACK_IMPORTED_MODULE_10_jquery__('#submit').prop("disabled", false);
                _this._logger.error('select product error', error);
                if (error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].TIMEOUT && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDNSERROR && error != "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
                    _this.errorModalDataService.sendToErrorModal('エラー', '商品を選択できません。');
                }
            });
        }
    };
    //トップへ遷移
    SelectProductComponent.prototype.onClick = function () {
        location.href = "" + __WEBPACK_IMPORTED_MODULE_12__app_constants__["b" /* AppConstService */].PAGE_URL.TOP;
    };
    /**
   * 合計枚数チェック
   * @param  {number}  num 未割当枚数
   */
    SelectProductComponent.prototype.unassignedSeatCheck = function (num) {
        if (num > 0) {
            this.modalVisible = true;
            this.modalMessage = '<p>未割当の座席があります。</p>';
            this.animationEnableService.sendToRoadFlag(false);
            __WEBPACK_IMPORTED_MODULE_10_jquery__('#submit').prop("disabled", false);
        }
    };
    /**
    * 整数か返す
    * @param  {number}  x 判定対象
    * @return {boolean}
    */
    SelectProductComponent.prototype.isInteger = function (x) {
        return Math.round(x) === x;
    };
    /**
    * 3桁区切りにし返す
    * @param  {any}  num 桁区切り対象
    * @return {any}
    */
    SelectProductComponent.prototype.separate = function (num) {
        num = String(num);
        var len = num.length;
        if (len > 3) {
            return this.separate(num.substring(0, len - 3)) + ',' + num.substring(len - 3);
        }
        else {
            return num;
        }
    };
    SelectProductComponent.prototype.ngAfterViewInit = function () {
        var that = this;
        function bodyContentsHeight() {
            var h = Math.max.apply(null, [document.body.clientHeight, document.body.scrollHeight, document.documentElement.scrollHeight, document.documentElement.clientHeight]);
            return h;
        }
        __WEBPACK_IMPORTED_MODULE_10_jquery__(function () {
            var windowWidth = __WEBPACK_IMPORTED_MODULE_10_jquery__(window).width();
            var windowSm = 768;
            if (windowWidth <= windowSm) {
                //横幅768px以下のとき（つまりスマホ時）に行う処理を書く
                __WEBPACK_IMPORTED_MODULE_10_jquery__(function () {
                    var windowH;
                    var mainH;
                    var minus = 112;
                    var mainID = 'buySeatArea';
                    function heightSetting() {
                        windowH = __WEBPACK_IMPORTED_MODULE_10_jquery__(window).height();
                        mainH = windowH - minus;
                        if (that.isQuantityOnly) {
                            __WEBPACK_IMPORTED_MODULE_10_jquery__('#' + mainID).height(bodyContentsHeight());
                        }
                    }
                    heightSetting();
                    __WEBPACK_IMPORTED_MODULE_10_jquery__(window).resize(function () {
                        heightSetting();
                    });
                });
            }
            else {
                //横幅768px超のとき（タブレット、PC）に行う処理を書く
                __WEBPACK_IMPORTED_MODULE_10_jquery__(function () {
                    var windowH;
                    var mainH;
                    var minus = 169;
                    var mainID = 'buySeatArea';
                    function heightSetting() {
                        windowH = __WEBPACK_IMPORTED_MODULE_10_jquery__(window).height();
                        mainH = windowH - minus;
                        __WEBPACK_IMPORTED_MODULE_10_jquery__('#' + mainID).height(mainH + 'px');
                    }
                    heightSetting();
                    __WEBPACK_IMPORTED_MODULE_10_jquery__(window).resize(function () {
                        heightSetting();
                    });
                });
            }
        });
    };
    SelectProductComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-select-product',
            template: __webpack_require__("../../../../../src/app/select-product/select-product.component.html"),
            styles: [__webpack_require__("../../../../../src/app/select-product/select-product.component.css")]
        }),
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["NgModule"])({
            imports: [
                __WEBPACK_IMPORTED_MODULE_2_primeng_primeng__["DropdownModule"],
            ],
            declarations: [
                __WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]
            ],
            bootstrap: [__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"]]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_3__shared_services_seat_status_service__["a" /* SeatStatusService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__shared_services_seat_status_service__["a" /* SeatStatusService */]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["ActivatedRoute"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_4__shared_services_performances_service__["a" /* PerformancesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__shared_services_performances_service__["a" /* PerformancesService */]) === 'function' && _d) || Object, (typeof (_e = typeof __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_types_service__["a" /* StockTypesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5__shared_services_stock_types_service__["a" /* StockTypesService */]) === 'function' && _e) || Object, (typeof (_f = typeof __WEBPACK_IMPORTED_MODULE_7__shared_services_select_product_service__["a" /* SelectProductService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_7__shared_services_select_product_service__["a" /* SelectProductService */]) === 'function' && _f) || Object, (typeof (_g = typeof __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_6__shared_services_error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _g) || Object, (typeof (_h = typeof __WEBPACK_IMPORTED_MODULE_8__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_8__shared_services_smartPhone_check_service__["a" /* SmartPhoneCheckService */]) === 'function' && _h) || Object, (typeof (_j = typeof __WEBPACK_IMPORTED_MODULE_9__shared_services_animation_enable_service__["a" /* AnimationEnableService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_9__shared_services_animation_enable_service__["a" /* AnimationEnableService */]) === 'function' && _j) || Object, (typeof (_k = typeof __WEBPACK_IMPORTED_MODULE_13_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_13_angular2_logger_core__["Logger"]) === 'function' && _k) || Object])
    ], SelectProductComponent);
    return SelectProductComponent;
    var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/select-product.component.js.map

/***/ }),

/***/ "../../../../../src/app/shared/components/road-animation.component.css":
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__("../../../../css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "", ""]);

// exports


/*** EXPORTS FROM exports-loader ***/
module.exports = module.exports.toString();

/***/ }),

/***/ "../../../../../src/app/shared/components/road-animation.component.html":
/***/ (function(module, exports) {

module.exports = "<!-- loading animation -->\r\n<div *ngIf=\"roadAnimeDisplay\">\r\n    <div id=\"roadBackground\">\r\n        <div id=\"roadfloatingCircles\">\r\n            <div class=\"f_circleG\" id=\"frotateG_01\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_02\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_03\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_04\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_05\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_06\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_07\"></div>\r\n            <div class=\"f_circleG\" id=\"frotateG_08\"></div>\r\n            <p id=\"loadingText\">読み込み中<p>\r\n        </div>\r\n    </div>\r\n</div>\r\n<!-- /loading animation -->"

/***/ }),

/***/ "../../../../../src/app/shared/components/road-animation.component.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return RoadAnimationComponent; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__shared_services_animation_enable_service__ = __webpack_require__("../../../../../src/app/shared/services/animation-enable.service.ts");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var RoadAnimationComponent = (function () {
    function RoadAnimationComponent(animationEnableService) {
        this.animationEnableService = animationEnableService;
    }
    RoadAnimationComponent.prototype.ngOnInit = function () {
        var _this = this;
        this.animationEnableService.toRoadingFlag$.subscribe(function (flag) {
            _this.roadAnimeDisplay = flag;
        });
    };
    RoadAnimationComponent = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Component"])({
            selector: 'app-road-animation',
            template: __webpack_require__("../../../../../src/app/shared/components/road-animation.component.html"),
            styles: [__webpack_require__("../../../../../src/app/shared/components/road-animation.component.css")]
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__shared_services_animation_enable_service__["a" /* AnimationEnableService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__shared_services_animation_enable_service__["a" /* AnimationEnableService */]) === 'function' && _a) || Object])
    ], RoadAnimationComponent);
    return RoadAnimationComponent;
    var _a;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/road-animation.component.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/animation-enable.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return AnimationEnableService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__ = __webpack_require__("../../../../rxjs/Subject.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var AnimationEnableService = (function () {
    function AnimationEnableService() {
        this.roadingFlag = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        this.toRoadingFlag$ = this.roadingFlag.asObservable();
    }
    AnimationEnableService.prototype.sendToRoadFlag = function (roadBool) {
        this.roadingFlag.next(roadBool);
    };
    AnimationEnableService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], AnimationEnableService);
    return AnimationEnableService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/animation-enable.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/api-base.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return ApiBase; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_rxjs_Observable__ = __webpack_require__("../../../../rxjs/Observable.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_rxjs_Observable___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_rxjs_Observable__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_rxjs_add_operator_map__ = __webpack_require__("../../../../rxjs/add/operator/map.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_rxjs_add_operator_map___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_rxjs_add_operator_map__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__);
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};







var ApiBase = (function (_super) {
    __extends(ApiBase, _super);
    function ApiBase(backend, options, errorModalDataService, _logger) {
        _super.call(this, backend, options);
        this.errorModalDataService = errorModalDataService;
        this._logger = _logger;
        this.settingHeader(options);
        this.cachedGetObservables = {};
    }
    /**
     * APIリクエスト時の共通ヘッダーを設定します
     *
     * @param RequestOptions options - リクエストオプション
     */
    ApiBase.prototype.settingHeader = function (options) {
        options.headers = new __WEBPACK_IMPORTED_MODULE_1__angular_http__["Headers"]({
            'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
        });
    };
    /**
     * GETリクエストを実行します
     *
     * @param string url - API-URL
     * @param boolean useCache - Returns cached response if true
     * @return Observable<T> - Observable関数
     * @return null - 通信エラー
     */
    ApiBase.prototype.httpGet = function (url, useCache) {
        var _this = this;
        if (useCache === void 0) { useCache = false; }
        if (useCache && this.cachedGetObservables[url] != undefined) {
            this._logger.debug('API GET:', url + ' [CACHED]');
            return this.cachedGetObservables[url];
        }
        this._logger.debug('API GET:', url);
        var get = this.get(url, this.options)
            .timeout(60000)
            .map(function (response) {
            var body = response.json();
            _this.check401(body);
            _this.cachedGetObservables[url] = __WEBPACK_IMPORTED_MODULE_2_rxjs_Observable__["Observable"].of(body);
            return body;
        })
            .catch(function (error) { return _this.handleError(error); })
            .share();
        this.cachedGetObservables[url] = get;
        return get;
    };
    /**
     * POSTリクエストを実行します
     *
     * @param string url - API-URL
     * @param Object data - ポストデータ
     * @return Observable<T> - Observable関数
     * @return null - 通信エラー
     */
    ApiBase.prototype.httpPost = function (url, data) {
        var _this = this;
        this._logger.debug('API POST', url);
        return this.post(url, data, this.options)
            .timeout(60000)
            .map(function (response) {
            var body = response.json();
            _this.check401(body);
            return body;
        })
            .catch(function (error) { return _this.handleError(error); });
    };
    ApiBase.prototype.handleError = function (error) {
        var errMsg;
        if (error instanceof __WEBPACK_IMPORTED_MODULE_1__angular_http__["Response"]) {
            var body = error.json() || '';
            var err = body.error || JSON.stringify(body);
            var status = error.status;
            errMsg = error.status + " - " + (error.statusText || '') + " " + err;
            if (status == 0) {
                errMsg = "" + __WEBPACK_IMPORTED_MODULE_5__app_constants__["a" /* ApiConst */].SERVERDNSERROR;
            }
            else if (status == 503) {
                errMsg = "" + __WEBPACK_IMPORTED_MODULE_5__app_constants__["a" /* ApiConst */].SERVERDOWNERROR;
            }
        }
        else {
            errMsg = error.message ? error.message : error.toString();
        }
        this._logger.error(errMsg);
        this.callErrorModal(errMsg);
        return __WEBPACK_IMPORTED_MODULE_2_rxjs_Observable__["Observable"].throw(errMsg);
    };
    ApiBase.prototype.callErrorModal = function (errMsg) {
        if (errMsg == "" + __WEBPACK_IMPORTED_MODULE_5__app_constants__["a" /* ApiConst */].TIMEOUT || errMsg == "" + __WEBPACK_IMPORTED_MODULE_5__app_constants__["a" /* ApiConst */].SERVERDNSERROR || errMsg == "" + __WEBPACK_IMPORTED_MODULE_5__app_constants__["a" /* ApiConst */].SERVERDOWNERROR) {
            this.errorModalDataService.sendToErrorModal();
        }
    };
    ApiBase.prototype.check401 = function (body) {
        if (body.data.error && body.data.error.code == 401) {
            var message = "Error:401 Unauthorized";
            this._logger.error(message);
            this.errorModalDataService.sendToErrorModal('エラー', 'ログインしてください。');
            window.location.reload();
            throw new Error(message);
        }
    };
    ApiBase = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__["Logger"]) === 'function' && _d) || Object])
    ], ApiBase);
    return ApiBase;
    var _a, _b, _c, _d;
}(__WEBPACK_IMPORTED_MODULE_1__angular_http__["Http"]));
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/api-base.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/count-select.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return CountSelectService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__ = __webpack_require__("../../../../rxjs/Subject.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var CountSelectService = (function () {
    function CountSelectService() {
        this.toQuentityCountSelect = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        // Observable streams
        this.toQuentityData$ = this.toQuentityCountSelect.asObservable();
    }
    // Service message commands
    CountSelectService.prototype.sendToQuentity = function (countSelect) {
        this.toQuentityCountSelect.next(countSelect);
    };
    CountSelectService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], CountSelectService);
    return CountSelectService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/count-select.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/error-modal-data.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return ErrorModalDataService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__ = __webpack_require__("../../../../rxjs/Subject.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var ErrorModalDataService = (function () {
    function ErrorModalDataService() {
        //private toQuentityDataStockTypeId = new Subject<number>();
        //private errorDisplay = new Subject<boolean>();
        this.errorTitle = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        this.errorDetail = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        // Observable streams
        //public toQuentityData$= this.toQuentityDataStockTypeId.asObservable();
        //public errorDisplay$= this.errorDisplay.asObservable();
        this.errorTitle$ = this.errorTitle.asObservable();
        this.errorDetail$ = this.errorDetail.asObservable();
    }
    // Service message commands
    ErrorModalDataService.prototype.sendToErrorModal = function (title, detail) {
        // this.toQuentityDataStockTypeId.next(stockTypeId);
        //this.errorDisplay.next(true);
        title = title ? title : 'サーバーと通信できません。';
        this.errorTitle.next(title);
        detail = detail ? detail : 'インターネットに未接続または通信が不安定な可能性があります。通信環境の良いところで操作をやり直すかページを再読込してください。';
        this.errorDetail.next(detail);
    };
    ErrorModalDataService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], ErrorModalDataService);
    return ErrorModalDataService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/error-modal-data.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/performance-resolver.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return PerformanceResolver; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__ = __webpack_require__("../../../../rxjs/Rx.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__services_performances_service__ = __webpack_require__("../../../../../src/app/shared/services/performances.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};





var PerformanceResolver = (function () {
    function PerformanceResolver(performanceService, router, _logger) {
        this.performanceService = performanceService;
        this.router = router;
        this._logger = _logger;
    }
    /**
     * Resolve the performance by performance id in url param
     * @param  {ActivatedRouteSnapshot} route
     * @return {Observable<IPerformanceInfoResponse | IErrorResponse>} response
     */
    PerformanceResolver.prototype.resolve = function (route) {
        var _this = this;
        if (!route.params || !route.params['performance_id']) {
            var message = "Error: performance_id not exists in url";
            this._logger.error(message);
            return __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__["Observable"].throw(message);
        }
        var id = route.params['performance_id'];
        var getPerformance = this.performanceService.getPerformance(id);
        getPerformance.subscribe(function (response) {
            _this._logger.debug("Performance#" + id + " has been fetched.", response);
        }, function (error) {
            var message = "Error: Performance#${id} could not fetched.";
            _this._logger.error(message + error);
            _this.router.navigate(['/performances/' + id + '']);
            return __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__["Observable"].throw(message);
        });
        return getPerformance;
    };
    PerformanceResolver = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_3__services_performances_service__["a" /* PerformancesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__services_performances_service__["a" /* PerformancesService */]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__["Logger"]) === 'function' && _c) || Object])
    ], PerformanceResolver);
    return PerformanceResolver;
    var _a, _b, _c;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/performance-resolver.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/performances.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return PerformancesService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__api_base_service__ = __webpack_require__("../../../../../src/app/shared/services/api-base.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__);
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};






var PerformancesService = (function (_super) {
    __extends(PerformancesService, _super);
    function PerformancesService(backend, options, errorModalDataService, _logger) {
        _super.call(this, backend, options, errorModalDataService, _logger);
    }
    /**
     * 公演情報取得
     * @param {number} performanceId 公演ID
     * @return {Observable} see http.get()
     */
    PerformancesService.prototype.getPerformance = function (performanceId) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.PERFORMANCE_INfO.replace(/{:performance_id}/, performanceId + '');
        var httpGet = this.httpGet(url, true).map(function (response) {
            response.data.performance.sales_segments = response.data.sales_segments;
            return response;
        }).share();
        return httpGet;
    };
    /**
     * 公演情報検索
     * @param  {number}     eventId イベントID
     * @return {Observable} see http.get()
     */
    PerformancesService.prototype.findPerformancesByEventId = function (eventId) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.PERFORMANCES.replace(/{:event_id}/, eventId + '');
        return this.httpGet(url);
    };
    PerformancesService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"]) === 'function' && _d) || Object])
    ], PerformancesService);
    return PerformancesService;
    var _a, _b, _c, _d;
}(__WEBPACK_IMPORTED_MODULE_2__api_base_service__["a" /* ApiBase */]));
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/performances.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/quentity-check.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return QuentityCheckService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};

var QuentityCheckService = (function () {
    function QuentityCheckService() {
        this.defaultMaxQuantity = 10;
        this.defaultMinQuantity = 1;
    }
    /**
   * 購入上限枚数チェックを行います
   *
   * @param  {number} maxQuantity - 最大購入数
   * @param  {number} performanceOrderLimit - 購入上限枚数:perormance.order-limit
   * @param  {number} eventOrderLimit - 購入上限枚数:event.order-limit
   * @param  {number} quantity - 枚数
   * @return {boolean}
   */
    QuentityCheckService.prototype.maxLimitCheck = function (maxQuantity, performanceOrderLimit, eventOrderLimit, quantity) {
        if (maxQuantity) {
            if (quantity > maxQuantity) {
                return false;
            }
        }
        else {
            if (performanceOrderLimit) {
                if (quantity > performanceOrderLimit) {
                    return false;
                }
            }
            else {
                if (eventOrderLimit) {
                    if (quantity > eventOrderLimit) {
                        return false;
                    }
                }
                else {
                    if (quantity > this.defaultMaxQuantity) {
                        return false;
                    }
                }
            }
        }
        return true;
    };
    /**
  * 購入下限枚数チェックを行います
  *
  * @param  {number} minQuantity - 最小購入数
  * @param  {number} quantity - 枚数
  * @return {boolean}
  */
    QuentityCheckService.prototype.minLimitCheck = function (minQuantity, quantity) {
        if (minQuantity) {
            if (quantity < minQuantity) {
                return false;
            }
        }
        else {
            if (quantity < this.defaultMinQuantity) {
                return false;
            }
        }
        return true;
    };
    /**
  * 販売単位のチェックを行います
  * 席種の中でその選択席数がその販売単位の倍数ではない場合、エラーとする。
  * @param  {IProducts[]} products - 商品情報
  * @param  {number} quantity - 選択座席数
  * @return {number}
  */
    QuentityCheckService.prototype.salesUnitCheck = function (products, quantity) {
        var FALSE_NUMBER = 1;
        var salesUnitNumber = null;
        var result = null;
        for (var i = 0, len = products.length; i < len; i++) {
            salesUnitNumber = null;
            for (var j = 0, len_1 = products[i].product_items.length; j < len_1; j++) {
                if (products[i].product_items[j].sales_unit_quantity) {
                    salesUnitNumber += products[i].product_items[j].sales_unit_quantity;
                }
            }
            if ((quantity % salesUnitNumber) == 0) {
                return null;
            }
            else {
                result = salesUnitNumber;
            }
        }
        return result;
    };
    /**
   * 枚数選択表示用配列作成、販売単位1を削除する関数
   * @param  {IProducts[]} products - 商品情報
   * @return {number[]}
   */
    QuentityCheckService.prototype.eraseOne = function (products) {
        var ERASE_NUMBER = 1;
        var result = [];
        for (var i = 0, len = products.length; i < len; i++) {
            var sum = null;
            for (var j = 0, len_2 = products[i].product_items.length; j < len_2; j++) {
                if (products[i].product_items.length == 1 && products[i].product_items[0].sales_unit_quantity == ERASE_NUMBER) {
                    result.push(null);
                    break;
                }
                else {
                    sum += products[i].product_items[j].sales_unit_quantity;
                }
            }
            if (sum) {
                result.push(sum);
            }
        }
        return result;
    };
    QuentityCheckService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], QuentityCheckService);
    return QuentityCheckService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/quentity-check.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/seat-status.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return SeatStatusService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__api_base_service__ = __webpack_require__("../../../../../src/app/shared/services/api-base.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__);
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};






var SeatStatusService = (function (_super) {
    __extends(SeatStatusService, _super);
    function SeatStatusService(backend, options, errorModalDataService, _logger) {
        _super.call(this, backend, options, errorModalDataService, _logger);
    }
    /**
     * 座席確保
     * @param  {number}     performanceId 公演ID
     * @param  {number}     salesSegmentId 販売セグメントID
     * @return {Observable} see http.post()
     */
    SeatStatusService.prototype.seatReserve = function (performanceId, salesSegmentId, data) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.SEATS_RESERVE.replace(/{:performance_id}/, performanceId + '')
            .replace(/{:sales_segment_id}/, salesSegmentId + '');
        return this.httpPost(url, data);
    };
    /**
    * 座席解放
    * @param  {number}     performanceId 公演ID
    * @return {Observable} see http.post()
    */
    SeatStatusService.prototype.seatRelease = function (performanceId) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.SEATS_RELEASE.replace(/{:performance_id}/, performanceId + '');
        return this.httpPost(url);
    };
    SeatStatusService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"]) === 'function' && _d) || Object])
    ], SeatStatusService);
    return SeatStatusService;
    var _a, _b, _c, _d;
}(__WEBPACK_IMPORTED_MODULE_2__api_base_service__["a" /* ApiBase */]));
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/seat-status.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/seats.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return SeatsService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__api_base_service__ = __webpack_require__("../../../../../src/app/shared/services/api-base.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__);
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};






var SeatsService = (function (_super) {
    __extends(SeatsService, _super);
    function SeatsService(backend, options, errorModalDataService, _logger) {
        _super.call(this, backend, options, errorModalDataService, _logger);
    }
    /**
     * 座席情報検索:Get
     * @param  {number}     performanceId 公演ID
     * @param  {object}     params   検索条件
     * @return {Observable} see http.get()
     */
    SeatsService.prototype.findSeatsByPerformanceId = function (performanceId, params) {
        var seatsUrl = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.SEATS.replace(/{:performance_id}/, performanceId + '');
        if (params) {
            var serialized = this.serialize(params);
            seatsUrl += "?" + serialized;
        }
        return this.httpGet(seatsUrl);
    };
    /**
     * @param  {Object} obj - The system setup to be url encoded
     * @returns URLSearchParams - The url encoded system setup
     */
    SeatsService.prototype.serialize = function (obj) {
        var params = new __WEBPACK_IMPORTED_MODULE_1__angular_http__["URLSearchParams"]();
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                var element = obj[key];
                params.set(key, element);
            }
        }
        return params;
    };
    SeatsService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"]) === 'function' && _d) || Object])
    ], SeatsService);
    return SeatsService;
    var _a, _b, _c, _d;
}(__WEBPACK_IMPORTED_MODULE_2__api_base_service__["a" /* ApiBase */]));
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/seats.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/select-product.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return SelectProductService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__api_base_service__ = __webpack_require__("../../../../../src/app/shared/services/api-base.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__);
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};






var SelectProductService = (function (_super) {
    __extends(SelectProductService, _super);
    function SelectProductService(backend, options, errorModalDataService, _logger) {
        _super.call(this, backend, options, errorModalDataService, _logger);
    }
    /**
     * 商品選択
     * @param  {number}     performanceId 公演ID
     * @return {Observable} see http.post()
     */
    SelectProductService.prototype.selectProduct = function (performanceId, data) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.SELECT_PRODUCT.replace(/{:performance_id}/, performanceId + '');
        return this.httpPost(url, data);
    };
    SelectProductService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5_angular2_logger_core__["Logger"]) === 'function' && _d) || Object])
    ], SelectProductService);
    return SelectProductService;
    var _a, _b, _c, _d;
}(__WEBPACK_IMPORTED_MODULE_2__api_base_service__["a" /* ApiBase */]));
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/select-product.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/smartPhone-check.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return SmartPhoneCheckService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};

var SmartPhoneCheckService = (function () {
    function SmartPhoneCheckService() {
    }
    /**
   * iphone,ipod,androidかチェックを行います
   *
   * @return {boolean}
   */
    SmartPhoneCheckService.prototype.isSmartPhone = function () {
        if (navigator.userAgent.indexOf('iPhone') > 0 || navigator.userAgent.indexOf('iPod') > 0 || navigator.userAgent.indexOf('Android') > 0) {
            return true;
        }
        return false;
    };
    SmartPhoneCheckService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], SmartPhoneCheckService);
    return SmartPhoneCheckService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/smartPhone-check.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/stock-type-data.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockTypeDataService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__ = __webpack_require__("../../../../rxjs/Subject.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


var StockTypeDataService = (function () {
    function StockTypeDataService() {
        this.toQuentityDataStockTypeId = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        this.toSeatListDisplayFlag = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        this.toIsSearchFlag = new __WEBPACK_IMPORTED_MODULE_1_rxjs_Subject__["Subject"]();
        // Observable streams
        this.toQuentityData$ = this.toQuentityDataStockTypeId.asObservable();
        this.toSeatListFlag$ = this.toSeatListDisplayFlag.asObservable();
        this.toIsSearchFlag$ = this.toIsSearchFlag.asObservable();
    }
    // Service message commands
    StockTypeDataService.prototype.sendToQuentity = function (stockTypeId) {
        this.toQuentityDataStockTypeId.next(stockTypeId);
    };
    StockTypeDataService.prototype.sendToSeatListFlag = function (flag) {
        this.toSeatListDisplayFlag.next(flag);
    };
    StockTypeDataService.prototype.sendToIsSearchFlag = function (flag) {
        this.toIsSearchFlag.next(flag);
    };
    StockTypeDataService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [])
    ], StockTypeDataService);
    return StockTypeDataService;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/stock-type-data.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/stock-types-resolver.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockTypesResolver; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_router__ = __webpack_require__("../../../router/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__ = __webpack_require__("../../../../rxjs/Rx.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__services_stock_types_service__ = __webpack_require__("../../../../../src/app/shared/services/stock-types.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__);
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};





var StockTypesResolver = (function () {
    function StockTypesResolver(performanceService, router, _logger) {
        this.performanceService = performanceService;
        this.router = router;
        this._logger = _logger;
    }
    /**
     * Resolve stock types by performance id in url params
     * @param  {ActivatedRouteSnapshot} route Current route
     * @return {Observable<any>}
     */
    StockTypesResolver.prototype.resolve = function (route) {
        var _this = this;
        if (!route.params || !route.params['performance_id']) {
            var message = "Error: performance_id not exists in url";
            this._logger.error(message);
            return __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__["Observable"].throw(message);
        }
        var performanceId = route.params['performance_id'];
        var findStockTypesByPerformanceId = this.performanceService.findStockTypesByPerformanceId(performanceId);
        findStockTypesByPerformanceId.subscribe(function (response) {
            _this._logger.debug("StockTypes(performance id:" + performanceId + ") has been fetched.", response);
        }, function (error) {
            var message = "Error: StockTypes(performance_id:${performanceId}) could not fetched.";
            _this._logger.error(message + error);
            return __WEBPACK_IMPORTED_MODULE_2_rxjs_Rx__["Observable"].throw(message);
        });
        return findStockTypesByPerformanceId;
    };
    StockTypesResolver = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_3__services_stock_types_service__["a" /* StockTypesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_3__services_stock_types_service__["a" /* StockTypesService */]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_router__["Router"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4_angular2_logger_core__["Logger"]) === 'function' && _c) || Object])
    ], StockTypesResolver);
    return StockTypesResolver;
    var _a, _b, _c;
}());
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/stock-types-resolver.service.js.map

/***/ }),

/***/ "../../../../../src/app/shared/services/stock-types.service.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return StockTypesService; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_http__ = __webpack_require__("../../../http/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__api_base_service__ = __webpack_require__("../../../../../src/app/shared/services/api-base.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_constants__ = __webpack_require__("../../../../../src/app/app.constants.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__ = __webpack_require__("../../../../../src/app/shared/services/error-modal-data.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__performances_service__ = __webpack_require__("../../../../../src/app/shared/services/performances.service.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__);
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};







var StockTypesService = (function (_super) {
    __extends(StockTypesService, _super);
    function StockTypesService(backend, options, errorModalDataService, _logger, performances) {
        _super.call(this, backend, options, errorModalDataService, _logger);
        this.performances = performances;
    }
    /**
   * 席種情報取得
   * @param {number} performanceId 公演ID
   * @param {number} salesSegmentId 販売ID
   * @param {number} stockTypeId 席種ID
   * @return {Observable} see http.get()
   */
    StockTypesService.prototype.getStockType = function (performanceId, salesSegmentId, stockTypeId) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.STOCK_TYPE.replace(/{:performance_id}/, performanceId + '')
            .replace(/{:sales_segment_id}/, salesSegmentId + '')
            .replace(/{:stock_type_id}/, stockTypeId + '');
        return this.httpGet(url, true);
    };
    /**
     * 席種情報検索
     * @param  {number}     performanceId 公演ID
     * @return {Observable} see http.get()
     */
    StockTypesService.prototype.findStockTypesByPerformanceId = function (performanceId) {
        var _this = this;
        return this.performances.getPerformance(performanceId).flatMap(function (response) {
            var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.STOCK_TYPES.replace(/{:performance_id}/, performanceId + '')
                .replace(/{:sales_segment_id}/, response.data.performance.sales_segments[0].sales_segment_id + '');
            return _this.httpGet(url);
        }).share();
    };
    /**
     * 全席種情報取得
     * @param {number} performanceId 公演ID
     * @param {number} salesSegmentId 販売ID
     * @return {Observable} see http.get()
     */
    StockTypesService.prototype.getStockTypesAll = function (performanceId, salesSegmentId) {
        var url = "" + __WEBPACK_IMPORTED_MODULE_3__app_constants__["a" /* ApiConst */].API_URL.STOCK_TYPES_ALL.replace(/{:performance_id}/, performanceId + '')
            .replace(/{:sales_segment_id}/, salesSegmentId + '');
        return this.httpGet(url, true);
    };
    StockTypesService = __decorate([
        Object(__WEBPACK_IMPORTED_MODULE_0__angular_core__["Injectable"])(), 
        __metadata('design:paramtypes', [(typeof (_a = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["XHRBackend"]) === 'function' && _a) || Object, (typeof (_b = typeof __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_1__angular_http__["RequestOptions"]) === 'function' && _b) || Object, (typeof (_c = typeof __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_4__error_modal_data_service__["a" /* ErrorModalDataService */]) === 'function' && _c) || Object, (typeof (_d = typeof __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__["Logger"] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_6_angular2_logger_core__["Logger"]) === 'function' && _d) || Object, (typeof (_e = typeof __WEBPACK_IMPORTED_MODULE_5__performances_service__["a" /* PerformancesService */] !== 'undefined' && __WEBPACK_IMPORTED_MODULE_5__performances_service__["a" /* PerformancesService */]) === 'function' && _e) || Object])
    ], StockTypesService);
    return StockTypesService;
    var _a, _b, _c, _d, _e;
}(__WEBPACK_IMPORTED_MODULE_2__api_base_service__["a" /* ApiBase */]));
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/stock-types.service.js.map

/***/ }),

/***/ "../../../../../src/environments/environment.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return environment; });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_angular2_logger_core__ = __webpack_require__("../../../../angular2-logger/core.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_angular2_logger_core___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_angular2_logger_core__);

var environment = {
    production: true,
    logger: {
        level: __WEBPACK_IMPORTED_MODULE_0_angular2_logger_core__["Level"].WARN
    }
};
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/environment.js.map

/***/ }),

/***/ "../../../../../src/main.ts":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__angular_platform_browser_dynamic__ = __webpack_require__("../../../platform-browser-dynamic/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__angular_core__ = __webpack_require__("../../../core/index.js");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2__environments_environment__ = __webpack_require__("../../../../../src/environments/environment.ts");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__app_app_module__ = __webpack_require__("../../../../../src/app/app.module.ts");




if (__WEBPACK_IMPORTED_MODULE_2__environments_environment__["a" /* environment */].production) {
    Object(__WEBPACK_IMPORTED_MODULE_1__angular_core__["enableProdMode"])();
}
Object(__WEBPACK_IMPORTED_MODULE_0__angular_platform_browser_dynamic__["a" /* platformBrowserDynamic */])().bootstrapModule(__WEBPACK_IMPORTED_MODULE_3__app_app_module__["a" /* AppModule */]);
//# sourceMappingURL=/srv/altair/master/tools/spa_cart/altair-new-cart-20170927092254/src/main.js.map

/***/ }),

/***/ 0:
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__("../../../../../src/main.ts");


/***/ })

},[0]);
var _rollbarConfig = {
  accessToken: "9b73abba03a846dcb6bb06333d7c0b33",
  captureUncaught: true,
  payload: {
    environment: location.protocol=="https:" ? location.hostname.split(".")[1] : "unknown"
  }
};
!function(r){function e(t){if(o[t])return o[t].exports;var n=o[t]={exports:{},id:t,loaded:!1};return r[t].call(n.exports,n,n.exports,e),n.loaded=!0,n.exports}var o={};return e.m=r,e.c=o,e.p="",e(0)}([function(r,e,o){"use strict";var t=o(1).Rollbar,n=o(2);_rollbarConfig.rollbarJsUrl=_rollbarConfig.rollbarJsUrl||"https://d37gvrvc0wt4s1.cloudfront.net/js/v1.9/rollbar.min.js";var a=t.init(window,_rollbarConfig),i=n(a,_rollbarConfig);a.loadFull(window,document,!_rollbarConfig.async,_rollbarConfig,i)},function(r,e){"use strict";function o(r){return function(){try{return r.apply(this,arguments)}catch(e){try{console.error("[Rollbar]: Internal error",e)}catch(o){}}}}function t(r,e,o){window._rollbarWrappedError&&(o[4]||(o[4]=window._rollbarWrappedError),o[5]||(o[5]=window._rollbarWrappedError._rollbarContext),window._rollbarWrappedError=null),r.uncaughtError.apply(r,o),e&&e.apply(window,o)}function n(r){var e=function(){var e=Array.prototype.slice.call(arguments,0);t(r,r._rollbarOldOnError,e)};return e.belongsToShim=!0,e}function a(r){this.shimId=++c,this.notifier=null,this.parentShim=r,this._rollbarOldOnError=null}function i(r){var e=a;return o(function(){if(this.notifier)return this.notifier[r].apply(this.notifier,arguments);var o=this,t="scope"===r;t&&(o=new e(this));var n=Array.prototype.slice.call(arguments,0),a={shim:o,method:r,args:n,ts:new Date};return window._rollbarShimQueue.push(a),t?o:void 0})}function l(r,e){if(e.hasOwnProperty&&e.hasOwnProperty("addEventListener")){var o=e.addEventListener;e.addEventListener=function(e,t,n){o.call(this,e,r.wrap(t),n)};var t=e.removeEventListener;e.removeEventListener=function(r,e,o){t.call(this,r,e&&e._wrapped?e._wrapped:e,o)}}}var c=0;a.init=function(r,e){var t=e.globalAlias||"Rollbar";if("object"==typeof r[t])return r[t];r._rollbarShimQueue=[],r._rollbarWrappedError=null,e=e||{};var i=new a;return o(function(){if(i.configure(e),e.captureUncaught){i._rollbarOldOnError=r.onerror,r.onerror=n(i);var o,a,c="EventTarget,Window,Node,ApplicationCache,AudioTrackList,ChannelMergerNode,CryptoOperation,EventSource,FileReader,HTMLUnknownElement,IDBDatabase,IDBRequest,IDBTransaction,KeyOperation,MediaController,MessagePort,ModalWindow,Notification,SVGElementInstance,Screen,TextTrack,TextTrackCue,TextTrackList,WebSocket,WebSocketWorker,Worker,XMLHttpRequest,XMLHttpRequestEventTarget,XMLHttpRequestUpload".split(",");for(o=0;o<c.length;++o)a=c[o],r[a]&&r[a].prototype&&l(i,r[a].prototype)}return e.captureUnhandledRejections&&(i._unhandledRejectionHandler=function(r){var e=r.reason,o=r.promise,t=r.detail;!e&&t&&(e=t.reason,o=t.promise),i.unhandledRejection(e,o)},r.addEventListener("unhandledrejection",i._unhandledRejectionHandler)),r[t]=i,i})()},a.prototype.loadFull=function(r,e,t,n,a){var i=function(){var e;if(void 0===r._rollbarPayloadQueue){var o,t,n,i;for(e=new Error("rollbar.js did not load");o=r._rollbarShimQueue.shift();)for(n=o.args,i=0;i<n.length;++i)if(t=n[i],"function"==typeof t){t(e);break}}"function"==typeof a&&a(e)},l=!1,c=e.createElement("script"),p=e.getElementsByTagName("script")[0],d=p.parentNode;c.crossOrigin="",c.src=n.rollbarJsUrl,c.async=!t,c.onload=c.onreadystatechange=o(function(){if(!(l||this.readyState&&"loaded"!==this.readyState&&"complete"!==this.readyState)){c.onload=c.onreadystatechange=null;try{d.removeChild(c)}catch(r){}l=!0,i()}}),d.insertBefore(c,p)},a.prototype.wrap=function(r,e){try{var o;if(o="function"==typeof e?e:function(){return e||{}},"function"!=typeof r)return r;if(r._isWrap)return r;if(!r._wrapped){r._wrapped=function(){try{return r.apply(this,arguments)}catch(e){throw"string"==typeof e&&(e=new String(e)),e._rollbarContext=o()||{},e._rollbarContext._wrappedSource=r.toString(),window._rollbarWrappedError=e,e}},r._wrapped._isWrap=!0;for(var t in r)r.hasOwnProperty(t)&&(r._wrapped[t]=r[t])}return r._wrapped}catch(n){return r}};for(var p="log,debug,info,warn,warning,error,critical,global,configure,scope,uncaughtError,unhandledRejection".split(","),d=0;d<p.length;++d)a.prototype[p[d]]=i(p[d]);r.exports={Rollbar:a,_rollbarWindowOnError:t}},function(r,e){"use strict";r.exports=function(r,e){return function(o){if(!o&&!window._rollbarInitialized){var t=window.RollbarNotifier,n=e||{},a=n.globalAlias||"Rollbar",i=window.Rollbar.init(n,r);i._processShimQueue(window._rollbarShimQueue||[]),window[a]=i,window._rollbarInitialized=!0,t.processPayloads()}}}}]);
