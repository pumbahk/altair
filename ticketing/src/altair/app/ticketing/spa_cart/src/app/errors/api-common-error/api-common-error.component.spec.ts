import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ApiCommonErrorComponent } from './api-common-error.component';

describe('ApiCommonErrorComponent', () => {
  let component: ApiCommonErrorComponent;
  let fixture: ComponentFixture<ApiCommonErrorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ApiCommonErrorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ApiCommonErrorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
