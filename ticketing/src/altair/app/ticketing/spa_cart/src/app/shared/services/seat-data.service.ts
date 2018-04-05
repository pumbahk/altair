import { Injectable, EventEmitter } from '@angular/core';
import { XHRBackend, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiBase }  from './api-base.service';
import { ISuccessResponse, IErrorResponse}  from './interfaces';
import { ApiConst } from '../../app.constants';
import { ErrorModalDataService } from './error-modal-data.service';
import { Logger } from "angular2-logger/core";


@Injectable()
export class SeatDataService extends ApiBase{


  constructor(backend: XHRBackend,
            options: RequestOptions,
            errorModalDataService: ErrorModalDataService,
            _logger: Logger) {
    super(backend, options, errorModalDataService, _logger);

  }

  //venuemap / filter seat_groups共有フラグ
  isExistsSeatGroupData: boolean = false;

  /**
   * 個席データ取得
   * @return {Observable} see http.get()
   */
  getSeatData(url:string): Observable<any | IErrorResponse> {
    return this.httpGetJsonData(url);
  }

  /**
   * 個席グループデータ取得
   * @return {Observable} see http.get()
   */
  getSeatGroupData(url:string): Observable<any | IErrorResponse> {
    return this.httpGetJsonData(url);
  }
}