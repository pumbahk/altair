import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RoadAnimationComponent } from './road-animation.component';

describe('RoadAnimationComponent', () => {
  let component: RoadAnimationComponent;
  let fixture: ComponentFixture<RoadAnimationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RoadAnimationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RoadAnimationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});