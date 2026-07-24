import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';

import { PostSummary } from '../../core/models/api.models';
import { ApiErrorService } from '../../core/services/api-error.service';
import { GamificationService } from '../../core/services/gamification.service';
import { ToastService } from '../../core/services/toast.service';
import { BlogService } from './blog.service';

@Component({
  selector: 'app-blog',
  imports: [ReactiveFormsModule, FormsModule, DatePipe],
  templateUrl: './blog.component.html',
  styleUrl: './blog.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BlogComponent implements OnInit {
  private readonly api = inject(BlogService);
  private readonly fb = inject(FormBuilder);
  private readonly errors = inject(ApiErrorService);
  private readonly toast = inject(ToastService);
  private readonly gamification = inject(GamificationService);

  protected readonly posts = signal<PostSummary[]>([]);
  protected readonly comments: Record<string, string> = {};
  protected readonly form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.minLength(2)]],
    content: ['', [Validators.required, Validators.minLength(2)]],
  });

  ngOnInit(): void {
    this.load();
  }

  protected load(): void {
    this.api.list().subscribe({
      next: (posts) => this.posts.set(posts),
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected create(): void {
    if (this.form.invalid) {
      return;
    }
    const data = this.form.getRawValue();
    this.api.create(data.title, data.content).subscribe({
      next: () => {
        this.form.reset();
        this.load();
        this.gamification.load().subscribe();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }

  protected comment(postId: string): void {
    const content = this.comments[postId]?.trim();
    if (!content) {
      return;
    }
    this.api.comment(postId, content).subscribe({
      next: () => {
        this.comments[postId] = '';
        this.load();
      },
      error: (error) => this.toast.show(this.errors.message(error)),
    });
  }
}
