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
  errorTitle: string;
  errorDetail: string;

  ngOnInit() {
    this.errorModalDataService.errorTitle$.subscribe(
      errorTitle => {
        this.errorTitle = errorTitle;
        this.errorDisplay = true;
      });
    this.errorModalDataService.errorDetail$.subscribe(
      errorDetail => {
        this.errorDetail = errorDetail;
        this.errorDisplay = true;
      });
  }
  display() {
    this.errorDisplay = false;
    this.animationEnableService.sendToRoadFlag(false);
  }
}
