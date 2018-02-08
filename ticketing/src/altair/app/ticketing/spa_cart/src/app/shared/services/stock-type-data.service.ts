import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class StockTypeDataService {

  constructor() { }

  private toQuantityDataStockTypeId = new Subject<number>();
  private toSeatListDisplayFlag = new Subject<boolean>();
  private toIsSearchFlag = new Subject<boolean>();

  // Observable streams
  public toQuantityData$ = this.toQuantityDataStockTypeId.asObservable();
  public toSeatListFlag$ = this.toSeatListDisplayFlag.asObservable();
  public toIsSearchFlag$ = this.toIsSearchFlag.asObservable();

  // Service message commands
  sendToQuantity(stockTypeId: number) {
    this.toQuantityDataStockTypeId.next(stockTypeId);
  }

  sendToSeatListFlag(flag: boolean) {
    this.toSeatListDisplayFlag.next(flag);
  }

  sendToIsSearchFlag(flag: boolean) {
     this.toIsSearchFlag.next(flag);
   }
}