import { of } from 'rxjs';
import { describe, beforeEach, expect, it, vi } from 'vitest';

import { AgendaDisplayComponent } from './agenda-display';
import { ApiService } from '../../services/api';

describe('AgendaDisplayComponent', () => {
  let component: AgendaDisplayComponent;

  beforeEach(() => {
    const apiServiceMock = {
      createIcs: vi.fn().mockReturnValue(of(new Blob()))
    } as unknown as ApiService;

    component = new AgendaDisplayComponent(apiServiceMock);
  });

  it('initializes editable content for single day agendas', () => {
    component.parsedAgenda = {
      title: 'Test',
      summary: 'Summary',
      items: [
        {
          title: 'Coffee Break',
          description: 'Grab a drink',
          time_slot: '10:00 - 10:15',
          duration: '15 mins'
        }
      ]
    };

    component.initializeEditableContent();

    expect(component.dayEditableContent.length).toBe(1);
    expect(component.dayEditableContent[0]).toContain('☕ COFFEE BREAK');
  });

  it('uses dinner emoji for social events', () => {
    const icon = component.getIconForTitle('Dinner and Drinks');
    expect(icon).toBe('🍻');
  });
});
