import { Component, OnInit, NgModule } from '@angular/core';
//router
import { ActivatedRoute, Router } from '@angular/router';
//service
import { PerformancesService } from '../../shared/services/performances.service';
import { ErrorModalDataService } from '../../shared/services/error-modal-data.service';
import { AppConstService } from '../../app.constants';
//interface
import { IPerformance, IPerformanceInfoResponse } from '../../shared/services/interfaces';
//logger
import { Logger } from "angular2-logger/core";
// constants
import { ApiConst } from '../../app.constants';

@Component({
  providers: [AppConstService],
  selector: 'app-event-info',
  templateUrl: './event-info.component.html',
  styleUrls: ['./event-info.component.css']
})
@NgModule({
  imports: [
  ],
  declarations: [
    Component
  ],
  bootstrap: [Component]
})


export class EventinfoComponent implements OnInit {

  //公演情報
  performance: IPerformance;
  //公演名
  performanceName = null;
  //会場名
  venueName = null;
  //公演id
  performanceId: number;
  //試合開始時間
  startOnTime: any;
  isDateObtained: boolean = false;
  //年
  year: any;
  //月
  month: any;
  //日
  day: any;


  /**
   * コンストラクタ
   */
  constructor(private route: ActivatedRoute,
    private router: Router,
    private performancesService: PerformancesService,
    private errorModalDataService: ErrorModalDataService,
    private AppConstService: AppConstService,
    private _logger: Logger) {
  }

  /**
   * 初期化処理
   */
  ngOnInit() {
    this.route.params.subscribe((params) => {
      if (params && params['performance_id']) {
        //パラメーター切り出し
        this.performanceId = +params['performance_id'];
        this.performancesService.getPerformance(this.performanceId).subscribe((response: IPerformanceInfoResponse) => {
          this._logger.debug(`get Performance(#${this.performanceId}) success`, response);
          this.performance = response.data.performance;
          this.performanceName = this.performance.performance_name;
          this.venueName = this.performance.venue_name;

          let startOn = new Date(this.performance.start_on + '+09:00');
          this.startOnTime = startOn.getHours() + '時';
          if (startOn.getMinutes() != 0) {
            this.startOnTime += startOn.getMinutes() + '分';
          }
          this.year = startOn.getFullYear();
          this.month = startOn.getMonth() + 1;
          this.day = startOn.getDate();
          this.isDateObtained = true;
        },
          (error) => {
            this._logger.error('get Performance(#${this.performanceId}) error', error);
          });
      }
    });


  }

  onClick() {
    location.href = `${AppConstService.PAGE_URL.TOP}`;
  }
}
