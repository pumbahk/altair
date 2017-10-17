/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { VenuemapComponent } from './venue-map.component';

describe('VenuemapComponent', () => {
  let component: VenuemapComponent;
  let fixture: ComponentFixture<VenuemapComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VenuemapComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VenuemapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
