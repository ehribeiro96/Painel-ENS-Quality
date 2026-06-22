export type ChatAttachmentCategory = "text" | "image" | "binary";

export type ChatAttachmentDraft = {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  category: ChatAttachmentCategory;
  preview: string | null;
  note: string;
};
