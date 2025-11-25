import { FormBuilder } from '@angular/forms';
import { describe, beforeEach, expect, it } from 'vitest';

import { AgendaFormComponent } from './agenda-form';
import { ApiService } from '../../services/api';

describe('AgendaFormComponent', () => {
  let component: AgendaFormComponent;

  beforeEach(() => {
    component = new AgendaFormComponent(new FormBuilder(), {} as ApiService);
  });

  it('combines date and time inputs into a Date object', () => {
    const date = new Date('2024-05-01T00:00:00');
    const result = component.combineDateAndTime(date, '10:30');

    expect(result.getHours()).toBe(10);
    expect(result.getMinutes()).toBe(30);
  });

  it('converts dates into local ISO strings without timezone suffix', () => {
    const date = new Date('2024-05-01T10:30:00');
    const localIso = component.toLocalISOString(date);

    expect(localIso).toMatch(/2024-05-01T10:30:00/);
    expect(localIso.endsWith('Z')).toBeFalsy();
  });
});
