import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class CountSelectService {

  constructor() { }

  private toQuantityCountSelect = new Subject<number>();

  // Observable streams
  public toQuantityData$= this.toQuantityCountSelect.asObservable();

  // Service message commands
  sendToQuantity(countSelect: number) {
    this.toQuantityCountSelect.next(countSelect);
  }
}