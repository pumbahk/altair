/*以下のAPIを呼び出し座席の状態変更を行うサービス（Injectable）。
・座席確保   http://dev.altair-spa.tk/cart_api/api/v1/performances/{preformanceId}/seats/reserve
・座席解放   http://dev.altair-spa.tk/cart_api/api/v1/performances/{performanceId}/seats/release
*/
import { Injectable, EventEmitter } from '@angular/core';
import { XHRBackend, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiBase }  from './api-base.service';
import { ISuccessResponse, IErrorResponse, ISeatsReserveResponse, ISeatsReleaseResponse, IResult}  from './interfaces';
import { ApiConst } from '../../app.constants';
import { ErrorModalDataService } from './error-modal-data.service';
import { Logger } from "angular2-logger/core";


@Injectable()
export class SeatStatusService extends ApiBase {

    //座席確保レスポンス共通データ
    seatReserveResponse: ISeatsReserveResponse;

    constructor(backend: XHRBackend,
              options: RequestOptions,
              errorModalDataService: ErrorModalDataService,
              _logger: Logger) {
      super(backend, options, errorModalDataService, _logger);

    }

  /**
   * 座席確保
   * @param  {number}     performanceId 公演ID
   * @param  {number}     salesSegmentId 販売セグメントID
   * @return {Observable} see http.post()
   */
  seatReserve(performanceId: number,salesSegmentId: number,data: {}): Observable<ISeatsReserveResponse | IErrorResponse> {
    const url = `${ApiConst.API_URL.SEATS_RESERVE.replace(/{:performance_id}/, performanceId + '')
                  .replace(/{:sales_segment_id}/, salesSegmentId + '')}`;
    return this.httpPost(url,data);
  }

   /**
   * 座席解放
   * @param  {number}     performanceId 公演ID
   * @return {Observable} see http.post()
   */
  seatRelease(performanceId: number): Observable<ISeatsReserveResponse | IErrorResponse> {
    const url = `${ApiConst.API_URL.SEATS_RELEASE.replace(/{:performance_id}/, performanceId + '')}`;
    return this.httpPost(url);
  }
}