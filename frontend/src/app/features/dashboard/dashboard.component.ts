import { ChangeDetectionStrategy, Component, inject, OnInit } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';
import { GamificationService } from '../../core/services/gamification.service';

interface NavigationItem {
  path: string;
  icon: string;
  label: string;
  description: string;
  tone: string;
}

@Component({
  selector: 'app-dashboard',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent implements OnInit {
  protected readonly auth = inject(AuthService);
  protected readonly gamification = inject(GamificationService);
  private readonly router = inject(Router);

  protected readonly modules: NavigationItem[] = [
    {
      path: '/activities',
      icon: '▣',
      label: 'Actividades',
      description: 'Ver actividades asignadas y completar tareas',
      tone: 'activities',
    },
    {
      path: '/courses',
      icon: '▤',
      label: 'Cursos',
      description: 'Explorar y gestionar los cursos disponibles',
      tone: 'courses',
    },
    {
      path: '/simulations',
      icon: '♜',
      label: 'Simulaciones',
      description: 'Acceder a simulaciones interactivas externas',
      tone: 'simulations',
    },
    {
      path: '/library',
      icon: '▥',
      label: 'Biblioteca',
      description: 'Recursos y material académico online',
      tone: 'library',
    },
    {
      path: '/blog',
      icon: '⌁',
      label: 'Blog',
      description: 'Publicar artículos y comentar publicaciones',
      tone: 'blog',
    },
    {
      path: '/contact',
      icon: 'ⓘ',
      label: 'Sobre nosotros',
      description: 'Información del sistema y contacto',
      tone: 'contact',
    },
    {
      path: '/reports',
      icon: '▥',
      label: '📊 Mi Reporte / Reportes',
      description: 'Estadísticas de progreso, medallas obtenidas y historial completo de actividades',
      tone: 'reports',
    },
  ];

  ngOnInit(): void {
    this.gamification.load().subscribe();
  }

  protected toggleContrast(): void {
    document.body.classList.toggle('high-contrast');
  }

  protected adjustFont(delta: number): void {
    const root = document.documentElement;
    const current = Number.parseFloat(getComputedStyle(root).fontSize) || 16;
    root.style.fontSize = `${Math.max(12, Math.min(20, current + delta))}px`;
  }

  protected logout(): void {
    this.auth.logout().subscribe(() => void this.router.navigate(['/auth']));
  }
}
