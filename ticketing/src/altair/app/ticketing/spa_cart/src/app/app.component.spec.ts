/* tslint:disable:no-unused-variable */

import { TestBed, async } from '@angular/core/testing';
import { MockComponent } from 'ng2-mock-component';
import { AppComponent } from './app.component';

describe('AppComponent', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        AppComponent,
        MockComponent({ selector: 'app-header' }),
        MockComponent({ selector: 'router-outlet' })
      ]
    });
    TestBed.compileComponents();
  });

  it('should create the app', async(() => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  }));
});
