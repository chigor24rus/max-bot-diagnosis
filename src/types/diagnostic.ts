export type DriveType = 'fwd' | 'rwd' | 'awd' | null;

export interface Question {
  id: string;
  text: string;
  type: 'choice' | 'multiselect' | 'text' | 'photo';
  options?: string[];
  allowText?: boolean;
  allowPhoto?: boolean;
  conditional?: {
    dependsOn: string;
    value: string | string[];
  };
}

export interface Section {
  id: string;
  title: string;
  questions: Question[];
  conditional?: {
    dependsOn: string;
    value: string | string[];
  };
}

export interface DiagnosticAnswer {
  questionId: string;
  value: string | string[] | null;
  textComment?: string;
  photos?: string[];
}

export interface DiagnosticData {
  mechanicId?: number;
  mechanicName: string;
  carNumber: string;
  mileage: number;
  diagnosticType: string;
  driveType?: DriveType;
  answers: DiagnosticAnswer[];
  currentSection: string;
  completedSections: string[];
}