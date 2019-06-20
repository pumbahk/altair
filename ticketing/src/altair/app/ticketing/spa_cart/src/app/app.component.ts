import { Component, ElementRef, OnInit } from '@angular/core';
//router
import {
    Router,
    // import as RouterEvent to avoid confusion with the DOM Event
    Event as RouterEvent,
    NavigationStart,
    NavigationEnd,
    NavigationCancel,
    NavigationError
} from '@angular/router';
//Ng2-loading-animate
import { LoadingAnimateService } from 'ng2-loading-animate';
//jquery
import * as $ from 'jquery';
//service
import { TranslateService } from "ng2-translate";
import { I18nService } from './shared/services/i18n-service'

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
  
export class AppComponent implements OnInit {

   public userAgent:any;

  /**
   * constructor
   * @param {Router}                private router Router
   * @param {LoadingAnimateService} private loadingService loading animation service
   * @param {TranslateService} private translateService translate service
   * @param {I18nService} private i18nService i18n service
   */
  constructor(private router: Router,
              private loadingService: LoadingAnimateService,
              private translateService: TranslateService,
              private i18nService: I18nService) {
    // ブラウザのUAを小文字で取得
    this.userAgent = window.navigator.userAgent.toLowerCase();
 
    // 一般的なブラウザ判定
      router.events.subscribe((event: RouterEvent) => {
        this.navigationInterceptor(event);
      });
  }

  ngOnInit(): void {
    this.translateService.addLangs(I18nService.LOCALES_AVAILABLE);
    this.translateService.setDefaultLang(this.i18nService.locale);

    //nothing to do
    if( this.userAgent.indexOf('chrome') != -1 ){
      var bodyStyle;

      document.getElementsByTagName('html')[0].style.height='100%';
      document.getElementsByTagName('html')[0].style.overflowY = 'hidden';

      bodyStyle = document.getElementsByTagName('body')[0].style; 
      bodyStyle.height = '100%';
      bodyStyle.overflowY = 'auto';

    } else if (((this.userAgent.indexOf('msie') > -1) && (this.userAgent.indexOf('opera') == -1)) || (this.userAgent.indexOf('trident/7') > -1)) {
      //IE
      $('body').addClass('ie');
    }
  }

  // Shows and hides the loading spinner during RouterEvent changes
  navigationInterceptor(event: RouterEvent): void {
    if (event instanceof NavigationStart) {
      this.loadingService.setValue(true);
    }
    if (event instanceof NavigationEnd) {
      this.loadingService.setValue(false);
    }

    // Set loading state to false in both of the below events to hide the spinner in case a request fails
    if (event instanceof NavigationCancel) {
      this.loadingService.setValue(false);
    }
    if (event instanceof NavigationError) {
      this.loadingService.setValue(false);
    }
    if(undefined){
      this.loadingService.setValue(false);
    }
  }
  
}