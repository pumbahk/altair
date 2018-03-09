import { Injectable } from '@angular/core';

@Injectable()
export class SmartPhoneCheckService {

  /**
 * iphone,ipod,androidかチェックを行います
 *
 * @return {boolean}
 */
  isSmartPhone() {
    if (navigator.userAgent.indexOf('iPhone') > 0 || navigator.userAgent.indexOf('iPod') > 0 || (navigator.userAgent.indexOf('Android') > 0 && navigator.userAgent.indexOf('Mobile') > 0)) {
      return true;
    }
    return false;
  }

  /**
* ipadかチェックを行います
*
* @return {boolean}
*/
  isIpad() {
    if (navigator.userAgent.indexOf('iPad') > 0) {
      return true;
    }
    return false;
  }
  /**
* スマホサイズのtablet(Android)かチェックを行います
* ※769px以下はタブレットでもスマホ表示
* @return {boolean} スマホ表示タブレット/true,タブレットではない/false
*/
  isTabletSP() {
    const WINDOW_SM = 768;
    var windowWidth = window.outerWidth;
    if (navigator.userAgent.indexOf('Android') > 0 && navigator.userAgent.indexOf('Mobile') < 0) {
      if (windowWidth <= WINDOW_SM) {
        return true;
      }
    return false;
  }
}