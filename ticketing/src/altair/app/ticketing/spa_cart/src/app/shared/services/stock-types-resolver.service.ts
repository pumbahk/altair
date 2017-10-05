import { Injectable } from '@angular/core';
import { Router, Resolve, ActivatedRouteSnapshot } from '@angular/router';
import { Observable } from 'rxjs/Rx';
import { StockTypesService } from '../services/stock-types.service';
import { IErrorResponse, IStockTypesResponse}  from '../services/interfaces';
//logger
import { Logger } from "angular2-logger/core";

@Injectable()
/**
 * Stock Types Resolver
 */
export class StockTypesResolver implements Resolve<any> {
  constructor(
    private performanceService: StockTypesService
    , private router: Router
    , private _logger: Logger
  ) {}

  /**
   * Resolve stock types by performance id in url params
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
    let findStockTypesByPerformanceId: Observable<IStockTypesResponse | IErrorResponse> = this.performanceService.findStockTypesByPerformanceId(performanceId);

    findStockTypesByPerformanceId.subscribe((response: IStockTypesResponse) => {
      this._logger.debug(`StockTypes(performance id:${performanceId}) has been fetched.`, response);
    },
    (error: IErrorResponse) => {
      let message = "Error: StockTypes(performance_id:${performanceId}) could not fetched.";
      this._logger.error(message + error);
      return Observable.throw(message);
    });

    return findStockTypesByPerformanceId;
  }
}