
/**
 * @interface レスポンス成功時に必ず返却されるパラメータのインタフェースになります
 */
export interface ISuccessResponse {

  /** @type boolean - 成功可否 */
  success: boolean;
}

/**
 * @interface APIエラーレスポンス
 */
export interface IErrorResponse {

  /** @type boolean - 結果ステータス */
  success: boolean;

  /** @type number - HTTPステータスコード */
  code: number;

  /** @type string - エラーコード */
  errorCode: string;

  /** @type string - エラーメッセージ */
  errorMessage: string;
}

/** @interface 公演情報レスポンスインタフェース */
export interface IPerformanceInfoResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IPerformance - 公演情報 */
    performance: IPerformance;

    /** @type ISalesSegment - 販売情報 */
    sales_segments: ISalesSegment[];

    /** @type IEvent - イベント情報 */
    event: IEvent;
  };
}

/** @interface 公演情報検索レスポンスインタフェース */
export interface IPerformancesResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IPerformance[] - 公演情報 */
    performances: IPerformance[];
  };
}

/** @interface 席種情報レスポンスインタフェース */
export interface IStockTypeResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IStockType[] - 席種情報 */
    stock_types: IStockType[];
  };
}

/** @interface 席種情報検索レスポンスインタフェース */
export interface IStockTypesResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IStockTypes[] - 席種情報 */
    stock_types: IStockType[];
  };
}

/** @interface 全席種情報レスポンスインタフェース */
export interface IStockTypesAllResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IStockType - 席種情報 */
    stock_types: IStockType[];
  };
}

/** @interface 座席情報検索レスポンスインタフェース */
export interface ISeatsResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IStockType[] - 席種情報 */
    stock_types: IStockType[];

    /** @type IRegion[] - ブロック情報 */
    regions: IRegion[];

    /** @type ISeat[] - 座席情報 */
    seats: ISeat[];

    /** @type ISeatGroup[] - 座席グループ情報 */
    seat_groups: ISeatGroup[];
  };
}

/** @interface 座席確保レスポンスインタフェース */
export interface ISeatsReserveResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IResult - 座席確保 */
    results: IResult;
  };
}

/** @interface 座席解放レスポンスインタフェース */
export interface ISeatsReleaseResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    /** @type IResult - 座席解放 */
    results: IResult;
  };
}

/** @interface 商品選択レスポンスインタフェース */
export interface ISelectProductResponse extends ISuccessResponse {
  environment: string,
  organization_short_name: string,
  data: {
    results: {
        /** @type string - ステータス */
        status: string;
        /** @type string - 失敗理由 */
        reason: string;
    }
  }
}

/** @interface 公演情報インタフェース */
export interface IPerformance {
  /** @type number - 会場ID */
  venue_id: number;
  /** @type string - 会場名 */
  venue_name: string;
  /** @type number - 購入上限枚数 */
  order_limit: number;
  /** @type string - 公演名 */
  performance_name: string;
  /** @type string - 開場日時 yyyy-mm-dd hh24:mi:ss */
  start_on: string;
  /** @type string - 開演日時 yyyy-mm-dd hh24:mi:ss */
  open_on: string;
  /** @type string - 終演日時 yyyy-mm-dd hh24:mi:ss */
  end_on: string;
  /** @type number - 公演ID */
  performance_id: number;
  /** @type ISalesSegment[] - 販売情報 */
  sales_segments: ISalesSegment[];
  /** @type string - 会場図URL */
  venue_map_url: string;
  /** @type string - ミニ会場図URL */
  mini_venue_map_url: string;
}

/** @interface 販売情報インタフェース */
export interface ISalesSegment {
  /** @type number - 販売区分ID */
  sales_segment_id: number;
  /** @type string - 販売開始日時 yyyy-mm-dd hh24:mi:ss */
  start_at: string;
  /** @type string - 購入上限枚数 */
  order_limit: string;
  /** @type boolean - 座席選択可否 */
  seat_choice: boolean;
  /** @type string - 販売区分名 */
  sales_segment_name: string;
  /** @type string - 販売終了日時 yyyy-mm-dd hh24:mi:ss */
  end_at: string;
}

/** @interface イベント情報インタフェース */
export interface IEvent {
  /** @type number - イベントID */
  event_id: number;
  /** @type number - 購入上限枚数 */
  order_limit: number;
}

/** @interface 席種情報インタフェース */
export interface IStockType {
  /** @type number - 席種ID */
  stock_type_id: number;
  /** @type string - 席種名 */
  stock_type_name: string;
  /** @type boolean - 数受け 「false: 席受け, true: 数受け」*/
  is_quantity_only: boolean;
  /** @type string - 説明 */
  description: string;
  /** @type number - 最小購入数 */
  min_quantity: number;
  /** @type number - 最大購入数 */
  max_quantity: number;
  /** @type number - 最小商品購入数 */
  min_product_quantity: number;
  /** @type number - 最大商品購入数 */
  max_product_quantity: number;
  /** @type string[] - ブロック情報 */
  regions: string[];
  /** @type IProducts[] - 商品インターフェース */
  products: IProducts[];
  /** @type number - 空席数 */
  available_counts: number;
  /** @type string - 在庫状況 */
  stock_status: string;
}

/** @interface 商品インタフェース */
export interface IProducts {
  /** @type number - 商品ID */
  product_id: number;
  /** @type string - 商品名 */
  product_name: string;
  /** @type number - 金額 */
  price: number;
  /** @type number - 最小商品購入数 */
  min_product_quantity: number;
  /** @type number - 最大商品購入数 */
  max_product_quantity: number;
  /** @type boolean - 必須選択 */
  is_must_be_chosen: boolean;
  /** @type IProductItems[] - 商品明細情報インターフェース */
  product_items: IProductItems[];
}

/** @interface 商品明細情報インターフェース */
export interface IProductItems {
  /** @type number - 商品明細ID */
  product_item_id: number;
  /** @type string - 商品明細名 */
  product_item_name: string;
  /** @type number - 金額 */
  price: number;
  /** @type number - 販売単位 */
  sales_unit_quantity: number
}

/** @interface ブロックインタフェース */
export interface IRegion {
  /** @type string - ブロックID */
  region_id: string;
  /** @type string - 在庫状況 */
  stock_status: string;
}

/** @interface 座席インタフェース */
export interface ISeat {
  /** @type string - 座席ID */
  seat_l0_id: string;
  /** @type string - 座席ID */
  seat_id: string;
  /** @type string - 座席名 */
  seat_name: string;
  /** @type string - 商品明細ID */
  product_item_id: number;
  /** @type boolean - 確保可否 */
  is_available: boolean;
  /** @type number - 席種ID */
  stock_type_id: number;
}
/** @interface 座席グループ情報インタフェース */
export interface ISeatGroup {
  /** @type string - 座席グループID */
  seat_group_id: string;
  /** @type string - 座席グループ名 */
  seat_group_name: string;
  /** @type string[] - 座席IDの配列 */
  seat_l0_ids: string[];
}

/** @interface 座席インタフェース */
export interface IResult {
  /** @type string - ステータス */
  status: string;
  /** @type string - 失敗理由 */
  reason: string;
  /** @type string - 確保タイプ */
  reserve_type: string;
  /** @type number - 席種ID */
  stock_type_id: number;
  /** @type number - 枚数 */
  quantity: number;
  /** @type boolean - 数受け */
  is_quantity_only: boolean;
  /** @type boolean - 飛び席 */
  is_separated: boolean;
  /** @type ISeat[] - 座席情報 */
  seats: ISeat[];
  /** @type string[] - 座席名 */
  seat_name: string[];
  /** @type string[] - 座席IDの配列 */
  seat_l0_id: string[];
}

/** @interface 検索パラメータインタフェース */
export interface ISeatsRequest {
  /** @type string - 取得対象情報 */
  fields: string;
  /** @type number - 最小金額 */
  min_price: number;
  /** @type number - 最大金額 */
  max_price: number;
  /** @type string - 席種名 */
  stock_type_name: string;
}

/** @interface 商品選択パラメータインタフェース */
export interface IProductsRequest {
  /** @type string - 数受け */
  is_quantity_only: string;
  /** @type ISelectedProducts[] - 商品情報リスト */
  selected_products: ISelectedProducts[];

}
/** @interface 商品情報リストインタフェース */
export interface ISelectedProducts {
  /** @type string - 座席ID */
  seat_id: string;
  /** @type number - 商品明細ID */
  product_item_id: number;
  /** @type number - 枚数 */
  quantity: number;
}
