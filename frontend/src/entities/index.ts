/**
 * Auto-generated entity types
 * Contains all CMS collection interfaces in a single file 
 */

/**
 * Collection ID: contactinquiries
 * Interface for ContactInquiries
 */
export interface ContactInquiries {
  _id: string;
  _createdDate?: Date;
  _updatedDate?: Date;
  /** @wixFieldType text */
  userName?: string;
  /** @wixFieldType text */
  emailAddress?: string;
  /** @wixFieldType text */
  subject?: string;
  /** @wixFieldType text */
  messageContent?: string;
  /** @wixFieldType datetime */
  submissionDate?: Date | string;
  /** @wixFieldType text */
  status?: string;
}


/**
 * Collection ID: learningresources
 * Interface for LearningResources
 */
export interface LearningResources {
  _id: string;
  _createdDate?: Date;
  _updatedDate?: Date;
  /** @wixFieldType text */
  resourceTitle?: string;
  /** @wixFieldType text */
  description?: string;
  /** @wixFieldType text */
  contentBody?: string;
  /** @wixFieldType url */
  videoUrl?: string;
  /** @wixFieldType text */
  resourceType?: string;
  /** @wixFieldType image - Contains image URL, render with <Image> component, NOT as text */
  thumbnailImage?: string;
  /** @wixFieldType text */
  tags?: string;
}


/**
 * Collection ID: practicesessions
 * Interface for PracticeSessions
 */
export interface PracticeSessions {
  _id: string;
  _createdDate?: Date;
  _updatedDate?: Date;
  /** @wixFieldType datetime */
  sessionDateTime?: Date | string;
  /** @wixFieldType url */
  recordingUrl?: string;
  /** @wixFieldType number */
  overallReadinessScore?: number;
  /** @wixFieldType text */
  verbalAnalysisSummary?: string;
  /** @wixFieldType text */
  nonVerbalAnalysisSummary?: string;
  /** @wixFieldType text */
  feedbackSummary?: string;
  /** @wixFieldType text */
  sessionType?: string;
}
