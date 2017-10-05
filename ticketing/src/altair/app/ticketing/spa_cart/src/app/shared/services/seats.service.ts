/*以下のAPIを呼び出し情報の取得管理を行うサービス（Injectable）。
・座席情報検索　http://dev.altair-spa.tk/cart_api/api/v1/performances/{performanceId}/seats
*/
import { Injectable, EventEmitter } from '@angular/core';
import { XHRBackend, RequestOptions, Http, URLSearchParams } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiBase }  from './api-base.service';
import {
  ISuccessResponse,
  IErrorResponse,
  ISeatsResponse,
  ISeatsRequest,
  IStockType
} from './interfaces';
import { ApiConst } from '../../app.constants';
import { ErrorModalDataService } from './error-modal-data.service';
import { Logger } from "angular2-logger/core";


@Injectable()
export class SeatsService extends ApiBase{

  constructor(backend: XHRBackend,
              options: RequestOptions,
              errorModalDataService: ErrorModalDataService,
              _logger: Logger) {
    super(backend, options, errorModalDataService, _logger);

  }

  /**
   * 座席情報検索:Get
   * @param  {number}     performanceId 公演ID
   * @param  {object}     params   検索条件
   * @return {Observable} see http.get()
   */
  findSeatsByPerformanceId(performanceId: number, params?: ISeatsRequest): Observable<ISeatsResponse | IErrorResponse> {
    let seatsUrl = `${ApiConst.API_URL.SEATS.replace(/{:performance_id}/, performanceId + '')}`;
    if(params){
      let serialized: URLSearchParams = this.serialize(params);
      seatsUrl += "?" + serialized;
    }
    return this.httpGet(seatsUrl);
  }

/**
 * @param  {Object} obj - The system setup to be url encoded
 * @returns URLSearchParams - The url encoded system setup
 */
  private serialize(obj: Object): URLSearchParams {
    let params: URLSearchParams = new URLSearchParams();
    for (var key in obj) {
      if (obj.hasOwnProperty(key)) {
        var element = obj[key];
        params.set(key, element);
      }
    }
    return params;
  }
}