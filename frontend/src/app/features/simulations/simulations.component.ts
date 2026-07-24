import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-simulations',
  templateUrl: './simulations.component.html',
  styleUrl: './simulations.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SimulationsComponent {}
