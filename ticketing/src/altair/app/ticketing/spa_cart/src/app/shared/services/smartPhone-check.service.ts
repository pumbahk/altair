import { Injectable } from '@angular/core';

@Injectable()
export class SmartPhoneCheckService {

    /**
   * iphone,ipod,androidかチェックを行います
   *
   * @return {boolean}
   */
    isSmartPhone() {
        if (navigator.userAgent.indexOf('iPhone') > 0 || navigator.userAgent.indexOf('iPod') > 0 || navigator.userAgent.indexOf('Android') > 0) {
            return true;
        }
        return false;
    }
}