import { Component, OnInit , Input, EventEmitter} from '@angular/core';
//service
import { ErrorModalDataService } from '../../shared/services/error-modal-data.service';
import { AnimationEnableService } from '../../shared/services/animation-enable.service';


@Component({
  selector: 'app-api-common-error',
  templateUrl: './api-common-error.component.html',
  styleUrls: ['./api-common-error.component.css']
})
export class ApiCommonErrorComponent {

  constructor(private errorModalDataService: ErrorModalDataService,
              private animationEnableService: AnimationEnableService) {
  }

  errorDisplay: boolean;
  errorTitleDict: {msg: string, param: string};
  errorDetailDict: {msg: string, param: string};
  onClosed: () => void;

  ngOnInit() {
    this.errorModalDataService.errorTitle$.subscribe(
      errorTitleDict => {
        this.errorTitleDict = errorTitleDict;
        this.errorDisplay = true;
      });
    this.errorModalDataService.errorDetail$.subscribe(
      errorDetailDict => {
        this.errorDetailDict = errorDetailDict;
        this.errorDisplay = true;
      });
    this.errorModalDataService.onClosed$.subscribe(
      onClosed => {
        this.onClosed = onClosed;
      });
  }
  display() {
    this.errorDisplay = false;
    this.animationEnableService.sendToRoadFlag(false);
    this.onClosed && this.onClosed();
  }
}
