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
export class SeatDataService extends ApiBase{


  constructor(backend: XHRBackend,
            options: RequestOptions,
            errorModalDataService: ErrorModalDataService,
            _logger: Logger,
            private performances: PerformancesService) {
    super(backend, options, errorModalDataService, _logger);

  }
  /**
   * 個席データ取得
   * @return {Observable} see http.get()
   */
  getSeatData(): Observable<any | IErrorResponse> {
    const url = "../../assets/newSeatElements.json";
    //const url = "../../assets/seatDataEls.zip";
    return this.httpGetSeat(url, false);
  }

  /**
   * 全席種情報取得
   * @param {number} performanceId 公演ID
   * @param {number} salesSegmentId 販売ID
   * @return {Observable} see http.get()

    getStockTypesAll(performanceId: number, salesSegmentId: number): Observable<IStockTypesAllResponse | IErrorResponse> {
      const url = `${ApiConst.API_URL.STOCK_TYPES_ALL.replace(/{:performance_id}/, performanceId + '')
        .replace(/{:sales_segment_id}/, salesSegmentId + '')}`;
      return this.httpGet(url, true);
    }
    */
}