import { Injectable } from '@angular/core';
import { AppConstService } from '../../app.constants';

@Injectable()
export class I18nService {

  constructor() { }

  public get locale() {
      return document.getElementById('locale').getAttribute('value');
  }

  public get isJpn() {
      return document.getElementById('locale').getAttribute('value') == AppConstService.LOCALE.JAPANESE;
  }

  public static LOCALES_AVAILABLE = [
      AppConstService.LOCALE.JAPANESE,
      AppConstService.LOCALE.ENGLISH,
  ];

  public get i18n() {
      return Boolean(document.getElementById('i18n').getAttribute('value'));
  }

  public get localeOptions() {
      return [
          {
              value: AppConstService.LOCALE.ENGLISH,
              label: 'English'
          },{
              value: AppConstService.LOCALE.JAPANESE,
              label: '日本語'
          }
      ];
  }

  selectLocale(locale: string): void {
    if (locale != this.locale) {
      window.location.href = '/locale?language=' + locale;
    }
  }
}