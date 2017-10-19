import { Injectable } from '@angular/core';
/************************************************************************************
 *
 * 定数クラス
 *
 ***********************************************************************************/

/**
 * @class API関連 定数管理
 */
export class ApiConst {

  // APIのパス以前のURL（スキーム, ドメイン, ベースパス）になります
  // public static API_BASE_URL = 'http://dev.altair-spa.tk/cart_api/api/v1/';
  public static API_BASE_URL = '/cart_api/api/v1/';

  // 各APIのURLになります
  public static API_URL = {

    // 公演情報検索API
    PERFORMANCES:     `${ApiConst.API_BASE_URL}events/{:event_id}/performances`,

    // 公演情報API
    PERFORMANCE_INfO: `${ApiConst.API_BASE_URL}performances/{:performance_id}`,

    // 席種情報検索API
    STOCK_TYPES:      `${ApiConst.API_BASE_URL}performances/{:performance_id}/sales_segments/{:sales_segment_id}/stock_types`,

    // 席種情報API
    STOCK_TYPE: `${ApiConst.API_BASE_URL}performances/{:performance_id}/sales_segments/{:sales_segment_id}/stock_types/{:stock_type_id}`,

    // 席種情報API
    STOCK_TYPES_ALL: `${ApiConst.API_BASE_URL}performances/{:performance_id}/sales_segments/{:sales_segment_id}/stock_types/all`,

    // 座席情報検索API
    SEATS:            `${ApiConst.API_BASE_URL}performances/{:performance_id}/seats`,

    // 座席確保
    SEATS_RESERVE:    `${ApiConst.API_BASE_URL}performances/{:performance_id}/sales_segments/{:sales_segment_id}/seats/reserve`,

    // 座席解放
    SEATS_RELEASE:    `${ApiConst.API_BASE_URL}performances/{:performance_id}/seats/release`,

    // 商品選択
    SELECT_PRODUCT:    `${ApiConst.API_BASE_URL}performances/{:performance_id}/select_products`,
  };

  //通信断時のエラー
  public static TIMEOUT = 'Timeout has occurred';
  //DNSエラー
  public static SERVERDNSERROR = 'server dns error';
  //ダウンエラー
  public static SERVERDOWNERROR = 'server down error';
}
@Injectable()
export class AppConstService{

  // サイトのパス以前のURL（スキーム, ドメイン, ベースパス）になります
  public static APP_BASE_URL = 'public/';

  // アセッツルート 画像等のファイル関連設置場所になります
  public static ASSETS_ROOT = '/public/assets/';

  // 画像の設置場所になります
  public static IMG_ROOT = `${AppConstService.ASSETS_ROOT}img/`;

  // 各ページのURLになります
  public static PAGE_URL = {

    // トップページ
    TOP: `https://eagles.tstar.jp/`,

    // 支払ページ
    PAYMENT: `${AppConstService.APP_BASE_URL}payment`,

    // 枚数選択
    RESERVE_BY_QUANTITY: `${AppConstService.APP_BASE_URL}reserve-by-quantity`,

    //商品選択
    SELECT_PRODUCT: `${AppConstService.APP_BASE_URL}select-product`,
  };
}