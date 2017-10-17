/* tslint:disable:no-unused-variable */

import { TestBed, async, inject } from '@angular/core/testing';
import { ApiBase } from './api-base.service';

describe('ApiBase', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ApiBase]
    });
  });

  it('should ...', inject([ApiBase], (service: ApiBase) => {
    expect(service).toBeTruthy();
  }));
});