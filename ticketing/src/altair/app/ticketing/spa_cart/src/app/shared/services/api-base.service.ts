import { Injectable }  from '@angular/core';
import { Http, XHRBackend, RequestOptions, Request, RequestOptionsArgs, ResponseContentType, Response, Headers } from '@angular/http';
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
   * JsonDataGETリクエストを実行します
   *
   * @param string url - API-URL
   * @return Observable<T> - Observable関数
   * @return null - 通信エラー
   */
  protected httpGetJsonData<T>(url: string): Observable<T> {
    var Zlib = require('zlibjs/bin/gunzip.min').Zlib;
    this._logger.debug('API GET:', url);
    let seat_options: RequestOptionsArgs = {};
    seat_options.responseType = ResponseContentType.ArrayBuffer;
    var get = this.get(url, seat_options)
      .timeout(60000)
      .map((response) => {
        var plain;
        var asciistring = '';
        var uint8array = new Uint8Array(response.arrayBuffer());
        var gunzip = new Zlib.Gunzip(uint8array);
        try {
          plain = gunzip.decompress();
        } catch (e) {
          plain = new Uint8Array(response.arrayBuffer());
        }
        if (typeof(plain.slice) !== 'function') {
          for (let i = 0; i < plain.length; i++) {
            asciistring += String.fromCharCode(plain[i]);
          }
        } else {
          const block_size = 1024;
          for (let i = 0; i < plain.length; i += block_size) {
            if (i + block_size >= plain.length) {
              asciistring += String.fromCharCode.apply(String, plain.slice(i));
            } else {
              asciistring += String.fromCharCode.apply(String, plain.slice(i, i + block_size));
            }
          }
        }
        const body = JSON.parse(asciistring);
        return body;
      })
      .catch(error => this.handleError(error))
      .share();
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
      const status = error.status;
      if (status == 0) {
        errMsg = `${ApiConst.SERVER_DNS_ERROR}`;
      } else if (status == 500) {
        errMsg = `${ApiConst.INTERNAL_SERVER_ERROR}`;
      } else if (status == 503) {
        errMsg = `${ApiConst.SERVICE_UNAVAILABLE}`;
      } else {
        errMsg = `${error.status} - ${error.statusText}`;
      }
    } else {
      errMsg = error.message ? error.message : error.toString();
    }
    this._logger.error(errMsg);
    this.callErrorModal(errMsg);
    return Observable.throw(errMsg);
  }
  private callErrorModal(errMsg:string) {
    if (errMsg == `${ApiConst.TIMEOUT}` || errMsg == `${ApiConst.SERVER_DNS_ERROR}`) {
      this.errorModalDataService.sendToErrorModal(
        '通信エラー発生',
        'インターネットに未接続または通信が不安定な可能性があります。通信環境の良いところで操作をやり直すかページを再読込してください。'
      );
    } else if (errMsg == `${ApiConst.INTERNAL_SERVER_ERROR}`) {
      this.errorModalDataService.sendToErrorModal(
        'サーバーエラー発生',
        '予期しないエラーが発生しました。操作をやり直すかページを再読込してください。'
      );
    } else if (errMsg == `${ApiConst.SERVICE_UNAVAILABLE}`) {
      this.errorModalDataService.sendToErrorModal(
        'メンテナンス中',
        'ただいまメンテナンス中のため、一時的にサービスをご利用いただけません。'
      );
    } else {
      this.errorModalDataService.sendToErrorModal(
        'その他エラー発生',
        '予期しないエラーが発生しました。操作をやり直すかページを再読込してください。'
      );
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