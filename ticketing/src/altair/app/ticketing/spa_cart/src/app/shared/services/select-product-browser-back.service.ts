import { Injectable } from '@angular/core';
import { CanDeactivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs/Observable';
import { SelectProductComponent } from '../../select-product/select-product.component';

@Injectable()
export class SelectProductBrowserBackService implements CanDeactivate<SelectProductComponent> {
  constructor(
    private router: Router,
    ) {
  }
  canDeactivate(
    component: SelectProductComponent,
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean>|Promise<boolean>|boolean {
    if (component.deactivate) {
      return true;
    } else {
      component.confirmReturn();
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
