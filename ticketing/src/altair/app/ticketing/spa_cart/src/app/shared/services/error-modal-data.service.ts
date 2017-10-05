import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class ErrorModalDataService {

  constructor() { }

  //private toQuentityDataStockTypeId = new Subject<number>();

  //private errorDisplay = new Subject<boolean>();
  private errorTitle = new Subject<string>();
  private errorDetail = new Subject<string>();


  // Observable streams
  //public toQuentityData$= this.toQuentityDataStockTypeId.asObservable();

  //public errorDisplay$= this.errorDisplay.asObservable();
  public errorTitle$= this.errorTitle.asObservable();
  public errorDetail$= this.errorDetail.asObservable();

  // Service message commands
  sendToErrorModal(title?: string, detail?: string) {
    // this.toQuentityDataStockTypeId.next(stockTypeId);
    //this.errorDisplay.next(true);
    title = title ? title: 'サーバーと通信できません。';
    this.errorTitle.next(title);
    detail = detail ? detail : 'インターネットに未接続または通信が不安定な可能性があります。通信環境の良いところで操作をやり直すかページを再読込してください。';
    this.errorDetail.next(detail);
  }
}