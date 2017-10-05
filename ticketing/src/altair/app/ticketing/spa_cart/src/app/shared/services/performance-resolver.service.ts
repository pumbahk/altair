import { Injectable } from '@angular/core';
import { Router, Resolve, ActivatedRouteSnapshot } from '@angular/router';
import { Observable } from 'rxjs/Rx';
import { PerformancesService } from '../services/performances.service';
import { IErrorResponse, IPerformanceInfoResponse}  from '../services/interfaces';
//logger
import { Logger } from "angular2-logger/core";

@Injectable()
/**
 * Performance Resolver
 */
export class PerformanceResolver implements Resolve<any> {
  constructor(
    private performanceService: PerformancesService
    , private router: Router
    , private _logger: Logger
  ) {}

  /**
   * Resolve the performance by performance id in url param
   * @param  {ActivatedRouteSnapshot} route
   * @return {Observable<IPerformanceInfoResponse | IErrorResponse>} response
   */
  resolve(route: ActivatedRouteSnapshot): Observable<IPerformanceInfoResponse | IErrorResponse> {
    if(!route.params || !route.params['performance_id']){
      let message = "Error: performance_id not exists in url";
      this._logger.error(message);
      return Observable.throw(message);
    }

    let id = route.params['performance_id'];
    let getPerformance: Observable<IPerformanceInfoResponse | IErrorResponse> = this.performanceService.getPerformance(id);

    getPerformance.subscribe((response: IPerformanceInfoResponse) => {
      this._logger.debug(`Performance#${id} has been fetched.`, response);
    },
    (error: IErrorResponse) => {
      let message = "Error: Performance#${id} could not fetched.";
      this._logger.error(message + error);
      this.router.navigate(['/performances/'+id+'']);
      return Observable.throw(message);
    });

    return getPerformance;
  }
}