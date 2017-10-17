import { Injectable, EventEmitter } from '@angular/core';
import { XHRBackend, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiBase }  from './api-base.service';
import { ISuccessResponse, IErrorResponse, IStockTypeResponse, IStockTypesResponse, IStockTypesAllResponse,
          IStockType, IPerformanceInfoResponse, ISalesSegment}  from './interfaces';
import { ApiConst } from '../../app.constants';
import { ErrorModalDataService } from './error-modal-data.service';
import { PerformancesService } from './performances.service';
import { Logger } from "angular2-logger/core";


@Injectable()
export class StockTypesService extends ApiBase{


  constructor(backend: XHRBackend,
            options: RequestOptions,
            errorModalDataService: ErrorModalDataService,
            _logger: Logger,
            private performances: PerformancesService) {
    super(backend, options, errorModalDataService, _logger);

  }

  /**
 * 席種情報取得
 * @param {number} performanceId 公演ID
 * @param {number} salesSegmentId 販売ID
 * @param {number} stockTypeId 席種ID
 * @return {Observable} see http.get()
 */
  getStockType(performanceId: number, salesSegmentId: number, stockTypeId: number): Observable<IStockTypeResponse | IErrorResponse> {
    const url = `${ApiConst.API_URL.STOCK_TYPE.replace(/{:performance_id}/, performanceId + '')
      .replace(/{:sales_segment_id}/, salesSegmentId + '')
      .replace(/{:stock_type_id}/, stockTypeId + '')}`;
    return this.httpGet(url, true);
  }
  /**
   * 席種情報検索
   * @param  {number}     performanceId 公演ID
   * @return {Observable} see http.get()
   */
  findStockTypesByPerformanceId(performanceId: number): Observable<IStockTypesResponse | IErrorResponse> {

    return this.performances.getPerformance(performanceId).flatMap((response: IPerformanceInfoResponse) => {
      const url = `${ApiConst.API_URL.STOCK_TYPES.replace(/{:performance_id}/, performanceId + '')
        .replace(/{:sales_segment_id}/, response.data.performance.sales_segments[0].sales_segment_id + '')}`;
      return this.httpGet(url);
    }).share();
  }

  /**
   * 全席種情報取得
   * @param {number} performanceId 公演ID
   * @param {number} salesSegmentId 販売ID
   * @return {Observable} see http.get()
   */
    getStockTypesAll(performanceId: number, salesSegmentId: number): Observable<IStockTypesAllResponse | IErrorResponse> {
      const url = `${ApiConst.API_URL.STOCK_TYPES_ALL.replace(/{:performance_id}/, performanceId + '')
        .replace(/{:sales_segment_id}/, salesSegmentId + '')}`;
      return this.httpGet(url, true);
    }
}
