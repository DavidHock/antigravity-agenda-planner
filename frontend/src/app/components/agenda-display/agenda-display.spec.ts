import { of } from 'rxjs';
import { describe, beforeEach, expect, it, vi } from 'vitest';

import { AgendaDisplayComponent } from './agenda-display';
import { ApiService } from '../../services/api';

describe('AgendaDisplayComponent', () => {
  let component: AgendaDisplayComponent;
  let apiServiceMock: { createIcs: ReturnType<typeof vi.fn>; refineText: ReturnType<typeof vi.fn> };
  let clipboardSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    apiServiceMock = {
      createIcs: vi.fn().mockReturnValue(of(new Blob())),
      refineText: vi.fn().mockReturnValue(of({ refined_text: 'updated' }))
    };

    component = new AgendaDisplayComponent(apiServiceMock as unknown as ApiService);

    clipboardSpy = vi.fn();
    Object.assign(globalThis, {
      navigator: {
        clipboard: {
          writeText: clipboardSpy
        }
      }
    });
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

  it('passes the correct language instruction to the refine endpoint', () => {
    component.language = 'EN';
    component.dayEditableContent = ['Original'];

    component.refineDay(0);

    expect(apiServiceMock.refineText).toHaveBeenCalledWith(
      'Original',
      'Ensure the entire text stays in English.'
    );
  });

  it('copies formatted agenda text to the clipboard', () => {
    component.parsedAgenda = {
      title: 'Daily Sync',
      summary: 'Status updates',
      items: [
        { title: 'Intro', description: 'Hello' }
      ]
    };
    component.dayEditableContent = ['test'];

    component.copyToClipboard();

    expect(clipboardSpy).toHaveBeenCalled();
  });

  it('downloads the full agenda using edited content', () => {
    component.dayEditableContent = ['Edited content'];
    component.agendaContent = '{"title":"x"}';
    component.topic = 'Topic';
    component.startTime = '2024-05-01T09:00:00';
    component.endTime = '2024-05-01T10:00:00';
    component.location = 'Room';

    component.downloadIcs();

    expect(apiServiceMock.createIcs).toHaveBeenCalledWith(
      'Topic',
      '2024-05-01T09:00:00',
      '2024-05-01T10:00:00',
      'Room',
      'Edited content'
    );
  });

  it('downloads a single day ICS with edited text', () => {
    component.parsedAgenda = {
      title: 'Multi',
      summary: '',
      days: [
        { date: '2024-05-01', start_time: '09:00', end_time: '17:00', items: [] }
      ]
    };
    component.dayEditableContent = ['Day content'];
    component.topic = 'Conference';
    component.location = 'Berlin';

    component.downloadDayIcs(0);

    expect(apiServiceMock.createIcs).toHaveBeenCalledWith(
      'Conference (Day 1)',
      '2024-05-01T09:00:00',
      '2024-05-01T17:00:00',
      'Berlin',
      'Day content'
    );
  });
});
