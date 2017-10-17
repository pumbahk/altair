import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { MockComponent } from 'ng2-mock-component';

import { ReserveBySeatComponent } from './reserve-by-seat.component';

describe('ReserveBySeatComponent', () => {
  let component: ReserveBySeatComponent;
  let fixture: ComponentFixture<ReserveBySeatComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ 
        ReserveBySeatComponent,
        MockComponent({ selector: 'app-eventinfo' }),
        MockComponent({ selector: 'app-filter' }),
        MockComponent({ selector: 'app-venuemap' }),
        MockComponent({ selector: 'app-seatlist' }),
        ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReserveBySeatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
