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
}