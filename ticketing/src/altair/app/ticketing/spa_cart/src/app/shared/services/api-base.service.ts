import { Injectable }  from '@angular/core';
import { Http, XHRBackend, RequestOptions, Request, RequestOptionsArgs, Response, Headers } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import { ISuccessResponse, IErrorResponse } from './interfaces';
import { ErrorModalDataService } from './error-modal-data.service';
// constants
import { ApiConst } from '../../app.constants';
import { Logger } from "angular2-logger/core";


@Injectable()
export class ApiBase extends Http{

  private cachedGetObservables: {};

  constructor(backend: XHRBackend,
              options: RequestOptions,
              private errorModalDataService: ErrorModalDataService,
              private _logger: Logger) {

    super(backend, options);
    this.settingHeader(options);
    this.cachedGetObservables = {};
  }

  /**
   * APIリクエスト時の共通ヘッダーを設定します
   *
   * @param RequestOptions options - リクエストオプション
   */
  protected settingHeader(options: RequestOptions) {
    options.headers = new Headers({
        'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
    });
  }


  /**
   * GETリクエストを実行します
   *
   * @param string url - API-URL
   * @param boolean useCache - Returns cached response if true
   * @return Observable<T> - Observable関数
   * @return null - 通信エラー
   */
  protected httpGet<T>(url: string, useCache: boolean = false): Observable<T> {
    if(useCache && this.cachedGetObservables[url] != undefined){
      this._logger.debug('API GET:', url + ' [CACHED]');
      return this.cachedGetObservables[url];
    }
    this._logger.debug('API GET:', url);
    var get = this.get(url, this.options)
      .timeout(60000)
      .map((response) => {
        const body = response.json();
        this.check401(body);
        this.cachedGetObservables[url] = Observable.of(body);
        return body;
      })
      .catch(error => this.handleError(error))
      .share();
    this.cachedGetObservables[url] = get;
    return get;
  }

  /**
   * POSTリクエストを実行します
   *
   * @param string url - API-URL
   * @param Object data - ポストデータ
   * @return Observable<T> - Observable関数
   * @return null - 通信エラー
   */
  protected httpPost<T>(url: string, data?: {}): Observable<T> {
    this._logger.debug('API POST', url);
    return this.post(url, data, this.options)
      .timeout(60000)
      .map((response) => {
        const body = response.json();
        this.check401(body);
        return body;
      })
      .catch(error => this.handleError(error));
  }

  private handleError(error: Response | any) {
    let errMsg: string;
    if (error instanceof Response) {
      const body = error.json() || '';
      const err = body.error || JSON.stringify(body);
      const status = error.status;
      errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
      if (status == 0) {//サーバー接続エラー
        errMsg = `${ApiConst.SERVERDNSERROR}`;
      } else if (status == 503) {//サーバーダウン
        errMsg = `${ApiConst.SERVERDOWNERROR}`;
      }
    } else {//タイムアウト
      errMsg = error.message ? error.message : error.toString();
    }
      this._logger.error(errMsg);
      this.callErrorModal(errMsg);
      return Observable.throw(errMsg);
  }

  private callErrorModal(errMsg:string) {
    if (errMsg == `${ApiConst.TIMEOUT}` || errMsg == `${ApiConst.SERVERDNSERROR}` || errMsg == `${ApiConst.SERVERDOWNERROR}`) {
      this.errorModalDataService.sendToErrorModal();
    }
  }

  private check401(body) {
    if(body.data.error && body.data.error.code == 401){
      var message = "Error:401 Unauthorized";
      this._logger.error(message);
      this.errorModalDataService.sendToErrorModal('エラー','ログインしてください。')
      window.location.reload();
      throw new Error(message);
    }
  }
}
