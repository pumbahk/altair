import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class ErrorModalDataService {

  constructor() { }

  private errorTitle = new Subject<{msg: string, param: string}>();
  private errorDetail = new Subject<{msg: string, param: string}>();
  private onClosed = new Subject<() => void>();

  public errorTitle$ = this.errorTitle.asObservable();
  public errorDetail$ = this.errorDetail.asObservable();
  public onClosed$ = this.onClosed.asObservable();

  sendToErrorModal(title?: string, detail?: string, onClosed?: () => void, titleStrParam: string = '', detailStrParam: string = '') {
    title = title ? title: 'サーバーと通信できません。';
    this.errorTitle.next({msg: title, param: titleStrParam});
    detail = detail ? detail : 'インターネットに未接続または通信が不安定な可能性があります。通信環境の良いところで操作をやり直すかページを再読込してください。';
    this.errorDetail.next({msg: detail, param: detailStrParam});
    this.onClosed.next(onClosed);
  }

  sendHandlerOnClosedToErrorModal(onClosed: () => void) {
    this.onClosed.next(onClosed);
  }

  sendReloadOnClosedToErrorModal() {
    this.sendHandlerOnClosedToErrorModal(() => {
      window.location.reload(true);
    })
  }
}