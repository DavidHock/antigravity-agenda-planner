import { Routes } from '@angular/router';
import { AgendaFormComponent } from './components/agenda-form/agenda-form';

export const routes: Routes = [
    { path: '', component: AgendaFormComponent },
    { path: '**', redirectTo: '' }
];
