import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';

interface AgendaItem {
  time_slot: string;
  title: string;
  description: string;
  duration: string;
}

interface AgendaData {
  title: string;
  summary: string;
  items: AgendaItem[];
}

@Component({
  selector: 'app-agenda-display',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatListModule, MatDividerModule],
  templateUrl: './agenda-display.html',
  styleUrls: ['./agenda-display.scss']
})
export class AgendaDisplayComponent implements OnChanges {
  @Input() agendaContent: string = '';
  parsedAgenda: AgendaData | null = null;
  rawContent: string = '';

  ngOnChanges(changes: SimpleChanges) {
    if (changes['agendaContent'] && this.agendaContent) {
      try {
        this.parsedAgenda = JSON.parse(this.agendaContent);
        this.rawContent = '';
      } catch (e) {
        console.warn('Could not parse agenda as JSON, falling back to raw text');
        this.parsedAgenda = null;
        this.rawContent = this.agendaContent;
      }
    }
  }

  copyToClipboard() {
    navigator.clipboard.writeText(this.agendaContent);
  }
}
