import { FormBuilder } from '@angular/forms';
import { describe, beforeEach, expect, it, vi } from 'vitest';

import { AgendaFormComponent } from './agenda-form';
import { ApiService } from '../../services/api';

describe('AgendaFormComponent', () => {
  let component: AgendaFormComponent;
  let apiServiceMock: { generateAgenda: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    apiServiceMock = {
      generateAgenda: vi.fn().mockReturnValue({
        subscribe: vi.fn().mockImplementation(({ next }) => next({ agenda: '{}' }))
      })
    };
    component = new AgendaFormComponent(new FormBuilder(), apiServiceMock as unknown as ApiService);
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

  it('invokes the API when submitting a valid form', () => {
    component.agendaForm.patchValue({
      topic: 'Sync',
      location: 'Room',
      language: 'EN',
      emailContent: '',
      startDate: new Date('2024-05-01T09:00:00'),
      endDate: new Date('2024-05-01T10:00:00')
    });

    component.onSubmit();

    expect(apiServiceMock.generateAgenda).toHaveBeenCalled();
  });

  it('skips API call when form is invalid', () => {
    component.agendaForm.patchValue({
      topic: '',
      location: '',
      language: 'EN'
    });

    component.onSubmit();

    expect(apiServiceMock.generateAgenda).not.toHaveBeenCalled();
  });

  it('removes files from the selection list', () => {
    const file = new File(['content'], 'notes.txt');
    component.selectedFiles = [file];

    component.removeFile(0);

    expect(component.selectedFiles.length).toBe(0);
  });
});
