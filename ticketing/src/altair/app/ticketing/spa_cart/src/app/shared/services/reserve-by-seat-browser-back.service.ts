import { Injectable } from '@angular/core';
import { CanDeactivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable,Subject } from 'rxjs';
import { ReserveBySeatComponent } from '../../reserve-by-seat/reserve-by-seat.component';

@Injectable()
export class ReserveBySeatBrowserBackService implements CanDeactivate<ReserveBySeatComponent> {
  constructor(
    private router: Router
    ) {
  }

  public deactivate: boolean = true;
  public modal = new Subject<any>();
  //IE、iOS+chrome用商品選択遷移回数
  public selectProductCount: number = 0;

  canDeactivate(
    component: ReserveBySeatComponent,
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean>|Promise<boolean>|boolean {
    if (this.deactivate) {
      return true;
    } else {
      this.modal.next();
      //iOS+chromeの場合進む、それ以外の場合履歴を追加
      if (navigator.userAgent.match(/crios/i)) {
        history.forward();
      } else {
        let destinationLink = window.location.href;
        setTimeout(() => {
            window.history.replaceState({}, '', destinationLink);
            window.history.pushState({}, '', this.router.url);
        });
      }
      return false;
    }
  }
}
