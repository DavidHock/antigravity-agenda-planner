import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgendaDisplay } from './agenda-display';

describe('AgendaDisplay', () => {
  let component: AgendaDisplay;
  let fixture: ComponentFixture<AgendaDisplay>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgendaDisplay]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AgendaDisplay);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
