import { Component, OnInit, NgModule } from '@angular/core';
//router
import { ActivatedRoute, Router } from '@angular/router';
//service
import { PerformancesService } from '../../shared/services/performances.service';
import { AppConstService } from '../../app.constants';
//interface
import { IPerformance, IPerformanceInfoResponse } from '../../shared/services/interfaces';

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
   bootstrap: [ Component ]
 })


export class EventinfoComponent implements OnInit {

  //公演情報
  performance: IPerformance;
  startOnTime: any;
  year: any;
  month: any;
  day: any;
  
  /**
   * コンストラクタ
   */
  constructor(private route: ActivatedRoute,
              private router: Router,
              private AppConstService:AppConstService) {
  }

  /**
   * 初期化処理
   */
  ngOnInit() {
    let response: IPerformanceInfoResponse = this.route.snapshot.data['performance'];
    this.performance = response.data.performance;
    let startOn = new Date(this.performance.start_on + '+09:00');
    this.startOnTime = startOn.getHours() + '時';
    if (startOn.getMinutes() != 0) {
      this.startOnTime += startOn.getMinutes() + '分';
    }
    this.year = startOn.getFullYear();
    this.month = startOn.getMonth() + 1;
    this.day = startOn.getDate();
  }

  onClick(){
    location.href = `${AppConstService.PAGE_URL.TOP}`;
  }
}
