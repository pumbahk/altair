/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { SeatlistComponent } from './seat-list.component';

describe('SeatlistComponent', () => {
  let component: SeatlistComponent;
  let fixture: ComponentFixture<SeatlistComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SeatlistComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SeatlistComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
