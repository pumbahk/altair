import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class CountSelectService {

  constructor() { }

  private toQuentityCountSelect = new Subject<number>();

  // Observable streams
  public toQuentityData$= this.toQuentityCountSelect.asObservable();

  // Service message commands
  sendToQuentity(countSelect: number) {
    this.toQuentityCountSelect.next(countSelect);
  }
}