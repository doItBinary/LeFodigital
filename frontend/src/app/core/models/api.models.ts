export type UserRole = 'teacher' | 'student';
export type ActivityStatus = 'draft' | 'published';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  institution: string;
  createdAt: string;
}

export interface AuthSession {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
  user: UserProfile;
}

export interface ApiError {
  code: string;
  message: string;
}

export interface PagedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface CourseSummary {
  id: string;
  name: string;
  description: string;
  ownerId: string;
  ownerName: string;
  createdAt: string;
}

export interface EvidenceMetadata {
  id: string;
  activityId: string;
  studentId: string;
  studentName: string;
  originalName: string;
  contentType: string;
  sizeBytes: number;
  uploadedAt: string;
}

export interface ActivitySummary {
  id: string;
  title: string;
  description: string;
  points: number;
  dueDate: string | null;
  status: ActivityStatus;
  courseId: string | null;
  courseName: string | null;
  authorName: string;
  createdAt: string;
  publishedAt: string | null;
  completed: boolean;
  completionCount: number;
  evidenceCount: number;
  myEvidence: EvidenceMetadata | null;
}

export interface MedalDefinition {
  key: string;
  icon: string;
  name: string;
  description: string;
}

export interface EarnedMedal extends MedalDefinition {
  awardedAt: string;
}

export interface GamificationProgress {
  points: number;
  level: number;
  completedActivities: number;
  medals: EarnedMedal[];
  pointsInLevel: number;
}

export interface CommentSummary {
  id: string;
  authorName: string;
  content: string;
  createdAt: string;
}

export interface PostSummary {
  id: string;
  title: string;
  content: string;
  authorName: string;
  createdAt: string;
  comments: CommentSummary[];
}

export interface StudentReport {
  studentId: string;
  name: string;
  email: string;
  institution: string;
  progress: GamificationProgress;
  totalPublishedActivities: number;
  completed: ActivitySummary[];
}

export interface TeacherStudentReport {
  studentId: string;
  name: string;
  email: string;
  institution: string;
  progress: GamificationProgress;
  totalPublishedActivities: number;
  progressPercent: number;
  evidenceCount: number;
}

export interface TeacherReport {
  students: TeacherStudentReport[];
  totalStudents: number;
  totalPublishedActivities: number;
  averagePoints: number;
  averageLevel: number;
  totalMedals: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
