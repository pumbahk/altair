import { Injectable, EventEmitter } from '@angular/core';
import { XHRBackend, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiBase }  from './api-base.service';
import { ISuccessResponse, IErrorResponse, IPerformanceInfoResponse, IPerformancesResponse, IPerformance}  from './interfaces';
import { ApiConst } from '../../app.constants';
import { ErrorModalDataService } from './error-modal-data.service';
import { Logger } from "angular2-logger/core";


@Injectable()
export class PerformancesService extends ApiBase{

  private performance: IPerformance;

  constructor(backend: XHRBackend,
              options: RequestOptions,
              errorModalDataService: ErrorModalDataService,
              _logger: Logger) {
    super(backend, options, errorModalDataService, _logger);

  }
  /**
   * 公演情報取得
   * @param {number} performanceId 公演ID
   * @return {Observable} see http.get()
   */
  getPerformance(performanceId: number): Observable<IPerformanceInfoResponse | IErrorResponse> {

    const url = `${ApiConst.API_URL.PERFORMANCE_INfO.replace(/{:performance_id}/, performanceId + '')}`;
    var httpGet = this.httpGet(url, true).map((response: IPerformanceInfoResponse) => {
      response.data.performance.sales_segments = response.data.sales_segments;
      return response;
    }).share();
    return httpGet;
  }

  /**
   * 公演情報検索
   * @param  {number}     eventId イベントID
   * @return {Observable} see http.get()
   */
  findPerformancesByEventId(eventId: number): Observable<IPerformancesResponse | IErrorResponse> {
    const url = `${ApiConst.API_URL.PERFORMANCES.replace(/{:event_id}/, eventId + '')}`;
    return this.httpGet(url);
  }
}