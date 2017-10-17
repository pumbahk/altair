import { Injectable, EventEmitter } from '@angular/core';
import { XHRBackend, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import { ApiBase }  from './api-base.service';
import { ISuccessResponse, IErrorResponse, ISelectProductResponse}  from './interfaces';
import { ApiConst } from '../../app.constants';
import { ErrorModalDataService } from './error-modal-data.service';
import { Logger } from "angular2-logger/core";


@Injectable()
export class SelectProductService extends ApiBase {

  //商品選択レスポンス
  selectProdustResponse: ISelectProductResponse;

  constructor(backend: XHRBackend,
            options: RequestOptions,
            errorModalDataService: ErrorModalDataService,
            _logger: Logger) {
    super(backend, options, errorModalDataService, _logger);

  }

  /**
   * 商品選択
   * @param  {number}     performanceId 公演ID
   * @return {Observable} see http.post()
   */
  selectProduct(performanceId: number,data: {}): Observable<ISelectProductResponse | IErrorResponse> {
    const url = `${ApiConst.API_URL.SELECT_PRODUCT.replace(/{:performance_id}/, performanceId + '')}`;
    return this.httpPost(url,data);
  }

}
