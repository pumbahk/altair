import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReserveByQuantityComponent } from './reserve-by-quantity.component';

describe(' ReserveByQuantityComponent', () => {
  let component:  ReserveByQuantityComponent;
  let fixture: ComponentFixture< ReserveByQuantityComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [  ReserveByQuantityComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent( ReserveByQuantityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
