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
    if ((navigator.userAgent.indexOf('iPad') > 0 || navigator.userAgent.indexOf('Macintosh') > 0) && 'ontouchend' in document) {
      return true;
    }
    return false;
  }
  /**
* スマホサイズのtablet(Android)かチェックを行います
* ※768px以下はタブレットでもスマホ表示
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
  /**
* PCサイズのtablet(Android)かチェックを行います
* ※769px以上はタブレットでもスマホ表示
* @return {boolean} PC表示タブレット/true,タブレットではない/false
*/
  isTabletPC() {
    const WINDOW_SM = 768;
    var windowWidth = window.outerWidth;
    if (navigator.userAgent.indexOf('Android') > 0 && navigator.userAgent.indexOf('Mobile') < 0) {
      if (windowWidth > WINDOW_SM) {
        return true;
      }
      return false;
    }
  }
  /**
* PCかチェックを行います
* @return {boolean} PC/true,PC以外/false
*/
  isPC() {
    if (!this.isSmartPhone() && !this.isIpad() && !this.isTabletSP() && !this.isTabletPC()) {
      return true;
    }
    return false;
  }
}