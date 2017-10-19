import { Injectable } from '@angular/core';
import { Subject } from 'rxjs/Subject';

@Injectable()
export class AnimationEnableService {

  constructor() { }
  private roadingFlag = new Subject<boolean>();

  public toRoadingFlag$= this.roadingFlag.asObservable();

  sendToRoadFlag(roadBool: boolean) {
    this.roadingFlag.next(roadBool);
  }
}