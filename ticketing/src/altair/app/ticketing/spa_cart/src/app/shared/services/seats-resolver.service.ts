import { Injectable } from '@angular/core';
import { Resolve, ActivatedRouteSnapshot } from '@angular/router';
import { Observable } from 'rxjs/Rx';
import { SeatsService } from '../services/seats.service';
import { IErrorResponse, ISeatsResponse } from '../services/interfaces';
//logger
import { Logger } from "angular2-logger/core";


@Injectable()
/**
 * Seats Resolver
 */
export class SeatsResolver implements Resolve<any> {
  constructor(
    private performanceService: SeatsService,
    private _logger: Logger
  ) {}

  /**
   * Resolve seats by performance id in url params
   * @param  {ActivatedRouteSnapshot} route Current route
   * @return {Observable<any>}
   */
  resolve(route: ActivatedRouteSnapshot): Observable<any> {
    if(!route.params || !route.params['performance_id']){
      let message = "Error: performance_id not exists in url";
      this._logger.error(message);
      return Observable.throw(message);
    }

    let performanceId = route.params['performance_id'];
    let findSeatsByPerformanceId: Observable<ISeatsResponse | IErrorResponse> = this.performanceService.findSeatsByPerformanceId(performanceId);

    findSeatsByPerformanceId.subscribe((response: ISeatsResponse) => {
      this._logger.debug(`Seats(performance id:${performanceId}) has been fetched.`, response);
    },
    (error: IErrorResponse) => {
      let message = "Error: Seats(performance_id:${performanceId}) could not fetched.";
      this._logger.error(message, error);
      return Observable.throw(message);
    });

    return findSeatsByPerformanceId;
  }
}