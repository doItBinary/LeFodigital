// Project rules and architecture: ../../../AGENTS.md and ../../../CONTEXT.md
import { Routes } from '@angular/router';

import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  {
    path: 'auth',
    loadComponent: () =>
      import('./features/auth/auth.component').then((module) => module.AuthComponent),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then(
        (module) => module.DashboardComponent,
      ),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'activities' },
      {
        path: 'activities',
        loadComponent: () =>
          import('./features/activities/activities.component').then(
            (module) => module.ActivitiesComponent,
          ),
      },
      {
        path: 'courses',
        loadComponent: () =>
          import('./features/courses/courses.component').then(
            (module) => module.CoursesComponent,
          ),
      },
      {
        path: 'simulations',
        loadComponent: () =>
          import('./features/simulations/simulations.component').then(
            (module) => module.SimulationsComponent,
          ),
      },
      {
        path: 'library',
        loadComponent: () =>
          import('./features/library/library.component').then(
            (module) => module.LibraryComponent,
          ),
      },
      {
        path: 'blog',
        loadComponent: () =>
          import('./features/blog/blog.component').then((module) => module.BlogComponent),
      },
      {
        path: 'reports',
        loadComponent: () =>
          import('./features/reports/reports.component').then(
            (module) => module.ReportsComponent,
          ),
      },
      {
        path: 'profile',
        loadComponent: () =>
          import('./features/profile/profile.component').then(
            (module) => module.ProfileComponent,
          ),
      },
      {
        path: 'contact',
        loadComponent: () =>
          import('./features/contact/contact.component').then(
            (module) => module.ContactComponent,
          ),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
